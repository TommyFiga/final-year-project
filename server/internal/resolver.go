package internal

import (
	"errors"
	"math"
	"os"
	"path/filepath"
	"strings"
)

// ChunkSize defines the maximum size in bytes of each content chunk.
const ChunkSize = 4096

var (
	ErrInvalidFilename = errors.New("invalid filename")
	ErrFileNotFound    = errors.New("file not found")
	ErrStorageNotFound = errors.New("storage dir not found")
)

// storageDir is the root directory where server content is stored.
var storageDir = os.Getenv("STORAGE_DIR")

// Sanitize validates if the received filename is valid and exists within the
// storage directory.
//
// It retuns ErrStorageNotFound if the storage directory isn't found and ErrInvalidFilename
// if the filename is out of the storage directory bounds or the file name is invalid
func Sanitize(filename string) (string, error) {
	if storageDir == "" {
		return "", ErrStorageNotFound
	}

	sanitizedFilename := filepath.Clean(filename)
	if sanitizedFilename == "." {
		return "", ErrInvalidFilename
	}

	// Build the full path verify it remains within storageDir
	// to prevent directory traversal attacks.
	fullPath := filepath.Join(storageDir, sanitizedFilename)
	if !strings.HasPrefix(fullPath, filepath.Clean(storageDir)+string(filepath.Separator)) {
		return "", ErrInvalidFilename
	}

	return fullPath, nil
}

// CheckFile returns the size of a file based on the filename provided.
//
// It returns ErrFileNotFound if the filename passed doesn't correspond to a
// valid file.
func FileSize(filename string) (int64, error) {
	fileinfo, err := os.Stat(filename)
	if err != nil {
		return 0, ErrFileNotFound
	}

	return fileinfo.Size(), nil
}

// calculateChunks returns the number of chunks required to send contentLen bytes,
// based on ChunkSize.
func CalculateChunks(contentLen int) int {
	return int(math.Ceil(float64(contentLen) / ChunkSize))
}

// calculateEncodedSize returns the content size after applying base64 encoding.
func CalculateEncodedSize(fileSize int64) int {
	return int(math.Ceil(float64(fileSize) / 3 * 4))
}
