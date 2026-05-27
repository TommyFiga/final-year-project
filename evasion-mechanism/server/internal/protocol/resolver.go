package protocol

import (
	"errors"
	"io"
	"mime"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

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

// ResolvedResource holds the metadata of a resolved resource, whether local or
// remote, required to stream its content back to the client.
type ResolvedResource struct {
	IsRemote    bool
	Status      int
	FilePath    string
	RawSize     int64
	ContentType string
	Headers		map[string][]string
}

func (r ResolvedResource) Cleanup() {
	if r.IsRemote {
		os.Remove(r.FilePath)
	}
}

// Resolve determines whether the requested content is a local or remote resource
// and delegates accordingly, returning a ResponseArgs containing the resolved
// file path, raw size, status and content type.
//
// It returns ErrStorageNotFound, ErrInvalidFilename, or ErrFileNotFound for local
// resources, and ErrRequestCreation, ErrResponseMaking, ErrCreatingTempFile, or
// ErrWritingToTempFile for remote resources.
func Resolve(reqArgs RequestArgs) (*ResolvedResource, error) {
	if strings.HasPrefix(reqArgs.Content, "http://") || strings.HasPrefix(reqArgs.Content, "https://") {
		return resolveRemote(reqArgs.Content)
	}

	return resolveLocal(reqArgs.Content)
}

// resolveRemote fetches an internet resource and stores it in a temporary file,
// replicating the HTTP response regardless of status code.
// It returns a ResponseArgs containing the temp file path, size in bytes,
// HTTP status code, and inferred content type.
//
// It returns ErrRequestCreation if creating the request fails, ErrResponseMaking
// if executing the request fails, ErrCreatingTempFile if the temporary file
// cannot be created, or ErrWritingToTempFile if writing the response body fails
func resolveRemote(url string) (*ResolvedResource, error) {
	client := &http.Client{}

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, ErrRequestCreation
	}

	resp, err := client.Do(req)
	if err != nil {
		return nil, ErrResponseMaking
	}
	defer resp.Body.Close()

	tempfile, err := os.CreateTemp(storageDir, "remote-")
	if err != nil {
		return nil, ErrCreatingTempFile
	}

	filesize, err := io.Copy(tempfile, resp.Body)
	if err != nil {
		tempfile.Close()
		os.Remove(tempfile.Name())
		return nil, ErrWritingToTempFile
	}
	tempfile.Close()

	contentType := "unknown"
	if ct := resp.Header.Get("Content-Type"); ct != "" {
		mediaType, _, err := mime.ParseMediaType(ct)
		if err == nil {
			parts := strings.SplitN(mediaType, "/", 2)
			if len(parts) == 2 {
				contentType = parts[1]
			}
		}
	}

	headers := make(map[string][]string)
	for k, v := range resp.Header {
		if k == "Content-Type" || k == "Content-Length" {
			continue
		}
		headers[k] = v
	}

	return &ResolvedResource{
		IsRemote:    true,
		Status:      resp.StatusCode,
		FilePath:    tempfile.Name(),
		RawSize:     filesize,
		ContentType: contentType,
		Headers: 	 headers,
	}, nil
}

// resolveLocal validates and resolves a local filename to its full path, size,
// and inferred content type. It ensures the file exists within the storage
// directory, preventing directory traversal attacks.
//
// It returns ErrStorageNotFound if STORAGE_DIR is not configured, ErrInvalidFilename
// if the filename is invalid or escapes the storage directory, and ErrFileNotFound
// if the file does not exist.
func resolveLocal(filename string) (*ResolvedResource, error) {
	if storageDir == "" {
		return nil, ErrStorageNotFound
	}

	sanitizedFilename := filepath.Clean(filename)
	if sanitizedFilename == "." {
		return nil, ErrInvalidFilename
	}

	// Build the full path verify it remains within storageDir
	// to prevent directory traversal attacks.
	fullPath := filepath.Join(storageDir, sanitizedFilename)
	if !strings.HasPrefix(fullPath, filepath.Clean(storageDir)+string(filepath.Separator)) {
		return nil, ErrInvalidFilename
	}

	fileinfo, err := os.Stat(fullPath)
	if err != nil {
		return nil, ErrFileNotFound
	}

	contentType := strings.TrimPrefix(filepath.Ext(fullPath), ".")
	if contentType == "" {
		contentType = "unknown"
	}

	return &ResolvedResource{
		IsRemote:    false,
		Status:      StatusOk,
		FilePath:    fullPath,
		RawSize:     fileinfo.Size(),
		ContentType: contentType,
		Headers: 	 nil,
	}, nil
}
