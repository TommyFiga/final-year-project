package internal

import "fmt"

const (
	StatusOk       = 200
	StatusNotFound = 404
)

// Header holds the status, content length and number of chunks of a response.
type Header struct {
	Status     int
	ContentLen int
	Chunks     int
}

// BuildHeader builds a Header from the given RequestArgs.
//
// If an error occurs, a Header is still returned with only Status set,
// and both ContentLen and Chunks defaulting to 0.
func BuildHeader(reqArgs *RequestArgs) (*Header, error) {
	contentLen, err := checkFile(reqArgs.Content)
	if err != nil {
		return &Header{
			Status: StatusNotFound,
		}, err
	}

	chunks := calculateChunks(contentLen)

	return &Header{
		Status:     StatusOk,
		ContentLen: int(contentLen),
		Chunks:     chunks,
	}, nil
}

// HeaderContent produces a string representation of a Header struct.
//
// Example: "s=200;b=67545;c=35"
func HeaderContent(header Header) string {
	return fmt.Sprintf("s=%d;b=%d;c=%d", header.Status, header.ContentLen, header.Chunks)
}
