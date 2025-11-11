# Telepay Service Modules

Telepay is a modular backend service layer designed to enable fast, secure, and user-friendly peer-to-peer payments within Telegram. It provides structured service classes that connect blockchain-based payment rails (specifically Solana and USDC) to Telegram user identifiers, enabling payments to occur seamlessly between Telegram usernames rather than wallet addresses.

This repository contains a subset of the backend service code used within the larger Telepay ecosystem. These Python modules represent the core logic for wallet management, invoice tracking, Solana RPC communication, and transaction building through Phantom Wallet.

------------------------------------------------------------

![Telepay Banner](assets/banner.jpg)

## Overview

Telepay allows Telegram users to send and receive USDC payments directly inside chat sessions. It uses the Solana blockchain as the settlement layer and leverages Phantom for wallet signing. Each Telegram user is mapped to an on-chain wallet address, and every payment is handled as a fully verifiable blockchain transaction.

The service modules in this repository are lightweight, decoupled, and designed for integration with other parts of the Telepay backend (such as FastAPI endpoints and Telegram bot handlers).

------------------------------------------------------------

## Key Components

### 1. services/phantom_link.py

Builds a deep link for Phantom Wallet that automatically opens the signing interface for the user. This allows Telepay to present a ready-to-sign transaction link inside Telegram, ensuring the user can authorize payment with one tap.

- Automatically adds an "autorun" parameter to trigger immediate signing.
- Designed for use with the "/phantom/sign" route of the web service.
- Relies on the PUBLIC_BASE_URL environment variable defined in core.config.

### 2. services/rpc.py

Implements a clean, minimal JSON-RPC client for Solana nodes. It supports key RPC methods that Telepay relies on, including balance checks, account information retrieval, and raw transaction submission.

Functions include:
- get_latest_blockhash() - fetches a recent finalized blockhash for transaction compilation.
- get_account_info(pubkey) - fetches account metadata and base64-encoded data.
- get_balance_lamports(pubkey) - returns balance in lamports (1 SOL = 1e9 lamports).
- get_token_account_by_owner(owner, mint) - fetches a user's token account address for a specific mint.
- get_token_balance_ui(token_account) - retrieves human-readable token balance.
- send_raw_transaction(raw_base64) - submits a signed base64 transaction to the Solana cluster.

### 3. services/solana_service.py

Handles Solana transaction construction for Telepay. It builds complete USDC transfer transactions, checking for account existence, balance sufficiency, and ensuring associated token accounts (ATA) are created when needed.

Core features:
- Automatic creation of ATAs if they do not exist.
- Transfer of USDC using TransferChecked instruction for precision.
- Balance pre-checks ensure both SOL and USDC are sufficient.
- Produces a base64-encoded unsigned transaction (BuiltTx) ready for Phantom signing.
- Compatible with Solders library for high-performance serialization.

### 4. services/user_service.py

Maintains Telegram user records in the Telepay database. It ensures users are created or updated as they interact with the bot and provides lookup functionality by username or user ID.

- Inserts new users as needed.
- Updates usernames if changed.
- Retrieves Telegram user IDs by username or ID.

### 5. services/wallet_service.py

Manages Telegram users' linked Solana wallets. It allows each user to maintain multiple wallets but ensures that only one is active at a time.

Functions include:
- add_wallet() - registers a new wallet for a Telegram user.
- list_wallets() - lists all wallets linked to a user.
- set_active() - marks one wallet as active and deactivates others.
- disconnect() - removes a wallet link from the user.
- active_wallet() - fetches the currently active wallet address.

### 6. services/x402_service.py

Implements invoice and payment record management for the x402 payment system used internally by Telepay.

Functions include:
- create_invoice(resource_id, price_usdc_int, buyer_tg_id) - generates a new open invoice.
- mark_paid(invoice_id) - updates invoice status to paid after successful blockchain confirmation.
- get_invoice(invoice_id) - retrieves full invoice details from the database.

------------------------------------------------------------

## Dependencies

Telepay uses the following Python dependencies:

- python-telegram-bot - Telegram bot framework for user interaction.
- fastapi + uvicorn - Web API layer for Phantom link callbacks and REST services.
- requests - HTTP client used by the Solana RPC wrapper.
- pynacl, base58 - for cryptographic and encoding utilities.
- solders - modern, high-speed Python library for Solana transaction handling.

These are pinned in the provided requirements.txt.

------------------------------------------------------------

## Architecture Notes

Telepay's architecture follows a service-oriented approach. Each module in services/ handles a specific logical responsibility and communicates through minimal interfaces. Database operations are abstracted through the core.db layer, which provides helper methods for executing SQL queries and returning results.

The system's main flow for user payments is as follows:

1. Telegram Interaction
   - The user types a command such as /pay @username 10 in the Telegram chat.
   - The Telegram bot calls the internal FastAPI backend to begin processing.

2. Invoice Creation
   - The backend uses X402Service to create a payment invoice and generate an ID.

3. Transaction Build
   - The backend calls SolanaService.build_usdc_transfer() to prepare a USDC transaction.

4. Phantom Signing
   - The backend constructs a signing link using PhantomLink.build_sign_link() and sends it to the Telegram user.
   - The user signs in Phantom, which returns the signed transaction to the backend.

5. Transaction Submission
   - The backend sends the signed transaction via Rpc.send_raw_transaction().
   - The invoice is marked paid with X402Service.mark_paid().

6. Confirmation and Logging
   - The system notifies both sender and recipient via Telegram that the payment succeeded.

------------------------------------------------------------

## Future Improvements

Planned enhancements include:
- Multi-token support beyond USDC.
- On-chain payment verification tracking with webhook callbacks.
- Integration with Telegram inline buttons for faster payment flows.
- User-to-merchant escrow or tip mechanisms.
- Enhanced database migrations with Alembic for schema versioning.

------------------------------------------------------------

## Author and License

[Follow Telepay on X](https://x.com/UseTelepay)

Telepay was developed as part of a broader research and engineering initiative focused on linking decentralized finance tools with mainstream messaging platforms.
All code is released under the MIT License (see LICENSE file).

------------------------------------------------------------

## Summary

Telepay's modular backend services combine simplicity, performance, and security. By mapping Telegram user identities to Solana wallet addresses and enabling Phantom-based transaction signing, it provides an efficient pathway for global peer-to-peer payments directly inside Telegram. Each module is intentionally small, testable, and composable, allowing developers to integrate or extend the system for their own blockchain payment applications.
