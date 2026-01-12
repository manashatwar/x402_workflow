# Workflows Reference

## Overview

This repository provides two GitHub Actions workflows for x402 score settlement.

| Workflow             | File                       | Trigger             | Purpose                          |
| -------------------- | -------------------------- | ------------------- | -------------------------------- |
| x402 Settlement      | `x402-settlement.yml`      | `workflow_call`     | Production use by external repos |
| x402 Settlement Demo | `x402-settlement-demo.yml` | `workflow_dispatch` | Manual testing                   |

---

## x402-settlement.yml

### Description

Reusable workflow designed to be called from command-trigger repositories. Executes the complete settlement flow and posts results back to GitHub issues.

### Usage

Call from another repository's workflow:

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

### Workflow Steps

1. **Checkout** - Clones this repository
2. **Setup Node.js** - Installs Node.js 20 with npm cache
3. **Install dependencies** - Runs `npm ci`
4. **Validate wallet address** - Checks recipient address format
5. **Validate contract address** - Checks contract address format
6. **Execute settlement** - Runs `sendScore.js`
7. **Post success comment** - Comments on GitHub issue with transaction details
8. **Post error notification** - Comments on failure (if applicable)

### Outputs

On success, posts a GitHub comment:

```
✅ x402 Settlement Complete

• Amount: 100 tokens
• Network: monad-testnet
• Recipient: 0x...
• Transaction: 0x...

View on Explorer
```

---

## x402-settlement-demo.yml

### Description

Manual-trigger workflow for testing the settlement flow. All parameters are entered via the GitHub Actions UI.

### Usage

1. Navigate to **Actions** tab in repository
2. Select **x402 Settlement Demo** workflow
3. Click **Run workflow**
4. Fill in required parameters
5. Click **Run workflow** button

### Input Fields

| Field                        | Type     | Required | Description                   |
| ---------------------------- | -------- | -------- | ----------------------------- |
| Recipient wallet address     | Text     | ✓        | Ethereum address (0x...)      |
| Amount of tokens to mint     | Text     | ✓        | Integer value                 |
| Network to deploy to         | Dropdown | ✓        | monad-testnet / monad-mainnet |
| GitHub issue number          | Text     | ✓        | Reference issue               |
| Repository name              | Text     | ✓        | Format: owner/repo            |
| Server wallet private key    | Text     | ✓        | Hex private key (0x...)       |
| Score token contract address | Text     | ✓        | Deployed contract             |
| Monad RPC URL                | Text     | ✓        | Network RPC endpoint          |

### Secrets Required

Only one secret needs to be configured in repository settings:

| Secret                | Description             |
| --------------------- | ----------------------- |
| `THIRDWEB_SECRET_KEY` | Thirdweb API secret key |

All other values are entered manually per workflow run.

### Output

Logs transaction details to workflow output:

```
✅ x402 Settlement Completed Successfully!

Network: monad-testnet
Amount: 100 tokens
Recipient: 0x...
Repository: manashatwar/x402_workflow
Issue: #1

--- Transaction Details ---
Transaction Hash: 0x...
Explorer: https://testnet.monadvision.com/tx/0x...
```

---

## Workflow Comparison

| Feature       | x402-settlement.yml   | x402-settlement-demo.yml |
| ------------- | --------------------- | ------------------------ |
| Trigger       | Called by other repos | Manual dispatch          |
| Inputs        | Passed via `with:`    | Entered in UI            |
| Secrets       | Passed via `secrets:` | From repo settings + UI  |
| Issue Comment | Posts automatically   | No comment posted        |
| Use Case      | Production automation | Development testing      |
