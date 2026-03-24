package internal

import (
	"errors"
	"io"
	"math"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

// ChunkSize defines the maximum size in bytes of each content chunk.
const ChunkSize = 4096

var (
	ErrInvalidFilename   = errors.New("invalid filename")
	ErrFileNotFound      = errors.New("file not found")
	ErrStorageNotFound   = errors.New("storage dir not found")
	ErrRequestCreation   = errors.New("failed creating a request")
	ErrResponseMaking    = errors.New("failed making response")
	ErrCreatingTempFile  = errors.New("failed creating a temporary file")
	ErrWritingToTempFile = errors.New("failed writing to temp file")
)

// storageDir is the root directory where server content is stored.
var storageDir = os.Getenv("STORAGE_DIR")

// resolveRemote fetches an internet resource and stores it in a temporary file.
// It replicates the HTTP response, meaning that even if the status is 4xx or
// 5xx the response is still propagated.
//
// It returns ErrRequestCreation if creating the request fails, ErrResponseMaking
// if executing the request fails, ErrCreatingTempFile if the temporary file
// cannot be created, or ErrWritingToTempFile if writing the response body fails.
func resolveRemote(url string) (string, int64, error) {
	client := &http.Client{}

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return "", 0, ErrRequestCreation
	}

	resp, err := client.Do(req)
	if err != nil {
		return "", 0, ErrResponseMaking
	}
	defer resp.Body.Close()

	tempfile, err := os.CreateTemp(storageDir, "remote-")
	if err != nil {
		return "", 0, ErrCreatingTempFile
	}

	filesize, err := io.Copy(tempfile, resp.Body)
	if err != nil {
		return "", 0, ErrWritingToTempFile
	}
	tempfile.Close()

	return tempfile.Name(), filesize, nil
}

// resolveLocal validates and resolves a local filename to its full path and size.
// It ensures the file exists within the storage directory, preventing directory
// traversal attacks.
//
// It returns ErrStorageNotFound if STORAGE_DIR is not configured, ErrInvalidFilename
// if the filename is invalid or escapes the storage directory, and ErrFileNotFound
// if the file does not exist.
func resolveLocal(filename string) (string, int64, error) {
	if storageDir == "" {
		return "", 0, ErrStorageNotFound
	}

	sanitizedFilename := filepath.Clean(filename)
	if sanitizedFilename == "." {
		return "", 0, ErrInvalidFilename
	}

	// Build the full path verify it remains within storageDir
	// to prevent directory traversal attacks.
	fullPath := filepath.Join(storageDir, sanitizedFilename)
	if !strings.HasPrefix(fullPath, filepath.Clean(storageDir)+string(filepath.Separator)) {
		return "", 0, ErrInvalidFilename
	}

	fileinfo, err := os.Stat(fullPath)
	if err != nil {
		return "", 0, ErrFileNotFound
	}

	return fullPath, fileinfo.Size(), nil
}

// calculateChunks returns the number of chunks required to send contentLen bytes, based on ChunkSize.
func CalculateChunks(contentLen int) int {
	return int(math.Ceil(float64(contentLen) / ChunkSize))
}

// calculateEncodedSize returns the content size after applying base64 encoding.
func CalculateEncodedSize(fileSize int64) int {
	return int(math.Ceil(float64(fileSize) / 3 * 4))
}
