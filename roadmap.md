# x402 Workflow Roadmap

This roadmap defines the evolution path for the x402 settlement system across caller and reusable repos.

Current baseline:

- Cross-repo PR-triggered settlement is working.
- Caller workflow handles wallet collection and maintainer trigger.
- Reusable workflow executes on-chain settlement and callback comments.

## Phase 1: Stability and Hardening

Goal:

- Make the current system production-stable before feature expansion.

Scope:

- Workflow reliability, retries, idempotency, and error messages.
- Better observability (run metadata, structured logs, failure classification).
- Security review of tokens/secrets and permission boundaries.
- Regression tests for: wallet parsing, maintainer permission checks, callback posting.

Deliverables:

- Stability checklist and runbook.
- Integration test matrix for caller + reusable workflows.
- Standardized incident triage guide.

Exit criteria:

- Success rate target met over rolling runs.
- Known failure types documented with resolution steps.
- No critical security findings open.

## Phase 2: Remove Thirdweb Dependency

Goal:

- Remove Thirdweb completely from settlement execution.

Required direction:

- Thirdweb is not used or mentioned for wallet generation.
- Setup guidance only uses:

  - `cast wallet new`
  - ethers.js one-liner
  - browser wallet

Scope:

- Replace Thirdweb transaction path in settlement engine with direct ethers.js JSON-RPC flow.
- Update docs, examples, and workflow secrets to remove Thirdweb references.
- Keep existing behavior and callback contract unchanged.

Deliverables:

- Refactored settlement script without Thirdweb imports.
- Updated docs and workflow interfaces.
- Migration note for existing users.

Exit criteria:

- Thirdweb dependency removed from `package.json` and source.
- End-to-end settlement works on testnet with ethers.js only.

## Phase 3: Treasury Contract Model (Pre-Funded Pool)

Goal:

- Move from mint-on-demand to treasury-based token distribution.

Scope:

- Introduce treasury contract funded in advance.
- CI/CD distributes from treasury pool instead of calling mint each time.
- Add safeguards: balance checks, allowance checks, and payout limits.

Deliverables:

- Treasury contract specification and deployment guide.
- Reusable workflow updated for transfer/disbursement mode.
- Emergency pause and treasury refill SOP.

Exit criteria:

- Settlements execute without mint role dependency.
- Treasury accounting and audit trail are verifiable.

## Phase 4: Chain-Agnostic and Multi-Token

Goal:

- Support any EVM chain and multiple token contracts.

Scope:

- Chain-agnostic config via workflow inputs (RPC, chainId, explorer, symbol).
- Multi-token support by repo, label, or contribution type.
- Validation layer for chain/token compatibility.

Deliverables:

- Unified chain config schema.
- Token routing policy map.
- Backward-compatible defaults for current Monad flows.

Exit criteria:

- Same reusable workflow runs on multiple EVM networks.
- Multiple token payouts supported in one org setup.

## Phase 5: x402 CI/CD Reusable Action + CLI + Chat UX

Goal:

- Provide a first-class reusable automation interface.

Scope:

- Publish reusable action style interface.
- Introduce CLI command:

```bash
x402 pay --to wallet 0x... --amount 100 --chain monad
```

- Support GitHub comment/chat command style:

```text
/send 0x... 10usdc monad
```

- Keep simple action usage in workflows:

```yaml
- uses: x402/pay@v1
  with:
    recipient: ${{ steps.wallet.outputs.addr }}
    score_amount: ${{ fromJSON(needs.maintainer_send.outputs.score_amount) }}
    network: monad-testnet
  secrets: inherit
```

Deliverables:

- `x402/pay@v1` reusable action/reusable workflow contract.
- CLI package and command docs.
- Command parser spec for GitHub comments.

Exit criteria:

- Teams can integrate payouts with one action step.
- CLI and comment command both resolve to the same payout engine.

## Phase 6: Policy Engine

Goal:

- Add declarative payment rules controlled by admins.

Scope:

- Policy gates such as:

  - tests passed
  - PR merged
  - maintainer approved
  - coverage > 80%

Example direction:

```yaml
- uses: x402/pay@v1/test-passed
  needs: test
  with:
    recipient: ${{ steps.wallet.outputs.addr }}
    score_amount: ${{ fromJSON(needs.maintainer_send.outputs.score_amount) }}
    network: monad-testnet
  secrets: inherit
```

Deliverables:

- Policy DSL/schema.
- Policy evaluator in workflow runtime.
- Admin docs for rule management and overrides.

Exit criteria:

- Payouts are blocked unless policies pass.
- Policy decisions are visible in logs/comments.

## Phase 7: Multi-Contributor and Split Payouts

Goal:

- Support multiple recipients and different amounts in one PR context.

Scope:

- Parse and execute multiple `/send` lines safely.
- Recipient-explicit command support.
- Batch settlement with partial-failure reporting.

Example target usage:

```text
@alice /send 0x... 30 usdc monad
@bob /send 0x... 40 usdc monad
@charlie /send 0x... 50 usdc monad
```

Deliverables:

- Multi-recipient parser and validator.
- Batch payout execution strategy.
- Clear PR comment summary per recipient.

Exit criteria:

- One maintainer action can settle multiple contributors.
- Failures do not hide successful payouts.

## Phase 8: Web2 Settlement + Reputation Dashboard

Goal:

- Expand beyond crypto-native contributors and improve visibility.

Scope:

- Web2 settlement/offramp via x402 HTTP payments for non-crypto users.
- Reputation dashboard reading on-chain scores and showing org-level contributor views.

Deliverables:

- Offramp integration architecture.
- Contributor identity mapping model.
- Dashboard service and UI MVP.

Exit criteria:

- Non-wallet contributors can receive value through Web2 rails.
- Org can view contributor score trends and payout history.

## Cross-Phase Program Requirements

- Backward compatibility for existing caller repos where possible.
- Security review before each major phase rollout.
- Versioned migration guides for workflow/action interface changes.
- Feature flags for controlled rollout and rollback.

## Suggested Delivery Rhythm

- Phase 1: 2 to 3 sprints
- Phase 2 to 4: 1 to 2 sprints each
- Phase 5 to 8: 2+ sprints each (parallel tracks possible)

## Ownership Suggestion

- Reusable repo team: settlement engine, action/CLI, policy engine core.
- Caller template team: command UX, maintainer workflows, docs for adopters.
- Shared: chain config standards, security, migration tooling.
