package input

import (
	"bufio"
	"context"
	"fmt"
	"os"
	"strings"
	"telegram-proxy-client/internal/telegram"
)

func StartReader(ctx context.Context, client *telegram.TdlibClient, wait func()) {
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
		
		client.SendMessage(ctx, trimmed)
		wait()
	}
}