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

// BuildHeader constructs a protocol response header string from a ResolvedResource.
// It computes the base64 encoded size and chunk count internally.
//
// The header format is: s={status};b={totalBytes};c={chunks};ct={contentType}
func BuildHeader(r ResolvedResource) string {
	contentLen := int(math.Ceil(float64(r.RawSize) / 3 * 4))
	chunks := int(math.Ceil(float64(contentLen) / ChunkSize))
	return fmt.Sprintf("s=%d;b=%d;c=%d;ct=%s", r.Status, contentLen, chunks, r.ContentType)
}
