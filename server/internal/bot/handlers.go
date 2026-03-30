package bot

import (
	"context"
	"errors"
	"telegram-proxy-server/internal/protocol"
	"time"

	"github.com/go-telegram/bot"
	"github.com/go-telegram/bot/models"
)

// Session holds the Telegram bot context for a single message interaction,
// grouping the fields required to send messages back to the client.
type Session struct {
	ctx    context.Context
	b      *bot.Bot
	chatID int64
}

// send delivers a text message to the session's chat.
func (s Session) send(text string) {
	s.b.SendMessage(s.ctx, &bot.SendMessageParams{
		ChatID: s.chatID,
		Text:   text,
	})
}

// Handler is the main Telegram bot handler. It parses the incoming message,
// resolves the requested resource, and streams its content back to the client
// as base64-encoded chunks, preceded by a protocol response header.
func Handler(ctx context.Context, b *bot.Bot, update *models.Update) {
	session := Session{
		ctx:    ctx,
		b:      b,
		chatID: update.Message.Chat.ID,
	}

	reqArgs, err := internal.ParseRequest(update.Message.Text)
	if err != nil {
		header := internal.BuildHeader(internal.ResolvedResource{Status: errorToStatus(err)})
		session.send(header)
		return
	}

	resolvedResource, err := internal.Resolve(*reqArgs)
	if err != nil {
		header := internal.BuildHeader(internal.ResolvedResource{Status: errorToStatus(err)})
		session.send(header)
		return
	}
	defer resolvedResource.Cleanup()

	header := internal.BuildHeader(*resolvedResource)
	session.send(header)

	chunks, errs := internal.StreamFile(resolvedResource.FilePath)
	for chunk := range chunks {
		time.Sleep(time.Second)
		session.send(chunk)
	}

	if err := <-errs; err != nil {
		return
	}
}

// errorToStatus maps internal package errors to their corresponding protocol
// status codes. Unrecognized errors default to StatusServerError.
func errorToStatus(err error) int {
	switch {
	case errors.Is(err, internal.ErrInvalidCommand),
		errors.Is(err, internal.ErrInvalidFilename),
		errors.Is(err, internal.ErrInvalidRequest):
		return internal.StatusInvalidRequest
	case errors.Is(err, internal.ErrFileNotFound):
		return internal.StatusNotFound
	case errors.Is(err, internal.ErrStorageNotFound),
		errors.Is(err, internal.ErrRequestCreation),
		errors.Is(err, internal.ErrResponseMaking),
		errors.Is(err, internal.ErrCreatingTempFile),
		errors.Is(err, internal.ErrWritingToTempFile):
		return internal.StatusServerError
	default:
		return internal.StatusServerError
	}
}
