package telegram

import (
	"context"
	"telegram-proxy-client/internal"

	"github.com/zelenin/go-tdlib/client"
)

type TdlibClient struct {
	inner *client.Client
}

func (c *TdlibClient) Close(ctx context.Context) {
	c.inner.Close(ctx)
}

func StartClient(config *internal.Config) (*TdlibClient, error) {
	tdlibParameters := &client.SetTdlibParametersRequest{
		UseTestDc:           false,
		DatabaseDirectory:   config.TdlibDatabase,
		FilesDirectory:      config.TdlibFiles,
		UseFileDatabase:     true,
		UseChatInfoDatabase: true,
		UseMessageDatabase:  true,
		UseSecretChats:      false,
		ApiId:               config.ApiID,
		ApiHash:             config.ApiHash,
		SystemLanguageCode:  "en",
		DeviceModel:         "Server",
		SystemVersion:       "1.0.0",
		ApplicationVersion:  "1.0.0",
	}

	authorizer := client.ClientAuthorizer(tdlibParameters)
	go client.CliInteractor(authorizer)

	_, err := client.SetLogVerbosityLevel(&client.SetLogVerbosityLevelRequest{
		NewVerbosityLevel: 1,
	})
	if err != nil {
		return nil, err
	}

	tdlibClient, err := client.NewClient(
		authorizer,
		client.WithResultHandler(
			client.NewCallbackResultHandler(NewMessageListener(config.BotID, config.DownloadDir)),
		),
	)
	if err != nil {
		return nil, err
	}

	return &TdlibClient{inner: tdlibClient}, nil
}
