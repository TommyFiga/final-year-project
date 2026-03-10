package internal

import "fmt"

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
