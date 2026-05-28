# Evasion Mechanism
> Proof-of-concept implementation of a proxy channel that uses Telegram messaging as the transport layer.

## Overview
The evasion mechanism demonstrates how a client can use Telegram messages to issue resource requests and receive content responses through a remote server. The server acts as a gateway that executes requests on behalf of the client, and the client receives the results over Telegram instead of a normal TCP/IP tunnel.

## Architecture
The implementation is split into three main parts:

- `protocol`: Defines the request/response format used by the client and server.
- `client`: Sends requests to the server over Telegram and receives response messages.
- `server`: Processes incoming requests and sends back structured responses through Telegram.

## Protocol
Communication is based on a simple request-response protocol inspired by HTTP.

### Request format
Requests are plain text messages sent from client to server.

```text
/METHOD resource
```

Examples:

```text
/GET local-file.png
/GET https://example.com/image.png
```

### Response format
Responses are sent as one header message plus one or more body messages.

Header format:

```text
s={status};b={total-bytes};c={chunks};ct={content-type}
{HTTP-headers}
```

Example header:

```text
s=200;b=30000;c=10;ct=png
```

Body content is encoded as Base64 and may span multiple Telegram messages depending on size.

## Components

### Server
The server listens for Telegram messages containing proxy requests, executes the requested operation, and returns the response metadata and payload as Telegram messages.

### Client
The client constructs and sends proxy requests over Telegram, then receives the server response and reconstructs the requested payload from the message stream.

## Design goals

- Demonstrate how messaging services can be leveraged as an alternate communication channel.
- Provide a structured request/response protocol on top of Telegram text messages.
- Support both local resource access and remote HTTP fetches through the server.

## Limitations

The design is constrained by Telegram’s messaging limits:

- Bot output rate: typically `1 message per second`
- Maximum message size: `4096 UTF-8 characters`
- Effective payload per body message is reduced by Base64 encoding overhead
