# 👨‍💼 Maintainer Guide - Using /send Command

## Overview

As a repository maintainer, you control when contributors receive token rewards and how much they get. This gives you flexibility to reward based on PR quality, complexity, and impact.

---

## 🎯 Quick Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/send 50` | Send 50 tokens | Small fixes, docs |
| `/send 100` | Send 100 tokens | Bug fixes, minor features |
| `/send 200` | Send 200 tokens | Medium features |
| `/send 500` | Send 500 tokens | Major features, refactoring |

---

## 📋 Workflow Steps

### 1. Contributor Opens PR
- Automatic welcome message is posted
- Asks for MetaMask wallet address

### 2. Contributor Submits Wallet
Contributor comments:
```
x402-wallet: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
```

Bot response:
```
✅ Wallet Address Saved!
Address: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266

Your wallet has been recorded. A maintainer will review 
your PR and send tokens when approved.

> Maintainers: Use /send <amount> to reward this contributor
```

### 3. You Review the PR
- Check code quality
- Review changes
- Assess impact and complexity

### 4. You Trigger Settlement
Comment on the PR:
```
/send 100
```

Bot response:
```
🔄 Settlement Triggered

Amount: 100 SCORE tokens
Recipient: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266

Processing transaction... ⏳
```

### 5. Transaction Completes
After ~1-2 minutes:
```
🎉 x402 Settlement Completed Successfully!

💰 Token Details
- Amount: 100 SCORE tokens
- Recipient: 0xf39Fd...92266
- Network: monad-testnet

🔗 Transaction Details
- Hash: 0x123abc...def789
- Explorer: View on MonadVision

✅ What This Means
- Non-transferable reputation tokens minted
- Tokens represent contribution to the project
- Visible in wallet on Monad network

> Thank you for your contribution! 🚀
```

---

## 🎨 Recommended Token Amounts

### Documentation Changes
```
/send 25    # Typo fixes
/send 50    # Minor docs updates
/send 100   # New documentation pages
```

### Bug Fixes
```
/send 75    # Simple bug fixes
/send 150   # Complex bug fixes
/send 300   # Critical security fixes
```

### Features
```
/send 150   # Small features
/send 300   # Medium features
/send 500   # Large features
/send 1000  # Major features/refactoring
```

### Special Contributions
```
/send 200   # Performance improvements
/send 250   # Test coverage additions
/send 500   # Architecture improvements
```

---

## 🔐 Permission Requirements

Only users with **write** or **admin** permissions can use `/send`:

✅ **Can use /send**:
- Repository admins
- Repository owners
- Collaborators with write access

❌ **Cannot use /send**:
- Contributors without write access
- PR authors (even if they have write access elsewhere)
- External contributors

---

## 💡 Best Practices

### 1. Communicate Your Scale
Add to your CONTRIBUTING.md:
```markdown
## Token Rewards

We reward contributions with SCORE tokens:
- 25-50: Documentation
- 75-150: Bug fixes
- 150-500: Features
- 500+: Major contributions
```

### 2. Be Consistent
Try to maintain consistent amounts for similar contributions to be fair.

### 3. Reward Promptly
Send tokens soon after merging PRs to keep contributors engaged.

### 4. Adjust Based on Impact
Feel free to adjust amounts based on:
- Lines of code changed
- Complexity
- Bug severity
- Strategic importance
- Time invested

### 5. Combine with Merge
Common workflow:
```
1. Review PR
2. Approve PR
3. Comment: "/send 100"
4. Merge PR

Or in one comment:
"Great work! Merging. /send 150"
```

---

## 🐛 Troubleshooting

### "Permission Denied" Error

**Problem**: You commented `/send` but got "Permission Denied"

**Solutions**:
1. Check you have write/admin access to the repository
2. Verify you're commenting on the correct repository
3. Make sure you're logged into the right GitHub account

### "No Wallet Address Found" Error

**Problem**: You used `/send` but bot says no wallet found

**Solutions**:
1. Ask PR author to submit wallet using `x402-wallet: 0x...`
2. Check if PR author commented in correct format
3. Verify the comment is from the PR author (not someone else)

### "Invalid /send Command Format" Error

**Problem**: Bot doesn't recognize your command

**Solutions**:
1. Use format: `/send <number>` (e.g., `/send 100`)
2. Don't use decimals (use whole numbers only)
3. Don't add extra characters or symbols
4. Make sure there's a space after `/send`

**Valid formats**:
```
✅ /send 100
✅ /send 50
✅ Great work! /send 200
```

**Invalid formats**:
```
❌ /send 100.5    (no decimals)
❌ /send100       (missing space)
❌ send 100       (missing /)
❌ /send          (missing amount)
```

### Settlement Triggers But Fails

**Problem**: Settlement starts but fails during execution

**Check x402_workflow repository**:
1. Is server wallet funded with MON?
2. Are all secrets configured correctly?
3. Is the RPC URL accessible?
4. Check workflow logs in x402_workflow Actions tab

---

## 📊 Multiple Contributors

### Same PR, Multiple People

If multiple people contributed:
```
Great work team!
@alice /send 150
@bob /send 150
@charlie /send 100
```

**Note**: Each person must have submitted their wallet address separately.

### Different Contributions, Different Amounts

```
Thanks everyone!

@alice - excellent refactoring /send 300
@bob - good bug fix /send 100
@charlie - docs update /send 50
```

---

## 🎯 Advanced Usage

### Conditional Rewards

**Example**: Reward only if tests pass
```yaml
# In your workflow (advanced)
- name: Check tests
  run: npm test
  
- name: Comment reward instruction
  if: success()
  run: |
    gh pr comment ${{ github.event.number }} \
      --body "Tests passed! Maintainer: /send 150"
```

### Automated Rewards by Labels

**Example**: Auto-suggest amount based on label
```yaml
# When label "good-first-issue" is added
- name: Suggest reward
  run: |
    gh pr comment ${{ github.event.number }} \
      --body "Great first contribution! Maintainer: /send 75"
```

### Batch Processing

Review multiple PRs and send rewards in batch:
1. Open PR #42: `/send 100`
2. Open PR #43: `/send 150`
3. Open PR #44: `/send 200`

Each triggers independently.

---

## 📈 Tracking & Analytics

### Manual Tracking

Keep a spreadsheet:
| PR # | Author | Amount | Date | Type |
|------|--------|--------|------|------|
| 42 | alice | 100 | 2026-01-20 | Bug fix |
| 43 | bob | 150 | 2026-01-21 | Feature |

### Automated Tracking (Advanc just lie K8s)

Query GitHub API for `/send` comments:
```javascript
// Find all /send commands in closed PRs
const comments = await github.paginate(
  github.rest.issues.listComments,
  { owner, repo, state: 'closed' }
);

const rewards = comments
  .filter(c => c.body.includes('/send'))
  .map(c => ({
    pr: c.issue_url,
    amount: c.body.match(/\/send\s+(\d+)/)[1],
    date: c.created_at
  }));
```

