# x402 Score Settlement

Blockchain settlement engine for GitHub contributor recognition on Monad.

## Overview

Mints non-transferable ERC-20 tokens to contributor wallets as immutable proof of contribution. Built for integration with GitHub Actions command-trigger workflows.

## Quick Start

```bash
npm install
```

Configure `THIRDWEB_SECRET_KEY` in GitHub repository secrets, then run the demo workflow from the Actions tab.

## Project Structure

```
.github/workflows/
├── x402-settlement.yml       # Reusable workflow (production)
└── x402-settlement-demo.yml  # Manual trigger (testing)

src/
├── settlement/
│   └── sendScore.js          # Settlement engine
├── contracts/
│   ├── ScoreToken.abi.json   # Contract ABI
│   └── scoreToken.js         # ABI export
└── validation/
    └── addressValidator.js   # Validation utilities

config/
└── chainConfig.js            # Network configurations

web-app/
├── index.html                # Web interface for triggering settlements
└── README.md                 # Deployment guide for GitHub Pages

caller-repo-template/
└── .github/workflows/
    └── pr-x402-trigger.yml   # Template for repos using x402

docs/
├── ARCHITECTURE.md           # System design
├── FILE_REFERENCE.md         # File documentation
├── WORKFLOWS.md              # Workflow reference
└── DEPLOYMENT.md             # Setup guide
```

## 🌐 Web Interface

Deploy a web UI to trigger settlements: [web-app/README.md](web-app/README.md)

## Documentation

| Document                                 | Description                       |
| ---------------------------------------- | --------------------------------- |
| [Architecture](docs/ARCHITECTURE.md)     | System design and data flow       |
| [File Reference](docs/FILE_REFERENCE.md) | Detailed file documentation       |
| [Workflows](docs/WORKFLOWS.md)           | GitHub Actions workflow guide     |
| [Deployment](docs/DEPLOYMENT.md)         | Setup and deployment instructions |

## Usage

### Demo (Manual Testing)

1. Add `THIRDWEB_SECRET_KEY` to repository secrets
2. Go to Actions → x402 Settlement Demo → Run workflow
3. Enter parameters and execute

### Production (Reusable Workflow)

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

## Networks

| Network       | Chain ID | Explorer                        |
| ------------- | -------- | ------------------------------- |
| Monad Testnet | 10143    | https://testnet.monadvision.com |
| Monad Mainnet | 41454    | https://monadvision.com         |

## Dependencies

| Package  | Purpose                         |
| -------- | ------------------------------- |
| thirdweb | Blockchain transaction handling |
| ethers   | Address validation              |

## License

MIT
