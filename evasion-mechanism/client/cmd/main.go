package main

import (
	"bufio"
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"strings"
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

	session := telegram.NewSession(config.DownloadDir)
	tdlibClient, err := telegram.StartClient(config, session)
	if err != nil {
		log.Fatalf("StartClient() error: %v", err)
	}
	defer tdlibClient.Close(ctx)

	log.Print("Client Started...")
	rdr := bufio.NewReader(os.Stdin)

	for {
		fmt.Print("Send Message: ")
		line, err := rdr.ReadString('\n')
		if err != nil {
            fmt.Fprintln(os.Stderr, "error:", err)
            return 
		}

		trimmed := strings.TrimSpace(line)
		if trimmed == "quit" {
			return
		}
		
		tdlibClient.SendMessage(ctx, trimmed)
		session.Wait()
	}
}
