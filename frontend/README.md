# x402 Frontend

Simple web interface to trigger GitHub workflow for token settlement.

## Files

- `index.html` - Main web UI for triggering settlements
- `workflow.html` - Alternative trigger page

## Deploy on Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Follow prompts

Or deploy via Vercel dashboard:
- Import this repository
- Vercel will auto-detect and deploy from `frontend/` folder

## Features

- No backend required
- All credentials stored in browser localStorage
- Direct GitHub API calls
- Pre-filled default values for testing
