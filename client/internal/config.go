package internal

import (
	"os"
	"strconv"
)

type Config struct {
	ApiHash       string
	ApiID         int32
	BotID         int64
	TdlibDatabase string
	TdlibFiles    string
	DownloadDir   string
}

func LoadEnv() (*Config, error) {
	var (
		apiHash       = os.Getenv("API_HASH")
		apiIDRaw      = os.Getenv("API_ID")
		botIDRaw      = os.Getenv("BOT_ID")
		tdlibDatabase = os.Getenv("TDLIB_DATABASE")
		tdlibFiles    = os.Getenv("TDLIB_FILES")
		downloadDir   = os.Getenv("DOWNLOAD_DIR")
	)

	apiID64, err := strconv.ParseInt(apiIDRaw, 10, 32)
	if err != nil {
		return nil, err
	}
	apiID := int32(apiID64)

	botID, err := strconv.ParseInt(botIDRaw, 10, 64)
	if err != nil {
		return nil, err
	}

	return &Config{
		ApiHash:       apiHash,
		ApiID:         apiID,
		BotID:         botID,
		TdlibDatabase: tdlibDatabase,
		TdlibFiles:    tdlibFiles,
		DownloadDir:   downloadDir,
	}, nil
}
