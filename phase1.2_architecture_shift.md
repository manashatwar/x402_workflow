# Phase 2 Architecture Shift Plan

This document explains how Phase 2 will shift the current settlement architecture from Thirdweb-based execution to a fully self-managed x402 execution stack.

Related roadmap phase:

- [roadmap.md](roadmap.md)

## 1. Why This Shift

Phase 2 is not only a dependency swap. It is a clarity shift toward client ownership.

Target outcome:

- Engine controls transaction building, signing flow, and execution lifecycle using **client-provided credentials**.
- Engine is fully independent of external SDKs; all execution is via ethers.js direct RPC calls.
- No Thirdweb in runtime, docs, secrets, or setup guidance.
- Existing caller experience and callback contract remain stable.
- Clear separation: engine is stateless orchestration; client owns all infrastructure (contracts, wallet, RPC).

## 2. Scope and Guardrails

In scope:

- Replace Thirdweb execution path with ethers.js JSON-RPC direct execution using client-provided credentials.
- Introduce internal x402 facilitator module for stateless execution orchestration.
- Keep caller command model and callback comment behavior unchanged.
- Ensure all infrastructure (RPC URL, private key, contract addresses) remain client-provided and client-owned.

Out of scope:

- Treasury model (Phase 3).
- Chain-agnostic multi-chain routing (Phase 4).
- CLI/action productization (Phase 5).
- Contract deployment or governance (client responsibility).

## 3. Current vs Target Architecture

### 3.1 Current (Before Phase 2)

```mermaid
flowchart LR
  subgraph CallerRepo[Caller Repo]
    PR[PR comment events]
    Trigger["/send parser + workflow trigger"]
  end

  subgraph ReusableRepo["x402_workflow Reusable Repo"]
    WF["x402-settlement.yml"]
    Script["sendScore.js"]
    SDK["Thirdweb SDK"]
  end

  Chain["(Monad RPC + Token Contract)"]

  PR --> Trigger --> WF --> Script --> SDK --> Chain
  WF --> Callback["PR callback comment"]
```

### 3.2 Target (After Phase 2)

```mermaid
flowchart LR
  subgraph CallerRepo[Caller Repo]
    PR[PR comment events]
    Trigger["/send parser + workflow trigger"]
  end

  subgraph ReusableRepo["x402_workflow Reusable Repo"]
    WF["x402-settlement.yml"]
    Fac["x402 Facilitator"]
    Val["Validation Layer"]
    Build["Tx Builder"]
    Sign["Signer Service"]
    Send["RPC Sender + Receipt Watcher"]
    CB["Callback Publisher"]
  end

  Chain["(EVM RPC + Token Contract)"]

  PR --> Trigger --> WF --> Fac
  Fac --> Val --> Build --> Sign --> Send --> Chain
  Fac --> CB --> PR
```

## 4. x402 Facilitator Design

The facilitator is the internal execution coordinator introduced in Phase 2.

Core responsibilities:

- Normalize and validate runtime inputs.
- Resolve chain + contract execution context.
- Build contract call payload with ethers Interface.
- Sign and submit transaction with private key wallet.
- Wait for confirmation and emit deterministic outputs.
- Publish callback result payload consumed by workflow comment step.

Suggested internal modules:

- `facilitator/context.js`: env and input normalization.
- `facilitator/validate.js`: address, amount, network guards.
- `facilitator/tx-builder.js`: ABI encode client-contract execution call (for example `disburse` or `transfer`).
- `facilitator/executor.js`: send/wait/retry with ethers provider.
- `facilitator/result.js`: `TX_HASH`, `EXPLORER_URL`, error classification.

Note: this aligns with the current JavaScript codebase. If TypeScript is adopted later, do it as a separate planned migration with build/tooling updates.

## 5. Workflow Contract Compatibility

The following must remain compatible during Phase 2:

- Caller workflow inputs to reusable workflow.
- Callback comment format (success and failure semantics).
- `TX_HASH` and `EXPLORER_URL` output keys.

This allows caller repos to migrate without behavior changes.

## 5.1 Runtime Security Modes

Execution is selected from client-provided configuration:

- If `TREASURY_CONTRACT` is provided: call treasury `disburse(recipient, amount)`.
- Else: call token contract transfer function.

Reference pattern:

```js
if (TREASURY_CONTRACT) {
  executeDisburse(recipient, amount);
} else {
  executeTransfer(recipient, amount);
}
```

This keeps existing client contracts usable while enabling an incremental security upgrade path.

## 5.2 Governance Layer Separation

- GitHub controls who can trigger execution (maintainer rights, PR checks, branch protection).
- Smart contracts control what execution is allowed (limits, pause, authorization).

The execution engine coordinates these layers but does not embed GitHub policy into contract logic.

## 6. Secrets and Setup Changes

### 6.1 Clarification: Client-Provided Credentials

These are **client-managed and owned**:

- `SERVER_WALLET`: private key of the operator account (fully client-controlled)
- `SCORE_TOKEN_CONTRACT`: address deployed and owned by client
- `RPC_URL`: client's chosen EVM chain endpoint
- `CALLBACK_GITHUB_TOKEN`: GitHub token for posting results (client-provided)

### 6.2 Remove (Thirdweb Dependency)

- Thirdweb secret references from workflows and docs.
- Thirdweb package dependencies from `package.json`.

### 6.3 Wallet Generation Guidance

Only these methods should appear in docs:

- `cast wallet new`
- ethers.js one-liner
- browser wallet

**No Thirdweb mention for wallet creation or management.**

## 7. Migration Plan (How the Shift Occurs)

```mermaid
flowchart TD
  A["Step 0: Baseline freeze + tests"] --> B["Step 1: Add facilitator modules behind feature flag"]
  B --> C["Step 2: Implement ethers transaction path"]
  C --> D["Step 3: Keep callback contract identical"]
  D --> E["Step 4: Run manual testnet settlements behind feature flag"]
  E --> F["Step 5: Remove Thirdweb deps and docs"]
  F --> G["Step 6: Full cutover + rollback guard retained"]
```

Detailed steps:

1. Baseline freeze

- Lock current behavior with golden integration tests.
- Capture expected comment payloads and output keys.

1. Parallel implementation

- Add facilitator path while retaining old path behind flag.
- Use explicit GitHub Actions control, for example workflow input or env variable:
  - `USE_FACILITATOR: true|false`
- Route settlement execution path using this value until full cutover.
- Validate output parity between both implementations.

1. Canary rollout

- Run 5 to 10 manual testnet settlements with `USE_FACILITATOR=true` before full cutover.
- Compare success rates, latency, and error classes.

1. Dependency removal

- Remove Thirdweb imports and packages.
- Remove Thirdweb docs and secret references.

1. Full cutover

- Set facilitator path as default.
- Keep temporary rollback flag for one release window.

## 8. Runtime Sequence (Target)

```mermaid
sequenceDiagram
  participant M as Maintainer
  participant CR as Caller Repo Workflow
  participant RR as Reusable Workflow
  participant F as x402 Facilitator
  participant RPC as EVM RPC
  participant GH as GitHub API

  M->>CR: /send amount
  CR->>CR: Permission + wallet resolution
  CR->>RR: workflow_call(inputs + secrets)
  RR->>F: executeSettlement(context)
  F->>F: validate + build tx
  F->>RPC: sendRawTransaction
  RPC-->>F: txHash + receipt
  F-->>RR: TX_HASH + EXPLORER_URL
  RR->>GH: post success/failure comment
```

## 9. Risks and Mitigations

Risk: nonce collisions under concurrent runs.

- Mitigation: fetch `pending` nonce at sign time and rely on chain-level nonce rules to reject replay/conflicts; avoid any external queue/server dependency.

Risk: RPC instability.

- Mitigation: retry policy, alternate RPC endpoint support, classified errors.

Risk: behavior drift in callback comments.

- Mitigation: snapshot tests for markdown payloads.

Risk: hidden Thirdweb references left in docs.

- Mitigation: CI lint check for forbidden keywords.

## 10. Definition of Done

Phase 2 is complete only when all are true:

- No Thirdweb dependency in source or package manifests.
- No Thirdweb mention in setup and wallet-generation docs.
- Testnet end-to-end runs pass with ethers-only path.
- Callback output contract unchanged for caller repos.
- Rollback plan documented and tested once.

## 11. Immediate Implementation Backlog

- Create facilitator module skeleton and interfaces.
- Refactor `src/settlement/sendScore.js` to delegate to facilitator.
- Replace Thirdweb calls with ethers provider/wallet/contract call.
- Add parity tests for success and failure callback payloads.
- Update docs and secrets sections across reusable and caller template docs.
