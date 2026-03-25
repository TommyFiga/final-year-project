package internal

import (
	"encoding/base64"
	"io"
	"os"
)

// RawChunkSize defines the size in bytes of each raw chunk before base64 encoding.
// 3072 bytes encodes to exactly 4096 base64 characters, matching Telegram's message limit.
const RawChunkSize = 3072

// StreamFile reads a file and emits its contents as base64-encoded chunks over a channel.
// It returns a read-only channel of base64 strings and a buffered error channel.
// The caller should drain the chunk channel before reading from the error channel.
func StreamFile(filepath string) (<-chan string, <-chan error) {
	chunkChan := make(chan string)
	errChan := make(chan error, 1)

	go func() {
		defer close(chunkChan)
		defer close(errChan)

		file, err := os.Open(filepath)
		if err != nil {
			errChan <- err
			return
		}
		defer file.Close()

		buffer := make([]byte, RawChunkSize)

		for {
			n, err := file.Read(buffer)

			if n > 0 {
				chunkChan <- base64.StdEncoding.EncodeToString(buffer[:n])
			}

			if err == io.EOF {
				return
			}

			if err != nil {
				errChan <- err
				return
			}
		}
	}()

	return chunkChan, errChan
}
