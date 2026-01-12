# Deployment Guide

## Prerequisites

- Node.js 20 or higher
- npm 9 or higher
- Deployed ScoreToken contract on Monad
- Thirdweb account with API key
- Wallet with MON for gas fees

---

## Contract Requirements

The ScoreToken contract must implement:

```solidity
interface IScoreToken {
    function mint(address to, uint256 amount) external;
    function burn(address from, uint256 amount) external;
    function balanceOf(address account) external view returns (uint256);
    function hasRole(bytes32 role, address account) external view returns (bool);
    function grantRole(bytes32 role, address account) external;
}
```

**Critical**: The wallet used as `SERVER_WALLET` must have the minter role granted:

```solidity
bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
scoreToken.grantRole(MINTER_ROLE, serverWalletAddress);
```

---

## Step 1: Repository Setup

Fork or clone this repository:

```bash
git clone https://github.com/manashatwar/x402_workflow.git
cd x402_workflow
npm install
```

---

## Step 2: Thirdweb Configuration

1. Create account at https://thirdweb.com
2. Navigate to **Dashboard** → **Settings** → **API Keys**
3. Create new API key with **Backend** scope
4. Copy the **Secret Key** (starts with `RZF...` or similar)

---

## Step 3: GitHub Secrets

Navigate to your repository:
**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add the following secret:

| Name                  | Value    | Description             |
| --------------------- | -------- | ----------------------- |
| `THIRDWEB_SECRET_KEY` | `RZF...` | From Thirdweb dashboard |

---

## Step 4: Test with Demo Workflow

1. Go to **Actions** tab
2. Select **x402 Settlement Demo**
3. Click **Run workflow**
4. Enter test parameters:
   - Recipient: Your test wallet address
   - Amount: `1` (small test amount)
   - Network: `monad-testnet`
   - Server wallet: Your private key with minter role
   - Contract: Your deployed ScoreToken address
   - RPC URL: `https://testnet.monad.xyz`
5. Click **Run workflow**
6. Monitor execution in Actions tab
7. Verify transaction on MonadVision explorer

---

## Step 5: Production Integration

Configure the calling repository with required secrets:

```yaml
# In calling repository's workflow
jobs:
  settle-score:
    uses: manashatwar/x402_workflow/.github/workflows/x402-settlement.yml@main
    with:
      repo_name: ${{ github.repository }}
      issue_number: ${{ github.event.issue.number }}
      recipient_wallet: ${{ steps.parse.outputs.wallet }}
      score_amount: ${{ steps.parse.outputs.amount }}
      network: "monad-testnet"
    secrets:
      THIRDWEB_SECRET_KEY: ${{ secrets.THIRDWEB_SECRET_KEY }}
      SERVER_WALLET: ${{ secrets.SERVER_WALLET }}
      SCORE_TOKEN_CONTRACT: ${{ secrets.SCORE_TOKEN_CONTRACT }}
      RPC_URL: ${{ secrets.RPC_URL }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Mainnet Deployment

When ready for production:

1. Deploy ScoreToken to Monad mainnet
2. Grant minter role to production wallet
3. Update secrets:
   - `SCORE_TOKEN_CONTRACT` → mainnet address
   - `RPC_URL` → `https://rpc.monad.xyz`
   - `SERVER_WALLET` → production wallet key
4. Change workflow input: `network: "monad-mainnet"`

---

## Troubleshooting

### Error: Missing required environment variables

Ensure all secrets are configured in GitHub repository settings.

### Error: Invalid address format

Addresses must be checksummed 42-character hex strings starting with `0x`.

### Error: Execution reverted

- Verify `SERVER_WALLET` has minter role on the contract
- Check wallet has sufficient MON for gas
- Confirm contract address is correct for the network

### Error: Thirdweb authentication failed

- Verify `THIRDWEB_SECRET_KEY` is the **Secret Key**, not Client ID
- Ensure API key has Backend scope enabled

### Transaction not visible on explorer

- Wait 1-2 blocks for indexer to process
- Verify correct explorer URL (testnet vs mainnet)
