package telegram

import (
	"context"
	
	"github.com/zelenin/go-tdlib/client"
)

func NewMessageListener(c *TdlibClient, downloadDir string, session *Session) func(client.Type) {
	return func(result client.Type) {
		msg, ok := extractMessageText(result, c.chatID)
		if !ok {
			return
		}

		msgText := msg.Content.(*client.MessageText).Text.Text

		switch session.state {
		case StateAwaitingHeader:
			session.handleHeader(msgText)
		case StateCollectingChunks:
			session.handleChunk(msgText)
		}
		
		msgID := msg.Id
		go c.DeleteMessage(context.Background(), msgID)
	}
}

func extractMessageText(result client.Type, botID int64) (*client.Message, bool) {
	if result.GetConstructor() != client.ConstructorUpdateNewMessage {
		return nil, false
	}

	msg := result.(*client.UpdateNewMessage).Message

	sender, ok := msg.SenderId.(*client.MessageSenderUser)
	if !ok || sender.UserId != botID {
		return nil, false
	}

	_, ok = msg.Content.(*client.MessageText)
	if !ok {
		return nil, false
	}
	
	return msg, true
}
