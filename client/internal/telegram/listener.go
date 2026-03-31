package telegram

import (
	"log"

	"github.com/zelenin/go-tdlib/client"
)

func NewMessageListener(botID int64) func(client.Type) {
	return func(result client.Type) {
		if result.GetConstructor() != client.ConstructorUpdateNewMessage {
			return
		}

		msg := result.(*client.UpdateNewMessage).Message

		sender, ok := msg.SenderId.(*client.MessageSenderUser)
		if !ok || sender.UserId != botID {
			return
		}

		content, ok := msg.Content.(*client.MessageText)
		if !ok {
			return
		}

		log.Printf("Received message: %s", content.Text.Text)
	}
}
