package internal

import (
	"errors"
	"os"
)

type Config struct {
	ApiToken   string
	StorageDir string
}

func LoadEnv() (*Config, error) {
	var (
		apiToken   = os.Getenv("API_TOKEN")
		storageDir = os.Getenv("STORAGE_DIR")
	)

	if apiToken == "" {
		return nil, errors.New("missing api token")
	}

	if storageDir == "" {
		return nil, errors.New("missing storage directory")
	}

	return &Config{
		ApiToken: 	apiToken,
		StorageDir: storageDir,
	}, nil
}