package telegram

import "github.com/zelenin/go-tdlib/client"

func NewMessageListener(botID int64, downloadDir string, session *Session) func(client.Type) {
	return func(result client.Type) {
		msg, ok := extractMessageText(result, botID)
		if !ok {
			return
		}

		switch session.state {
		case StateAwaitingHeader:
			session.handleHeader(msg)
		case StateCollectingChunks:
			session.handleChunk(msg)
		}
	}
}

func extractMessageText(result client.Type, botID int64) (string, bool) {
	if result.GetConstructor() != client.ConstructorUpdateNewMessage {
		return "", false
	}

	msg := result.(*client.UpdateNewMessage).Message

	sender, ok := msg.SenderId.(*client.MessageSenderUser)
	if !ok || sender.UserId != botID {
		return "", false
	}

	content, ok := msg.Content.(*client.MessageText)
	if !ok {
		return "", false
	}

	return content.Text.Text, true
}
