# Final-Year Project
> PoC and evaluation of restriction evasion over messaging services.


## Overview
In environments such as commercial flights, it is very common for internet access packages to be sold. In most cases, as a courtesy, a free internet package is offered that allows passengers to access messaging applications such as WhatsApp and Telegram. However, these applications are usually limited to text messages only. This raises the following question:

> _Is it possible to use authorized messaging applications as a way to bypass network limitations?_

To answer this question, a PoC of an **evasion mechanism** using Telegram messages as a communication channel will be implemented. And a **detection mechanism** based on Machine Learning techniques will also be developed, capable of analysing raw Wireshark traffic and categorizing it as either evasion traffic or normal traffic.

> **Disclaimer:** This implementation is intended exclusively for academic purposes. There is no intention to use this type of evasion mechanism outside an academic research context.


## Objectives
Main objectives:
- Implement the evasion mechanism
- Evaluate the viability of the evasion mechanism
- Evaluate the efficiency and security of these types of network restrictions
- Implement the detection mechanism
- Evaluate the effectiveness of the detection mechanism using multiple classifiers (e.g., kNN, SVM, Random Forest)

Optional objectives:
- Support SOCKS5 integration for the evasion mechanism client
- Support additional methods (e.g., POST, PUT, and DELETE) for the evasion mechanism protocol