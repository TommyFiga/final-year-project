package protocol

import (
	"encoding/base64"
	"errors"
	"os"
)

var (
	ErrDecodingChunk = errors.New("failed decoding chunk")
	ErrWritingToFile = errors.New("failed writing to file")
)

// DecodeChunks reads base64-encoded chunks from a channel and writes the decoded
// content to an already existing file. The channel is expectedto be closed by the
//  caller once all chunks have been sent, which signals the end of the transfer.
func DecodeChunks(file *os.File, encodedChunks <-chan string) error {
	for encodedChunk := range encodedChunks{
		decodedChunk, err := base64.StdEncoding.DecodeString(encodedChunk)
		if err != nil {
			return ErrDecodingChunk
		}

		_, err = file.Write(decodedChunk)
		if err != nil {
			return ErrWritingToFile
		}
	}

	return nil
}
