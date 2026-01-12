# File Reference

Complete reference for all files in this repository.

---

## `.github/workflows/`

### `x402-settlement.yml`

**Type**: Reusable GitHub Actions Workflow  
**Trigger**: `workflow_call` (called from other repositories)

**Purpose**: Production workflow for x402 score settlement. Designed to be called by external command-trigger systems.

**Inputs**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `repo_name` | string | ✓ | Repository name (owner/repo format) |
| `issue_number` | number | ✓ | GitHub issue number for tracking |
| `recipient_wallet` | string | ✓ | Ethereum address to receive tokens |
| `score_amount` | number | ✓ | Number of tokens to mint |
| `network` | string | ✓ | Target network (`monad-testnet` or `monad-mainnet`) |

**Secrets**:
| Name | Required | Description |
|------|----------|-------------|
| `THIRDWEB_SECRET_KEY` | ✓ | Thirdweb API authentication |
| `SERVER_WALLET` | ✓ | Private key with minter role |
| `SCORE_TOKEN_CONTRACT` | ✓ | Deployed ScoreToken address |
| `RPC_URL` | ✓ | Monad RPC endpoint |
| `GITHUB_TOKEN` | ✓ | For posting issue comments |

**Outputs**:

- Posts transaction confirmation comment to the specified issue
- Sets `TX_HASH` and `EXPLORER_URL` in `GITHUB_OUTPUT`

---

### `x402-settlement-demo.yml`

**Type**: GitHub Actions Workflow  
**Trigger**: `workflow_dispatch` (manual execution)

**Purpose**: Testing and demonstration workflow. Allows manual input of all parameters via GitHub Actions UI.

**Inputs** (via UI):
| Name | Default | Description |
|------|---------|-------------|
| `recipient_wallet` | `0xf39Fd6...` | Target wallet address |
| `score_amount` | `100` | Tokens to mint |
| `network` | `monad-testnet` | Target blockchain |
| `issue_number` | `1` | Reference issue |
| `repo_name` | `manashatwar/x402_workflow` | Repository reference |
| `server_wallet` | (required) | Private key input |
| `score_token_contract` | `0xFea986...` | Contract address |
| `rpc_url` | `https://testnet.monad.xyz` | RPC endpoint |

**Use Case**: Testing settlement flow without integrating with command-trigger system.

---

## `src/settlement/`

### `sendScore.js`

**Type**: Node.js ES Module  
**Runtime**: Node.js 20+

**Purpose**: Core settlement engine. Mints non-transferable ERC-20 tokens on Monad blockchain using Thirdweb SDK.

**Environment Variables**:
| Variable | Description |
|----------|-------------|
| `THIRDWEB_SECRET_KEY` | Thirdweb API secret key |
| `SERVER_WALLET` | Private key (hex, with or without 0x prefix) |
| `SCORE_TOKEN_CONTRACT` | Contract address |
| `RECIPIENT_WALLET` | Recipient address |
| `SCORE_AMOUNT` | Integer amount (multiplied by 10^18 internally) |
| `NETWORK` | `monad-testnet` or `monad-mainnet` |
| `ISSUE_NUMBER` | GitHub issue reference |
| `REPO_NAME` | Repository reference |

**Key Functions**:

| Function           | Description                                                    |
| ------------------ | -------------------------------------------------------------- |
| `validateEnv()`    | Validates all required environment variables                   |
| `getChainConfig()` | Returns Thirdweb chain config for specified network            |
| `getExplorerUrl()` | Constructs MonadVision explorer URL for transaction            |
| `main()`           | Entry point - orchestrates validation, transaction, and output |

**Dependencies**:

- `thirdweb` - Transaction signing, contract interaction, account management
- `ethers` - Address validation
- `fs` - Writing to `GITHUB_OUTPUT`

**Output**: Writes to `GITHUB_OUTPUT`:

```
TX_HASH=0x...
EXPLORER_URL=https://testnet.monadvision.com/tx/0x...
```

---

## `src/contracts/`

### `ScoreToken.abi.json`

**Type**: JSON ABI Definition

**Purpose**: Application Binary Interface for the deployed ScoreToken contract. Used by Thirdweb SDK to encode function calls.

**Key Functions in ABI**:
| Function | Signature | Description |
|----------|-----------|-------------|
| `mint` | `mint(address to, uint256 amount)` | Mints tokens to recipient |
| `burn` | `burn(address from, uint256 amount)` | Burns tokens (corrections) |
| `balanceOf` | `balanceOf(address account)` | Returns token balance |
| `hasRole` | `hasRole(bytes32 role, address account)` | Checks role assignment |

---

### `scoreToken.js`

**Type**: ES Module Export

**Purpose**: Exports the ABI JSON for use in other modules.

```javascript
import abiJson from "./ScoreToken.abi.json" assert { type: "json" };
export const SCORE_TOKEN_ABI = abiJson;
```

---

## `src/validation/`

### `addressValidator.js`

**Type**: ES Module Utility

**Purpose**: Validation utilities for Ethereum addresses and amounts.

**Exports**:

| Function                     | Parameters                           | Returns   | Description                                       |
| ---------------------------- | ------------------------------------ | --------- | ------------------------------------------------- |
| `isValidAddress`             | `address: string`                    | `boolean` | Validates 0x + 40 hex chars format                |
| `validateAndChecksumAddress` | `address: string`                    | `string`  | Validates and returns address (throws on invalid) |
| `isValidAmount`              | `amount: number, maxAmount?: number` | `boolean` | Validates positive finite number within bounds    |

---

## `config/`

### `chainConfig.js`

**Type**: ES Module Configuration

**Purpose**: Network configuration for Monad testnet and mainnet.

**Exports**:

| Export                                    | Type       | Description                                  |
| ----------------------------------------- | ---------- | -------------------------------------------- |
| `chainConfig`                             | `object`   | Map of network configs keyed by network name |
| `getChainConfig(network)`                 | `function` | Returns config for specified network         |
| `getExplorerTxUrl(txHash, network)`       | `function` | Returns explorer URL for transaction         |
| `getExplorerAddressUrl(address, network)` | `function` | Returns explorer URL for address             |

**Network Properties**:

```javascript
{
  chainId: 10143,
  name: "Monad Testnet",
  rpcUrl: "https://testnet.monad.xyz",
  explorerUrl: "https://testnet.monadvision.com",
  nativeCurrency: { name: "MON", symbol: "MON", decimals: 18 },
  features: { tps: 10000, blockTime: "0.4s", finality: "single-slot" }
}
```

---

## Root Files

### `package.json`

**Purpose**: Node.js project configuration.

**Scripts**:
| Script | Command | Description |
|--------|---------|-------------|
| `settle` | `node src/settlement/sendScore.js` | Execute settlement locally |
| `test` | `jest` | Run test suite |

**Key Dependencies**:
| Package | Version | Purpose |
|---------|---------|---------|
| `thirdweb` | `^5.79.0` | Blockchain interaction |
| `ethers` | `^6.13.4` | Address validation |
| `dotenv` | `^17.2.3` | Environment loading |
| `@octokit/rest` | `^21.0.2` | GitHub API |

---

### `.gitignore`

**Purpose**: Excludes from version control:

- `node_modules/` - Dependencies
- `.env*` - Environment files (secrets)
- `*.log` - Log files
- `.DS_Store` - macOS metadata

---

### `README.md`

**Purpose**: Project overview, setup instructions, and usage examples.
