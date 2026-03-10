package internal

import (
	"encoding/base64"
	"io"
	"os"
)

const RawChunkSize = 3072

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
