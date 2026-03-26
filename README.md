# Final-Year Project
> PoC implementation for a _proxy_ using Telegram as the communication channel.


## Overview
Usually in environments like commercial flights, it's very common to sell internet access packages. In most cases, as a courtesy, a free internet pack is offered that allows passengers to access text message applications such as WhatsApp and Telegram. 

However, these applications are usually limited to text messages only. This raises the following question:

> _Is it possible to use the actual authorized app messages as a way of surpassing the network limitations?_ 

To answer this question, there will be an implementation of a PoC of an evasion mechanism using Telegram messages as a communication channel.


## How it Works
The PoC is composed of two agents: a `client` and a `server`. The `client` sends requests through Telegram messages, which the `server` receives, processes, and responds to using a custom protocol. 

The exchanged content is encoded to support binary transmission and reassembled on the client side.

> **Disclaimer**: This implementation is being used exclusively for academic purposes, there is no intention of using this type of mechanism outside of an academic context.
