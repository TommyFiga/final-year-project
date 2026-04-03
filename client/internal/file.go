package internal

import (
	"fmt"
	"os"
	"path/filepath"
	"time"
)

// CreateFile creates a new file in the given download directory with a timestamp-based
// name and the given content type as the extension. The caller is responsible for
// closing the file once the transfer is complete.
func CreateFile(contentType, downloadDir string) (*os.File, error) {
	timestamp := time.Now().Format("20060102_150405")
	filename := fmt.Sprintf("%s.%s", timestamp, contentType)

	file, err := os.Create(filepath.Join(downloadDir, filename))
	if err != nil {
		return nil, err
	}

	return file, nil
}
