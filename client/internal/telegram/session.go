package telegram

import (
	"log"
	"os"
	"telegram-proxy-client/internal"
	"telegram-proxy-client/internal/protocol"
)

type SessionState int

const (
	StateAwaitingHeader SessionState = iota
	StateCollectingChunks
)

type Session struct {
	state          SessionState
	header         *protocol.Header
	file           *os.File
	chunksReceived int
	downloadDir    string
	signal         chan struct{}
}

func (s *Session) handleHeader(headerMsg string) {
	header, err := protocol.ParseHeader(headerMsg)
	if err != nil {
		log.Printf("ParsingHeader() failed: %v", err)
		s.reset()
		return
	}

	log.Printf("Header: %s", headerMsg)

	if header.Status >= 400 && header.Status < 600 {
		s.reset()
		return
	}

	file, err := internal.CreateFile(header.ContentType, s.downloadDir)
	if err != nil {
		log.Printf("CreateFile() failed: %v", err)
		s.reset()
		return
	}

	s.state = StateCollectingChunks
	s.header = header
	s.file = file
}

func (s *Session) handleChunk(chunkMsg string) {
	s.chunksReceived++

	err := protocol.DecodeChunk(s.file, chunkMsg)
	if err != nil {
		log.Printf("DecodeChunk failed: %v", err)
		s.reset()
		return
	}

	if s.chunksReceived == s.header.Chunks {
		log.Printf("File downloaded into %s", s.file.Name())
		s.reset()
		return
	}
}

func (s *Session) reset() {
	if s.file != nil {
		s.file.Close()
	}

	s.signal <- struct{}{}

	*s = Session{downloadDir: s.downloadDir, signal: s.signal}
}

func (s *Session) Wait() {
	<-s.signal
}

func NewSession(downloadDir string) *Session {
	return &Session{downloadDir: downloadDir, signal: make(chan struct{}, 1)}
}
