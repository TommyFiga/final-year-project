package bot

import (
	"context"
	"errors"
	"telegram-proxy-server/internal"
	"time"

	"github.com/go-telegram/bot"
	"github.com/go-telegram/bot/models"
)

func Handler(ctx context.Context, b *bot.Bot, update *models.Update) {
	chatID := update.Message.Chat.ID
	usrMsg := update.Message.Text

	reqArgs, err := internal.ParseRequest(usrMsg)
	if err != nil {
		status := errorToStatus(err)
		sendHeader(ctx, b, chatID, status, 0, 0)
		return
	}

	filePath, err := internal.Sanitize(reqArgs.Content)
	if err != nil {
		status := errorToStatus(err)
		sendHeader(ctx, b, chatID, status, 0, 0)
		return
	}

	fileSize, err := internal.FileSize(filePath)
	if err != nil {
		status := errorToStatus(err)
		sendHeader(ctx, b, chatID, status, 0, 0)
		return
	}

	contentLen := internal.CalculateEncodedSize(fileSize)
	totalChunks := internal.CalculateChunks(contentLen)
	sendHeader(ctx, b, chatID, internal.StatusOk, contentLen, totalChunks)

	chunks, errs := internal.StreamFile(filePath)
	for chunk := range chunks {
		time.Sleep(time.Second)
		b.SendMessage(ctx, &bot.SendMessageParams{
			ChatID: chatID,
			Text: chunk,
		})
	}

	if err := <-errs; err != nil {
		return 
	}
}

func sendHeader(ctx context.Context, b *bot.Bot, chatId int64, status, contentLen, chunks int) {
	header := internal.BuildHeader(status, contentLen, chunks)

	b.SendMessage(ctx, &bot.SendMessageParams{
		ChatID: chatId,
		Text:   header,
	})
}

func errorToStatus(err error) int {
	switch {
	case errors.Is(err, internal.ErrInvalidCommand),
		errors.Is(err, internal.ErrInvalidFilename),
		errors.Is(err, internal.ErrInvalidRequest):
		return internal.StatusInvalidRequest
	case errors.Is(err, internal.ErrFileNotFound):
		return internal.StatusNotFound
	case errors.Is(err, internal.ErrStorageNotFound):
		return internal.StatusServerError
	default:
		return internal.StatusServerError
	}
}
