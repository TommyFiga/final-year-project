package bot

import (
	"context"

	"github.com/go-telegram/bot"
)

type Bot struct {
	inner *bot.Bot
}

func New(token string) (*Bot, error) {
	opts := []bot.Option{
		bot.WithMiddlewares(),
		bot.WithDefaultHandler(Handler),
	}

	b, err := bot.New(token, opts...)
	if err != nil {
		return nil, err
	}

	return &Bot{inner: b}, nil
}

func (b *Bot) Start(ctx context.Context) {
	b.inner.Start(ctx)
}
