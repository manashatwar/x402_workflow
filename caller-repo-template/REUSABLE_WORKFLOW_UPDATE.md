# 🔄 Reusable Workflow Update

## ✅ Changes Made

We've updated the system to use **proper reusable workflows** instead of workflow_dispatch.

### What Changed?

#### 1. **pr-x402-trigger.yml** (Caller Repository Workflow)

**Before:** Used `workflow_dispatch` API call to trigger x402-settlement-demo.yml
```yaml
uses: actions/github-script@v7
# ... API call to trigger workflow_dispatch
```

**After:** Uses `workflow_call` to call x402-settlement.yml as a reusable workflow
```yaml
uses: manashatwar/x402_workflow/.github/workflows/x402-settlement.yml@main
with:
  repo_name: ${{ github.repository }}
  issue_number: ${{ github.event.issue.number }}
  recipient_wallet: ${{ steps.find_wallet.outputs.wallet_address }}
  score_amount: ${{ fromJSON(steps.extract_amount.outputs.amount) }}
  network: 'monad-testnet'
secrets:
  THIRDWEB_SECRET_KEY: ${{ secrets.THIRDWEB_SECRET_KEY }}
  SERVER_WALLET: ${{ secrets.X402_SERVER_WALLET }}
  SCORE_TOKEN_CONTRACT: ${{ secrets.X402_SCORE_TOKEN_CONTRACT }}
  RPC_URL: ${{ secrets.X402_RPC_URL }}
  CALLBACK_GITHUB_TOKEN: ${{ secrets.X402_WORKFLOW_TOKEN }}
```

#### 2. **x402-settlement.yml** (x402_workflow Repository)

**Updated:**
- Added `CALLBACK_GITHUB_TOKEN` to secrets input
- Changed all comment posting to use `CALLBACK_GITHUB_TOKEN` instead of `GITHUB_TOKEN`
- This allows cross-repository comment posting without permission issues

**Before:**
```yaml
with:
  github-token: ${{ github.token }}
```

**After:**
```yaml
with:
  github-token: ${{ secrets.CALLBACK_GITHUB_TOKEN }}
```

#### 3. **x402-settlement-demo.yml** (x402_workflow Repository)

**No changes needed** - This remains as a manual testing workflow using `workflow_dispatch`.

## 🎯 Why This Change?

### Problem with Old Approach
1. **Security Issue:** Secrets passed as workflow_dispatch inputs are visible in logs
2. **Permission Issue:** GITHUB_TOKEN from x402_workflow couldn't post comments to caller repo (403 errors)
3. **Architecture:** workflow_dispatch is for manual triggers, not automation

### Benefits of New Approach
1. **✅ Secure:** Secrets passed properly via workflow_call mechanism
2. **✅ Proper Permissions:** CALLBACK_GITHUB_TOKEN has explicit cross-repo permissions
3. **✅ Clean Architecture:** Reusable workflow (workflow_call) for automation, workflow_dispatch for testing
4. **✅ Better Debugging:** Cleaner workflow runs, easier to trace

## 🔐 Secret Configuration

### In Caller Repository (Your Repo)
```
X402_WORKFLOW_TOKEN       - PAT with 'repo' and 'workflow' scopes
X402_SERVER_WALLET        - Private key with MON tokens
X402_SCORE_TOKEN_CONTRACT - Score token contract address
X402_RPC_URL              - Monad RPC endpoint
THIRDWEB_SECRET_KEY       - Thirdweb secret key
```

### In x402_workflow Repository
```
CALLBACK_GITHUB_TOKEN     - PAT with 'repo' scope (for posting comments back)
THIRDWEB_SECRET_KEY       - Thirdweb secret key
```

**Note:** `CALLBACK_GITHUB_TOKEN` receives the value of `X402_WORKFLOW_TOKEN` from the caller repository.

## 📝 Migration Steps

If you already have the old version deployed:

1. **Update pr-x402-trigger.yml:**
   - Replace lines 241-315 with the new `uses:` approach
   - Change `manashatwar/x402_workflow` to your username
   - Keep all your existing secrets

2. **Update x402_workflow repository:**
   - Pull latest x402-settlement.yml (already updated)
   - Add `CALLBACK_GITHUB_TOKEN` secret to repository

3. **Test:**
   - Create a test PR
   - Submit wallet as PR author
   - Use `/send 100` as maintainer
   - Verify comment posting works

## 🎬 Workflow Comparison

### x402-settlement.yml (Production - Reusable)
- **Trigger:** `workflow_call` (called by other workflows)
- **Use Case:** Automated PR settlement
- **Secrets:** Passed securely via workflow_call
- **Modified:** ✅ Updated to use CALLBACK_GITHUB_TOKEN

### x402-settlement-demo.yml (Testing - Manual)
- **Trigger:** `workflow_dispatch` (manual button click)
- **Use Case:** Manual testing and debugging
- **Secrets:** Entered as inputs (fine for testing)
- **Modified:** ✅ Updated to use CALLBACK_GITHUB_TOKEN

## ✨ Result

You now have:
- 🔒 Secure secret passing
- 💬 Cross-repository comment posting
- 🏗️ Proper workflow architecture
- 🧪 Separate testing workflow
- 📊 Better traceability

## 🆘 Troubleshooting

### "Resource not accessible by integration" error?
- ✅ Fixed! CALLBACK_GITHUB_TOKEN now handles cross-repo comments

### Secrets visible in logs?
- ✅ Fixed! Secrets passed via workflow_call, not workflow_dispatch inputs

### Can't trigger workflow?
- Verify `uses:` line has correct username
- Ensure X402_WORKFLOW_TOKEN has 'workflow' scope
- Check CALLBACK_GITHUB_TOKEN is set in x402_workflow repo

---

**Updated:** [Current Date]  
**Architecture:** Reusable Workflows (workflow_call)  
**Security:** Proper secret management ✅
