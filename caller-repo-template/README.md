# 🎉 PR x402 Settlement - Caller Repository Template

This repository template automatically rewards Pull Request authors with non-transferable SCORE tokens on Monad blockchain using the x402 settlement system.

## 🌟 Features

- **Automatic PR Welcome**: Sends a congratulations message when a PR is opened
- **Wallet Collection**: Prompts PR authors to submit their MetaMask wallet address
- **Maintainer-Controlled Settlement**: Maintainers use `/send <amount>` to trigger token rewards
- **Flexible Amounts**: Maintainers decide token amount based on contribution quality
- **Real-time Updates**: Posts transaction details back to the PR

## 📋 Prerequisites

Before setting up this repository, you need:

1. **x402_workflow Repository**: A deployed instance of the x402_workflow repository (the settlement engine)
2. **GitHub Personal Access Token**: With `workflow` permissions to trigger workflows in the x402_workflow repo
3. **Monad Network Setup**: 
   - Server wallet private key (funded with MON for gas)
   - Deployed ScoreToken contract address
   - Monad RPC URL (testnet or mainnet)

## 🚀 Setup Instructions

### Step 1: Use This Template

1. Click "Use this template" or copy the `.github/workflows` folder to your repository
2. Ensure the workflow file is at: `.github/workflows/pr-x402-trigger.yml`

### Step 2: Configure x402 Workflow Repository

Edit `.github/workflows/pr-x402-trigger.yml` and update these values:

```yaml
X402_REPO_OWNER: 'manashatwar'  # Change to your x402_workflow repo owner
X402_REPO_NAME: 'x402_workflow'  # Change to your x402_workflow repo name
```

Also update the `ref` to match your default branch (line ~133):

```yaml
ref: 'main',  # Change to 'master' or your default branch name
```

### Step 3: Configure Repository Secrets

Go to your repository **Settings → Secrets and variables → Actions** and add these secrets:

#### Required Secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `X402_WORKFLOW_TOKEN` | GitHub Personal Access Token with `workflow` scope | `ghp_xxxxxxxxxxxx` |
| `X402_SERVER_WALLET` | Private key of server wallet (with 0x prefix) | `0x1234...abcd` |
| `X402_SCORE_TOKEN_CONTRACT` | Deployed ScoreToken contract address | `0xFea9...B3C3` |
| `X402_RPC_URL` | Monad RPC endpoint URL | `https://testnet.monad.xyz` |

#### How to Create Personal Access Token:

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "x402-workflow-trigger"
4. Select scopes: `repo` and `workflow`
5. Generate and copy the token
6. Add it as `X402_WORKFLOW_TOKEN` secret in your repository

### Step 4: Verify x402_workflow Repository Setup

Ensure your x402_workflow repository has:

1. The workflow file at: `.github/workflows/x402-settlement-demo.yml`
2. All required secrets configured:
   - `THIRDWEB_SECRET_KEY`
   - `GITHUB_TOKEN` (usually automatic)

The updated x402-settlement-demo.yml now includes callback functionality to post results back to the calling repository!

### Step 5: Test the Setup

1. Create a test PR in your repository
2. You should see a welcome message automatically posted
3. Comment with: `x402-wallet: 0xYourWalletAddress`
4. The workflow should trigger and post settlement results

## 📖 How It Works

### Flow Diagram (fr detailed one check inn docs)

```
1. PR Opened
   ↓
2. Welcome Message Posted (asking for wallet)
   ↓
3. PR Author Comments with Wallet Address
   ↓
4. Wallet Saved (no execution yet)
   ↓
5. Maintainer Reviews PR
   ↓
6. Maintainer Comments: /send <amount>
   ↓
7. Permission Check (maintainer only)
   ↓
8. Retrieve Stored Wallet Address
   ↓
9. Trigger x402-settlement-demo.yml in x402_workflow repo
   ↓
10. Settlement Executes (mints tokens on Monad)
   ↓
11. Success/Failure Posted Back to PR
```

### Workflow Triggers

**pr-x402-trigger.yml** has three jobs:

1. **welcome_message**: Runs when PR is opened/reopened
2. **store_wallet**: Runs when PR author comments with wallet address (stores it)
3. **maintainer_send**: Runs when maintainer comments `/send <amount>` (executes settlement)

## 🎨 Customization

### Change Token Amount

Edit `pr-x402-trigger.yml` line ~121:

```yaml
score_amount: '100',  # Change to desired amount
```

### Change Network

Edit `pr-x402-trigger.yml` line ~122:

```yaml
network: 'monad-testnet',  # or 'monad-mainnet'
```

### Customize Messages

The welcome message and response messages can be customized in the `pr-x402-trigger.yml` file under the respective `body:` sections.

## 🔧 Troubleshooting

### PR Author Comments but Nothing Happens

**Check:**
- Is the comment author the same as the PR author? (Only PR author can trigger settlement)
- Does the comment contain `x402-wallet: 0x...` in the correct format?
- Are the repository secrets configured correctly?

### "Failed to trigger workflow" Error

**Common causes:**
1. `X402_WORKFLOW_TOKEN` doesn't have `workflow` scope
2. Wrong `X402_REPO_OWNER` or `X402_REPO_NAME` 
3. x402_workflow repository doesn't have `x402-settlement-demo.yml` file
4. Wrong default branch name in the `ref:` field

### Settlement Workflow Runs but Fails

**Check x402_workflow repository:**
1. Are all secrets configured? (`THIRDWEB_SECRET_KEY`, etc.)
2. Is the server wallet funded with MON for gas?
3. Is the ScoreToken contract address correct?
4. Check the workflow logs in x402_workflow repository

## 📚 Wallet Address Format

Users must comment in this exact format:

```
x402-wallet: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
```

**Requirements:**
- Must start with `0x`
- Followed by exactly 40 hexadecimal characters (0-9, a-f, A-F)
- Case-insensitive

**Invalid formats:**
- ❌ `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb9226` (39 chars)
- ❌ `f39Fd6e51aad88F6F4ce6aB8827279cffFb92266` (no 0x)
- ❌ `My wallet: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266` (extra text before)

**Valid formats:**
- ✅ `x402-wallet: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`
- ✅ `x402-wallet:0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266` (no space)
- ✅ `x402-wallet: 0xF39FD6E51AAD88F6F4CE6AB8827279CFFFB92266` (uppercase)


