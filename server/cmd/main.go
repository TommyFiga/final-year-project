package main

import (
	"context"
	"log"
	"os"
	"os/signal"

	"github.com/go-telegram/bot"
	"github.com/go-telegram/bot/models"
)

func main() {
	var token = os.Getenv("API_TOKEN")
	if token == "" {
		log.Fatal("Bot API_TOKEN missing")
	}


	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
	defer cancel()

	opts := []bot.Option{
		bot.WithMiddlewares(showMessageWithUserID, showMessageWithUserName),
		bot.WithDefaultHandler(handler),
	}

	b, err := bot.New(token, opts...)
	if nil != err {
		log.Fatal("Invalid Bot Token!!")
		panic(err)
	}

	log.Print("Bot started (long polling)...")
	b.Start(ctx)
}

func showMessageWithUserID(next bot.HandlerFunc) bot.HandlerFunc {
	return func(ctx context.Context, b *bot.Bot, update *models.Update) {
		if update.Message != nil {
			log.Printf("%d says: %s", update.Message.From.ID, update.Message.Text)
		}

		next(ctx, b, update)
	}
}

func showMessageWithUserName(next bot.HandlerFunc) bot.HandlerFunc {
	return func(ctx context.Context, b *bot.Bot, update *models.Update) {
		if update.Message != nil {
			log.Printf("%s says: %s", update.Message.From.Username, update.Message.Text)
		}

		next(ctx, b, update)
	}
}

func handler(ctx context.Context, b *bot.Bot, update *models.Update) {
	b.SendMessage(ctx, &bot.SendMessageParams{
		ChatID: update.Message.Chat.ID,
		Text:   update.Message.Text,
	})
}
