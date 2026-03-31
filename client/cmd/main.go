package main

import (
	"context"
	"log"
	"os"
	"os/signal"
	"telegram-proxy-client/internal"
	"telegram-proxy-client/internal/telegram"
)


func main() {
	config, err := internal.LoadEnv()
	if err != nil {
		log.Fatalf("LoadEnv() error: %v", err)
	}
	
	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
	defer cancel()

	tdlibClient, err := telegram.StartClient(config)
	if err != nil {
		log.Fatalf("StartClient() error: %v", err)
	}
	defer tdlibClient.Close(ctx)

	log.Print("Client Started...")
	<-ctx.Done()
}
