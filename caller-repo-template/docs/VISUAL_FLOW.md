### Phase 1: PR Creation 

```
Contributor                 GitHub                      pr-x402-trigger.yml
     |                         |                               |
     |─── Opens PR ──────────→ |                               |
     |                         |─── Triggers workflow ────────→|
     |                         |                               |
     |                         |                        [welcome_message job]
     |                         |                               |
     |                         |                        Compose message
     |                         |                               |
     |←─ Welcome message ──────|←─── Post comment ────────────|
     |                         |                               |
```

### Phase 2: Wallet Submission 

```
Contributor                 GitHub                      pr-x402-trigger.yml
     |                         |                               |
     |─ Comments wallet ──────→|                               |
     |   "x402-wallet: 0x..."  |                               |
     |                         |─── Triggers workflow ────────→|
     |                         |                               |
     |                         |                    [trigger_settlement job]
     |                         |                               |
     |                         |                        Extract address
     |                         |                        Validate format
     |                         |                               |
     |←─ Acknowledgment ───────|←─── Post comment ────────────|
     |   "Wallet received!"    |                               |
```

### Phase 3: Settlement Trigger 

```
pr-x402-trigger.yml         GitHub API              x402_workflow
       |                        |                         |
       |─── dispatch_workflow ─→|                         |
       |    (with inputs)        |                         |
       |                         |─── Trigger ────────────→|
       |                         |                         |
       |                         |           [x402-settlement-demo.yml]
       |                         |                         |
       |                         |                    Starts running
```

### Phase 4: Token Minting 

```
x402-settlement-demo.yml    sendScore.js           Monad Blockchain
         |                       |                         |
         |─── Execute ──────────→|                         |
         |                       |                         |
         |                  Connect wallet                 |
         |                  Load contract                  |
         |                       |                         |
         |                       |─── mint() ─────────────→|
         |                       |    (recipient, amount)  |
         |                       |                         |
         |                       |                    Process TX
         |                       |                    Mint tokens
         |                       |                         |
         |                       |←─── TX Hash ────────────|
         |                       |                         |
         |←─── Return hash ──────|                         |
```

### Phase 5: Callback 

```
x402-settlement-demo.yml    GitHub API              Contributor's PR
         |                       |                         |
         |─── Post comment ─────→|                         |
         |    (with TX details)   |                         |
         |                        |─── Update ─────────────→|
         |                        |                         |
         |                        |                   Shows success
         |                        |                   with TX hash
```

## 🔄 Data Flow

```
User Input:
  "x402-wallet: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
                │
                ↓
  Regex Extraction:
    /x402-wallet:\s*(0x[a-fA-F0-9]{40})/i
                │
                ↓
  Extracted Address:
    "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
                │
                ↓
  Format Validation:
    /^0x[a-fA-F0-9]{40}$/
                │ ✓ Valid
                ↓
  Workflow Dispatch Inputs:
    {
      recipient_wallet: "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
      score_amount: "100",
      network: "monad-testnet",
      issue_number: "42",
      repo_name: "user/project",
      server_wallet: "***",
      score_token_contract: "0xFea9...",
      rpc_url: "https://testnet.monad.xyz"
    }
                │
                ↓
  sendScore.js Execution:
    - Connect to RPC
    - Initialize wallet
    - Load contract
    - Call mint(address, amount)
                │
                ↓
  Blockchain Transaction:
    {
      from: "0xServerWallet",
      to: "0xScoreTokenContract",
      data: "mint(0xf39Fd..., 100)",
      gasLimit: "auto",
      gasPrice: "auto"
    }
                │
                ↓
  Transaction Hash:
    "0x123abc...def789"
                │
                ↓
  Posted to PR:
    "🎉 Settlement Completed!
     TX Hash: 0x123abc...def789
     Explorer: https://monad.vision/tx/0x123abc...def789"
```