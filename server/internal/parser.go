package internal

import (
	"errors"
	"slices"
	"strings"
)

var (
	ErrInvalidRequest = errors.New("INVALID_REQUEST")
	ErrInvalidCommand = errors.New("INVALID_COMMAND")
)

// RequestArgs holds the parsed components of client request.
type RequestArgs struct {
	Cmd     string
	Content string
}

// ParseRequest parses  raw input string into a RequestArgs struct.
// The input must contain at least a command and content separated by a space.
//
// It returns ErrInvalidRequest if the input is malformed,
// or ErrInvalidCommand if the command is not recognized.
func ParseRequest(input string) (*RequestArgs, error) {
	parts := strings.Split(input, " ")

	if len(parts) < 2 {
		return nil, ErrInvalidRequest
	}

	reqArgs := &RequestArgs{parts[0], parts[1]}

	if err := checkReqCmd(reqArgs.Cmd); err != nil {
		return nil, err
	}

	return reqArgs, nil
}

// checkReqCmd reports whether cmd is a valid request command.
// Valid commands are: /get, /post, /put, /delete.
//
// It returns ErrInvalidCommand if the command is not recognized.
func checkReqCmd(cmd string) error {
	allowedCmds := []string{"/get", "/post", "/put", "/delete"}

	if !slices.Contains(allowedCmds, cmd) {
		return ErrInvalidRequest
	}

	return nil
}
