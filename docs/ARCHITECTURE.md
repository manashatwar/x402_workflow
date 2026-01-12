# Architecture Overview

## System Design

This repository implements a blockchain-based score settlement engine for GitHub contributor recognition. The system mints non-transferable ERC-20 tokens on the Monad blockchain as immutable proof of contribution.

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Actions                               │
│                                                                   │
│  ┌─────────────────┐         ┌─────────────────────────────┐     │
│  │ x402-settlement │         │ x402-settlement-demo.yml    │     │
│  │ .yml (Reusable) │         │ (Manual Trigger)            │     │
│  └────────┬────────┘         └──────────────┬──────────────┘     │
│           │                                  │                    │
│           └──────────────┬───────────────────┘                    │
│                          ▼                                        │
│              ┌───────────────────────┐                            │
│              │  sendScore.js         │                            │
│              │  (Settlement Engine)  │                            │
│              └───────────┬───────────┘                            │
│                          │                                        │
└──────────────────────────┼────────────────────────────────────────┘
                           │
                           ▼
              ┌───────────────────────┐
              │    Thirdweb SDK       │
              │  (Transaction Layer)  │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Monad Blockchain    │
              │  (Settlement Layer)   │
              │                       │
              │  ┌─────────────────┐  │
              │  │  ScoreToken     │  │
              │  │  ERC-20         │  │
              │  │  (Non-Transfer) │  │
              │  └─────────────────┘  │
              └───────────────────────┘
```

## Data Flow

1. **Trigger**: Workflow receives settlement request with recipient, amount, and metadata
2. **Validation**: Addresses and amounts are validated before execution
3. **Transaction**: Thirdweb SDK constructs and signs the mint transaction
4. **Execution**: Transaction is broadcast to Monad blockchain
5. **Confirmation**: Transaction hash and explorer URL are returned
6. **Output**: Results are written to `GITHUB_OUTPUT` for downstream steps

## Token Model

| Property     | Value                      |
| ------------ | -------------------------- |
| Standard     | ERC-20                     |
| Decimals     | 18                         |
| Transferable | No (`transfer()` reverts)  |
| Burnable     | Yes (minter only)          |
| Supply       | Unlimited (mint on demand) |

## Network Configuration

| Network       | Chain ID | RPC                       | Explorer                        |
| ------------- | -------- | ------------------------- | ------------------------------- |
| Monad Testnet | 10143    | https://testnet.monad.xyz | https://testnet.monadvision.com |
| Monad Mainnet | 41454    | https://rpc.monad.xyz     | https://monadvision.com         |
