# Architecture

## Scope

This document describes reusable settlement architecture only.

Caller repository behavior (PR comments, /send command UX, maintainer policy) is documented in [caller-repo-template/docs/README.md](https://github.com/kpj2006/caller-repo-template/blob/main/docs/README.md).

## Two-Repository Model

1. Caller repo receives GitHub events and decides when to settle.
2. Reusable repo executes settlement on-chain.

Handoff contract:

- Caller sends workflow inputs and secrets.
- Reusable workflow validates and mints.
- Reusable workflow reports success or failure back to GitHub.

## Component View

- Reusable workflow: [.github/workflows/x402-settlement.yml](../.github/workflows/x402-settlement.yml)
- Demo workflow: [.github/workflows/x402-settlement-demo.yml](../.github/workflows/x402-settlement-demo.yml)
- Settlement engine: [src/settlement/sendScore.js](../src/settlement/sendScore.js)
- Chain config: [config/chainConfig.js](../config/chainConfig.js)
- Address validation: [src/validation/addressValidator.js](../src/validation/addressValidator.js)

## Runtime Flow

1. Caller triggers reusable workflow with validated business intent.
2. Reusable workflow injects inputs as environment variables.
3. Settlement engine validates all required values.
4. Engine resolves chain settings from network key.
5. Engine submits mint transaction through Thirdweb.
6. Workflow surfaces transaction hash and explorer URL.
7. Workflow posts completion result to the linked GitHub context.

## Trust Boundaries

- Boundary A: Caller repo to reusable workflow (input trust boundary).
- Boundary B: Reusable workflow to blockchain RPC (network trust boundary).
- Boundary C: Reusable workflow to GitHub API callback (reporting boundary).

Each boundary has explicit validation and error handling. Caller-side authorization must remain in caller repo.

## Network Targets

- monad-testnet
  - Chain ID: 10143
  - Explorer: [testnet.monadvision.com](https://testnet.monadvision.com)
- monad-mainnet
  - Chain ID: 41454
  - Explorer: [monadvision.com](https://monadvision.com)
