# x402 Workflow (Reusable Settlement Engine)

Reusable GitHub Actions + Node.js settlement engine that mints SCORE tokens on Monad.

This repository is the settlement side of a two-repo system:

1. Caller repository: collects PR wallet and maintainer command.
2. This repository: validates inputs, executes mint transaction, reports result.

## Repository Responsibility

This repo owns:

- Settlement transaction logic
- Reusable and demo workflows
- Chain and contract integration details
- Core validation utilities

This repo does not own:

- PR comment UX in consumer repositories
- Maintainer reward policy (/send amount scale)
- Caller-side onboarding docs

Caller template docs live in [caller-repo-template/README.md](https://github.com/kpj2006/caller-repo-template/blob/main/README.md).

## Quick Start

```bash
npm install
```

Then configure secrets and run manual test workflow as described in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Reusable Workflow Usage

```yaml
jobs:
  settle:
    uses: manashatwar/x402_workflow/.github/workflows/x402-settlement.yml@main
    with:
      repo_name: ${{ github.repository }}
      issue_number: 42
      recipient_wallet: "0x..."
      score_amount: 100
      network: "monad-testnet"
    secrets:
      THIRDWEB_SECRET_KEY: ${{ secrets.THIRDWEB_SECRET_KEY }}
      SERVER_WALLET: ${{ secrets.SERVER_WALLET }}
      SCORE_TOKEN_CONTRACT: ${{ secrets.SCORE_TOKEN_CONTRACT }}
      RPC_URL: ${{ secrets.RPC_URL }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Documentation Map

- [docs/README.md](docs/README.md): documentation index and ownership boundaries
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): system flow and repo handoff points
- [docs/WORKFLOWS.md](docs/WORKFLOWS.md): workflow contract and inputs/outputs
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md): setup and operations for this reusable repo
- [docs/FILE_REFERENCE.md](docs/FILE_REFERENCE.md): source file responsibilities

## Related Repository

- Caller template (consumer repo side):
  [kpj2006/caller-repo-template](https://github.com/kpj2006/caller-repo-template)

## Cross-Repo GitHub Links

- Caller template repo: [https://github.com/kpj2006/caller-repo-template.git](https://github.com/kpj2006/caller-repo-template.git)
- Reusable engine repo: [https://github.com/manashatwar/x402_workflow.git](https://github.com/manashatwar/x402_workflow.git)

Use caller-side guides for PR interaction and maintainer command flow.

## License

MIT
