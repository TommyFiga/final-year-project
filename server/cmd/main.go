package main

import (
	"context"
	"log"
	"os"
	"os/signal"
	"telegram-proxy-server/internal/bot"
)

func main() {
	var token = os.Getenv("API_TOKEN")
	if token == "" {
		log.Fatal("Bot API_TOKEN missing")
	}

	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
	defer cancel()

	b, err := bot.New(token)
	if err != nil {
		log.Fatalf("Failed creating Bot: %v", err)
	}

	log.Print("Bot started (long polling)...")
	b.Start(ctx)
}
