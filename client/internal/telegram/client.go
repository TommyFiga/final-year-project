package telegram

import (
	"context"
	"log"
	"telegram-proxy-client/internal"

	"github.com/zelenin/go-tdlib/client"
)

type TdlibClient struct {
	inner  *client.Client
	chatID int64
}

func (c *TdlibClient) SendMessage(ctx context.Context, request string) {
	_, err := c.inner.SendMessage(ctx, &client.SendMessageRequest{
		ChatId: c.chatID,
		InputMessageContent: &client.InputMessageText{
			Text: &client.FormattedText{
				Text: request,
			},
		},
	})
	if err != nil {
		log.Fatalf("Unable to send message: %v", err)
	}

	log.SetFlags(log.LstdFlags | log.Lmicroseconds)
	log.Print("REQUEST_SENT")
}

func (c *TdlibClient) Close(ctx context.Context) {
	c.inner.Close(ctx)
}

func StartClient(config *internal.Config, session *Session) (*TdlibClient, error) {
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
			client.NewCallbackResultHandler(NewMessageListener(config.BotID, config.DownloadDir, session)),
		),
	)
	if err != nil {
		return nil, err
	}

	return &TdlibClient{inner: tdlibClient, chatID: config.BotID}, nil
}
