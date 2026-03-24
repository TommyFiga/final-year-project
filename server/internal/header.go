package internal

import (
	"fmt"
	"math"
)

// ChunkSize defines the maximum size in bytes of each content chunk.
const ChunkSize = 4096

const (
	StatusOk             = 200
	StatusInvalidRequest = 400
	StatusNotFound       = 404
	StatusServerError    = 500
)

// BuildHeader builds a header message from the given status, contentLen and chunks.
func BuildHeader(status int, contentLen int, chunks int) string {
	return fmt.Sprintf("s=%d;b=%d;c=%d", status, contentLen, chunks)
}

// calculateChunks returns the number of chunks required to send contentLen bytes, based on ChunkSize.
func calculateChunks(contentLen int) int {
	return int(math.Ceil(float64(contentLen) / ChunkSize))
}

// calculateEncodedSize returns the content size after applying base64 encoding.
func calculateEncodedSize(fileSize int64) int {
	return int(math.Ceil(float64(fileSize) / 3 * 4))
}
