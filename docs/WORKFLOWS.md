# Workflow Contract Reference

This document defines workflow behavior for this reusable repo only.

Caller-side command parsing and PR comment behavior are in:
[caller-repo-template/docs/MAINTAINER_GUIDE.md](https://github.com/kpj2006/caller-repo-template/blob/main/docs/MAINTAINER_GUIDE.md)

## Available Workflows

- .github/workflows/x402-settlement.yml
  - Trigger: workflow_call
  - Use: production integration
- .github/workflows/x402-settlement-demo.yml
  - Trigger: workflow_dispatch
  - Use: manual validation

## Reusable Workflow Contract

File:

- [.github/workflows/x402-settlement.yml](../.github/workflows/x402-settlement.yml)

Required inputs:

- repo_name (string): owner/repo of callback target
- issue_number (number): issue or PR number for status callback
- recipient_wallet (string): destination wallet
- score_amount (number): token amount
- network (string): monad-testnet or monad-mainnet

Required secrets:

- THIRDWEB_SECRET_KEY: Thirdweb backend auth
- SERVER_WALLET: private key with mint authority
- SCORE_TOKEN_CONTRACT: deployed SCORE token contract
- RPC_URL: Monad RPC endpoint
- GITHUB_TOKEN: callback comment permission

Success outputs:

- TX_HASH
- EXPLORER_URL

## Demo Workflow Contract

File:

- [.github/workflows/x402-settlement-demo.yml](../.github/workflows/x402-settlement-demo.yml)

Purpose:

- Execute settlement manually from Actions UI to validate chain config and credentials.

Expected usage:

- Testnet smoke tests
- Contract/wallet validation
- Integration debugging

## Error Surface Ownership

Reusable repo owns:

- Address validation, on-chain execution, callback status

Caller repo owns:

- Parsing /send command
- Verifying who is allowed to trigger settlement
- Determining reward amount policy
