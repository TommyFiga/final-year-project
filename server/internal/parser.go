package internal

import (
	"errors"
	"strings"
)

var (
	ErrInvalidRequest = errors.New("INVALID_REQUEST")
	ErrInvalidCommand = errors.New("INVALID_COMMAND")
)

// RequestArgs holds the parsed components of a client request.
type RequestArgs struct {
	Method  string
	Content string
}

// ParseRequest parses a raw input string into a RequestArgs struct.
// The input must contain at least a command and content separated by a space.
//
// It returns ErrInvalidRequest if the input is malformed,
// or ErrInvalidCommand if the command is not recognized.
func ParseRequest(input string) (*RequestArgs, error) {
	parts := strings.Split(input, " ")

	if len(parts) < 2 {
		return nil, ErrInvalidRequest
	}

	method, err := checkReqCmd(parts[0])
	if err != nil {
		return nil, err
	}

	return &RequestArgs{
		Method:  method,
		Content: parts[1],
	}, nil
}

// checkReqCmd reports whether cmd is a valid request command.
// Valid commands are: /get, /post, /put, /delete.
// 
// It returns the normalized HTTP method (e.g., GET, POST) if valid
// or ErrInvalidCommand if the command is not recognized.
func checkReqCmd(cmd string) (string, error) {
	allowedCmds := map[string]string{
		"/get":    "GET",
		"/post":   "POST",
		"/put":    "PUT",
		"/delete": "DELETE",
	}

	method, ok := allowedCmds[cmd]
	if !ok {
		return "", ErrInvalidCommand
	}

	return method, nil
}
