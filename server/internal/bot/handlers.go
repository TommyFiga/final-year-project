package bot

import (
	"context"
	"errors"
	"log"
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
	log.SetFlags(log.LstdFlags | log.Lmicroseconds)
	log.Printf("Request received: %s", update.Message.Text)

	session := Session{
		ctx:    ctx,
		b:      b,
		chatID: update.Message.Chat.ID,
	}

	reqArgs, err := protocol.ParseRequest(update.Message.Text)
	if err != nil {
		header := protocol.BuildHeader(protocol.ResolvedResource{Status: errorToStatus(err)})
		session.send(header)
		return
	}

	resolvedResource, err := protocol.Resolve(*reqArgs)
	if err != nil {
		header := protocol.BuildHeader(protocol.ResolvedResource{Status: errorToStatus(err)})
		session.send(header)
		return
	}
	defer resolvedResource.Cleanup()

	header := protocol.BuildHeader(*resolvedResource)
	session.send(header)

	chunks, errs := protocol.StreamFile(resolvedResource.FilePath)
	for chunk := range chunks {
		time.Sleep(1000 * time.Millisecond)
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
	case errors.Is(err, protocol.ErrInvalidCommand),
		errors.Is(err, protocol.ErrInvalidFilename),
		errors.Is(err, protocol.ErrInvalidRequest):
		return protocol.StatusInvalidRequest
	case errors.Is(err, protocol.ErrFileNotFound):
		return protocol.StatusNotFound
	case errors.Is(err, protocol.ErrStorageNotFound),
		errors.Is(err, protocol.ErrRequestCreation),
		errors.Is(err, protocol.ErrResponseMaking),
		errors.Is(err, protocol.ErrCreatingTempFile),
		errors.Is(err, protocol.ErrWritingToTempFile):
		return protocol.StatusServerError
	default:
		return protocol.StatusServerError
	}
}
