package main

import (
	"context"
	"log"
	"os"
	"os/signal"
	"telegram-proxy-server/internal"
	"telegram-proxy-server/internal/bot"
)

func main() {
	config, err := internal.LoadEnv()
	if err != nil {
		log.Fatalf("LoadEnv() error: %v", err)
	}

	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
	defer cancel()

	b, err := bot.New(config)
	if err != nil {
		log.Fatalf("Failed creating Bot: %v", err)
	}

	log.Print("Bot started (long polling)...")
	b.Start(ctx)
}
