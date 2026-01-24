# Architecture Overview

## System Design

This repository implements a blockchain-based score settlement engine for GitHub contributor recognition. The system mints non-transferable ERC-20 tokens on the Monad blockchain as immutable proof of contribution.

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Actions                               │
│                                                                   │
│  ┌─────────────────┐         ┌─────────────────────────────┐     │
│  │ x402-settlement │         │ x402-settlement-demo.yml    │     │
│  │ .yml (Reusable) │         │ (Workflow Dispatch)         │     │
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

## Workflow Integration (PR-based Rewards)

```
┌──────────────────────────────────────────────────────────────────┐
│                    Caller Repository                              │
│                (pr-x402-trigger.yml workflow)                     │
│                                                                   │
│  1. PR Opened → Welcome Message (asks for wallet)                │
│  2. PR Author Comments: "x402-wallet: 0x..."                     │
│     → Wallet Saved (no execution yet)                            │
│  3. Maintainer Comments: "/send 100"                             │
│     → Permission Check                                           │
│     → Find PR Author's Wallet                                    │
│     → Trigger x402-settlement-demo.yml ──────────────────┐       │
│  4. Result Posted Back to PR                             │       │
└──────────────────────────────────────────────────────────┼───────┘
                                                           │
                                                           ▼
                                           (Triggers settlement in x402_workflow)
```

## Data Flow

### Phase 1: Wallet Collection (PR Author)
1. **PR Created**: Automatic welcome message asks for wallet
2. **Author Comments**: Submits wallet with `x402-wallet: 0x...` format
3. **Wallet Stored**: Acknowledged but not executed
4. **Wait**: Awaits maintainer approval

### Phase 2: Maintainer Approval & Execution
1. **Trigger**: Maintainer comments `/send <amount>` (e.g., `/send 100`)
2. **Permission Check**: Verifies commenter has write/admin access
3. **Wallet Retrieval**: Finds stored wallet from PR author's comments
4. **Validation**: Validates wallet address and amount
5. **Transaction**: Thirdweb SDK constructs and signs the mint transaction
6. **Execution**: Transaction is broadcast to Monad blockchain
7. **Confirmation**: Transaction hash and explorer URL are returned
8. **Callback**: Results are posted back to the PR as a comment

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
