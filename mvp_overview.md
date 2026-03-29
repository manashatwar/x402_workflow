# MVP Overview: x402 Cross-Repo Settlement System

This document provides a single end-to-end overview of the two-repository x402 workflow:

- Caller repository (client-facing PR workflow): [kpj2006/caller-repo-template](https://github.com/kpj2006/caller-repo-template.git)
- Reusable settlement engine repository: [manashatwar/x402_workflow](https://github.com/manashatwar/x402_workflow.git)

It is based on current workflow files and settlement source code in this repository.

## 1. System Purpose

The x402 system is a **stateless CI/CD execution engine** that transfers tokens to pull request contributors after maintainer approval. The engine is not tied to any specific token or network.

- Caller repo handles GitHub PR interaction and approval command flow.
- Reusable repo (execution engine) orchestrates transactions on client-provided infrastructure and callback reporting.
- Client provides and owns: token contract, treasury contract (optional), RPC endpoint, operator wallet, and chain configuration.

## 1a. Client Responsibilities

The client organization must provide:

- **RPC_URL**: endpoint for the chosen EVM chain (e.g., Monad testnet)
- **PRIVATE_KEY**: operator wallet with sufficient balance for gas and transfers
- **TOKEN_CONTRACT** or **TREASURY_CONTRACT**: address of the client-deployed token or treasury contract with transfer/disbursement capability (if using treasury model)
- **Recipient and amount inputs**: from the caller workflow based on PR events

The client owns and manages:

- All smart contracts (deployment, upgrades, governance)
- All operator wallets (private keys, funding, rotation)
- The chosen blockchain network and RPC infrastructure
- Settlement policies and payout rules (enforced at contract level)

## 1b. Security Modes

The engine has two execution modes for client configuration:

1. Direct transfer mode
- Uses client-provided token contract for direct transfer execution.
- Best for compatibility, testnet, and early-stage rollouts.

2. Treasury mode(**currently out of scope, planned for Phase 3**)
- Uses client-provided treasury contract for `disburse(recipient, amount)` execution.
- Best for production environments requiring limits, pause controls, and stricter operator permissions.

This allows existing deployments to integrate immediately, then migrate to stronger controls without breaking caller workflows.

## 1c. Governance Split (Web2 vs Web3)

- GitHub governance controls who can trigger payouts (branch protection, approvals, status checks, maintainer commands).
- Contract governance controls what payout execution is allowed (limits, pause, authorization).

The engine bridges these layers but does not replace either governance system.

## 2. Repository Roles

### Caller Repository (kpj2006/caller-repo-template)

Primary file:

- .github/workflows/pr-x402-trigger.yml

Responsibilities:

- Post welcome message when PR opens.
- Accept and validate contributor wallet comments in the format `x402-wallet: 0x...`.
- Accept maintainer `/send <amount>` command.
- Check maintainer permissions (`admin` or `write`).
- Extract amount and locate PR author wallet.
- Call reusable workflow with normalized inputs.
- Show user-facing error/status messages for invalid command or missing wallet.

### Reusable Repository (manashatwar/x402_workflow) - Execution Engine

Primary files:

- .github/workflows/x402-settlement.yml
- .github/workflows/x402-settlement-demo.yml
- src/settlement/sendScore.js

Responsibilities (stateless execution only):

- Accept and validate settlement inputs (recipient, amount, contract address, RPC URL).
- Validate wallet and contract formats.
- Build and sign transaction using client-provided RPC and private key.
- Execute transaction against client-provided chain.
- Emit `TX_HASH` and `EXPLORER_URL` outputs.
- Post success/failure callback comment to caller repository using callback token.

**The engine does not:**

- Deploy or manage contracts
- Select or manage blockchain networks
- Store or custody funds
- Make policy decisions (all controlled by contract and client)

## 3. End-to-End Flow

```mermaid
flowchart TD
    A[PR Opened in Caller Repo] --> B[welcome_message job posts wallet instructions]
    B --> C[PR Author comments x402-wallet: 0x...]
    C --> D[store_wallet job validates and acknowledges wallet]
    D --> E[Maintainer comments /send amount]
    E --> F[maintainer_send checks collaborator permission]
    F --> G[Extract amount and find PR author wallet]
    G --> H[Caller triggers reusable x402-settlement.yml]

    H --> I[Reusable workflow validates wallet and contract format]
    I --> J[Execute src/settlement/sendScore.js]
    J --> K[Engine signs and sends transaction on client-provided RPC]
    K --> L[TX hash and explorer URL written to GITHUB_OUTPUT]
    L --> M[Reusable workflow posts callback comment to caller PR]

    F --> N[Permission denied message]
    G --> O[No wallet / invalid send format message]
```

## 4. Workflow Interface Contract

### Caller -> Reusable Inputs

Sent by caller `trigger_settlement` job:

- `repo_name`: caller repository (owner/repo)
- `issue_number`: PR number
- `recipient_wallet`: extracted PR author wallet
- `score_amount`: parsed from `/send <amount>`
- `network`: currently `monad-testnet` in caller template

### Required Secrets for Reusable Workflow

Defined in `.github/workflows/x402-settlement.yml`:

- `THIRDWEB_SECRET_KEY`
- `SERVER_WALLET`
- `SCORE_TOKEN_CONTRACT`
- `RPC_URL`
- `CALLBACK_GITHUB_TOKEN`

In caller template mapping, these are provided from caller secrets:

- `X402_SERVER_WALLET` -> `SERVER_WALLET`
- `X402_SCORE_TOKEN_CONTRACT` -> `SCORE_TOKEN_CONTRACT`
- `X402_RPC_URL` -> `RPC_URL`
- `X402_WORKFLOW_TOKEN` -> `CALLBACK_GITHUB_TOKEN`

## 5. Runtime Components

### GitHub Actions Layer

- Event processing and command orchestration
- Permission checks and guard rails
- Cross-repo workflow dispatch
- Callback comment publishing

### Settlement Engine Layer

`src/settlement/sendScore.js` performs:

- Required env validation
- Address validation with `ethers.isAddress`
- Network selection (`monad-testnet` or `monad-mainnet`)
- transaction preparation
- Transaction broadcast + hash capture
- Explorer URL construction

### Blockchain Layer

- Monad network RPC endpoint
- Client-provided contract execution call (for example `transfer(address,uint256)` or treasury `disburse(address,uint256)`)
- On-chain transaction confirmation via tx hash

## 6. Failure/Guard Paths

Caller-side guard paths:

- Non-maintainer `/send` -> permission denied comment
- Invalid `/send` format -> usage hint comment
- Missing PR author wallet -> wallet required comment

Reusable-side guard paths:

- Invalid input addresses -> workflow fail
- Missing required env/secrets -> workflow fail
- Transaction error -> failure callback comment

## 7. Operational Notes

- The two repositories are independent deploy units and should reference each other via GitHub URLs, not local relative paths.
- The caller template is designed for client adoption in separate repositories.
- `x402-settlement-demo.yml` is useful for manual smoke tests before wiring caller automation.

## 8. Key Files to Review

Caller repo (template):

- `.github/workflows/pr-x402-trigger.yml`
- `docs/QUICKSTART.md`
- `docs/MAINTAINER_GUIDE.md`

Reusable repo (this repo):

- `.github/workflows/x402-settlement.yml`
- `.github/workflows/x402-settlement-demo.yml`
- `src/settlement/sendScore.js`
- `docs/ARCHITECTURE.md`
- `docs/WORKFLOWS.md`
