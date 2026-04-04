package protocol

import (
	"errors"
	"strconv"
	"strings"
)

var (
	ErrInvalidStatus     = errors.New("invalid status value")
	ErrInvalidChunks     = errors.New("invalid chunks value")
	ErrInvalidTotalBytes = errors.New("invalid totalBytes value")
	ErrMalformedHeader   = errors.New("malformed header format")
)

// Header represents a parsed protocol response header.
// The header format is: s={status};b={totalBytes};c={chunks};ct={contentType}\r\n{HTTPHeaders}
type Header struct {
	Status      int
	TotalBytes  int
	Chunks      int
	ContentType string
	HttpHeaders map[string]string
}

// ParseHeader parses a protocol response header string into a Header struct.
// HTTP headers are only present for remote resources and are optional.
func ParseHeader(headerMsg string) (*Header, error) {
	parts := strings.SplitN(headerMsg, "\n", 2)
	protocolLine := parts[0]

	header := &Header{
		HttpHeaders: make(map[string]string),
	}

	fields := strings.Split(protocolLine, ";")
	for _, field := range fields {
		kv := strings.SplitN(field, "=", 2)
		if len(kv) != 2 {
			return nil, ErrMalformedHeader
		}
		key, value := kv[0], kv[1]

		switch key {
		case "s":
			status, err := strconv.Atoi(value)
			if err != nil {
				return nil, ErrInvalidStatus
			}
			header.Status = status
		case "b":
			totalBytes, err := strconv.Atoi(value)
			if err != nil {
				return nil, ErrInvalidTotalBytes
			}
			header.TotalBytes = totalBytes
		case "c":
			chunks, err := strconv.Atoi(value)
			if err != nil {
				return nil, ErrInvalidChunks
			}
			header.Chunks = chunks
		case "ct":
			header.ContentType = value
		}
	}

	if len(parts) > 1 {
		httpHeaders := strings.Split(parts[1], "\r\n")
		for _, httpHeader := range httpHeaders {
			kv := strings.SplitN(httpHeader, ":", 2)
			if len(kv) != 2 {
				continue
			}
			header.HttpHeaders[kv[0]] = kv[1]
		}
	}

	return header, nil
}
