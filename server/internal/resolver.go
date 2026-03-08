package internal

import (
	"errors"
	"math"
	"os"
	"path/filepath"
	"strings"
)

// ChunkSize defines the maaximum size in bytes of each content chunk.
const ChunkSize int16 = 4096

var (
	ErrInvalidFilename = errors.New("invalid filename")
	ErrFileNotFound    = errors.New("file not found")
)

// storageDir is the root directory where server content is stored.
var storageDir = os.Getenv("STORAGE_DIR")

// checkFile validates the given filename and returns its size in bytes.
// The filename is sanitized and verified to be within storageDir.
//
// It returns ErrInvalidFilename if the filename is invalid or escapes the
// storage directory, or ErrFileNotFound if the file does not exist or cannot
// be accessed.
func checkFile(filename string) (int64, error) {
	if storageDir == "" {
		return 0, ErrFileNotFound
	}

	sanitizedFilename := filepath.Clean(filename)
	if sanitizedFilename == "." {
		return 0, ErrInvalidFilename
	}

	// Build the full path verify it remains within storageDir
	// to prevent directory traversal attacks.
	fullPath := filepath.Join(storageDir, sanitizedFilename)
	if !strings.HasPrefix(fullPath, filepath.Clean(storageDir)+string(filepath.Separator)) {
		return 0, ErrInvalidFilename
	}

	fileinfo, err := os.Stat(fullPath)
	if err != nil {
		return 0, ErrFileNotFound
	}

	return fileinfo.Size(), nil
}

// calculateChunks returns the number of chunks required to send contentLen bytes,
// based on ChunkSize.
func calculateChunks(contentLen int64) int {
	return int(math.Ceil(float64(contentLen) / float64(ChunkSize)))
}
