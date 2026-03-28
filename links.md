# x402 Research Mapping for Roadmap

## Phase 1 - Stability and Hardening

### Core links
- [Payment Identifier](https://docs.x402.org/extensions/payment-identifier) - idempotency key support for retry-safe payments and deduplication.
- [Lifecycle Hooks](https://docs.x402.org/advanced-concepts/lifecycle-hooks) - intercept verification and settlement steps for observability and failure handling.
- [Facilitator](https://docs.x402.org/core-concepts/facilitator) - explains verification and settlement responsibilities and guarantees.

### Direct references (critical)
- [x402 Whitepaper](https://www.x402.org/x402-whitepaper.pdf) - protocol vision, lifecycle framing, and design rationale.
- [x402 Specification v2](https://github.com/coinbase/x402/blob/main/specs/x402-specification-v2.md) - canonical protocol behavior and response structure.
- [EIP-712](https://eips.ethereum.org/EIPS/eip-712) - typed signing standard used for signature verification and replay-safe domains.

### Supports
- retry safety
- callback correctness
- failure classification system

## Phase 2 - Remove Thirdweb

### Core links
- [Wallet](https://docs.x402.org/core-concepts/wallet) - wallet model and signing responsibilities in x402 flows.
- [Quickstart for Buyers](https://docs.x402.org/getting-started/quickstart-for-buyers) - practical buyer-side setup using direct wallet and RPC tooling.

### Direct references (execution layer)
- [ethers.js v6 docs](https://docs.ethers.org/v6/) - low-level provider, signer, and contract interaction APIs.
- [viem docs](https://viem.sh/docs/getting-started) - typed RPC client stack for direct wallet and chain interactions.

### Focus
- direct RPC control
- removing abstraction layer (Thirdweb)

## Phase 3 - Treasury Contract

### Core links
- [EIP-2612 Gas Sponsoring](https://docs.x402.org/extensions/eip2612-gas-sponsoring) - permit-based approval and sponsored execution flow.
- [ERC20 Approval Gas Sponsoring](https://docs.x402.org/extensions/erc20-approval-gas-sponsoring) - approval-then-transfer sponsorship path for ERC-20 payments.

### Direct references (essential standards)
- [EIP-2612](https://eips.ethereum.org/EIPS/eip-2612) - permit-based gasless approvals for ERC-20 allowances.
- [EIP-3009](https://eips.ethereum.org/EIPS/eip-3009) - transfer-with-authorization pattern for signature-based token transfers.

### Focus
- gasless approvals
- pre-funded treasury disbursement
- no mint dependency

## Phase 4 - Chain-Agnostic and Multi-Token

### Core links
- [Network and Token Support](https://docs.x402.org/core-concepts/network-and-token-support) - supported chains/tokens and chain identifier model.
- [Quickstart for Sellers](https://docs.x402.org/getting-started/quickstart-for-sellers) - seller integration pattern across supported networks.

### Direct references (architecture standard)
- [CAIP-2](https://standards.chainagnostic.org/CAIPs/caip-2) - chain identifier standard for multi-network abstraction and config portability.

### Focus
- chain abstraction layer
- dynamic config (RPC, chainId, token)

## Phase 5 - CLI and Reusable Action

### Core links
- [SDK Features](https://docs.x402.org/sdk-features) - capability matrix and core SDK building blocks.
- [MCP Server with x402](https://docs.x402.org/guides/mcp-server-with-x402) - reusable integration pattern for tool and workflow automation.
- [Extensions Overview](https://docs.x402.org/extensions/overview) - extension catalog and composability model.

### Direct references (real integrations)
- [x402 V2 launch](https://www.x402.org/writing/x402-v2-launch) - production-oriented lifecycle hooks, extension model, and modular SDK direction.
- [Stripe x402 machine payments](https://docs.stripe.com/payments/machine/x402) - concrete server-facilitator flow for real-world M2M payment integration.

### Focus
- reusable action abstraction
- CLI and workflow unification

## Phase 6 - Policy Engine

### Core links
- [Lifecycle Hooks](https://docs.x402.org/advanced-concepts/lifecycle-hooks) - hook points for policy checks and decision gating.
- [Extensions Overview](https://docs.x402.org/extensions/overview) - extension architecture for injecting custom policy behavior.

### Direct references
- [Elixir x402 SDK docs](https://hexdocs.pm/x402/readme.html) - concrete lifecycle hook and middleware implementation examples.

### Focus
- rule-based gating
- hook-driven evaluation system

## Phase 7 - Multi-Contributor and Split Payouts

### Core links
- [Payment Identifier](https://docs.x402.org/extensions/payment-identifier) - unique identifiers for per-recipient tracking and retry-safe batching.

### Direct references (conceptual support)
- [OpenZeppelin PaymentSplitter](https://docs.openzeppelin.com/contracts/4.x/api/finance#PaymentSplitter) - pull-based payout splitting pattern for multi-recipient disbursement.
- [Stripe separate charges and transfers](https://docs.stripe.com/connect/separate-charges-and-transfers) - production split-transfer design with partial transfer and reversal handling.

### Focus
- batching
- per-recipient tracking
- partial failure handling

## Phase 8 - Web2 Settlement and Dashboard

### Core links
- [HTTP 402](https://docs.x402.org/core-concepts/http-402) - explains the protocol's web-native payment signaling model.
- [Introduction](https://docs.x402.org/introduction) - high-level architecture and end-to-end transaction context.
- [FAQ](https://docs.x402.org/faq) - common operational and adoption questions, including roadmap context.

### Direct references (very important)
- [Bazaar (Discovery Layer)](https://docs.x402.org/extensions/bazaar) - discovery and cataloging model for payable resources and MCP tools.
- [x402 Bazaar launch post](https://www.coinbase.com/developer-platform/discover/launches/x402-bazaar) - launch context and real discovery use cases.
- [IQ.wiki x402 deep dive](https://iq.wiki/wiki/x402) - ecosystem and architecture summary with references.
- [HTTP 402 Payment Required (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402) - standard status reference and compatibility context.

### Focus
- web2 and web3 bridge
- discovery and reputation layer

## Cross-phase references
- [Migration v1 to v2](https://docs.x402.org/guides/migration-v1-to-v2)
- [Offer Receipt](https://docs.x402.org/extensions/offer-receipt)

## Quick links
- [Network and Token Support](https://docs.x402.org/core-concepts/network-and-token-support)
- [Payment Identifier and Idempotency](https://docs.x402.org/extensions/payment-identifier)
- [Lifecycle Hooks](https://docs.x402.org/advanced-concepts/lifecycle-hooks)
