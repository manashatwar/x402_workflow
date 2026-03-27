# File Reference (Ownership-Focused)

Use this document to find where behavior is implemented in this reusable repo.

Caller repository files are documented separately in [caller-repo-template/docs/README.md](https://github.com/kpj2006/caller-repo-template/blob/main/docs/README.md).

## Workflow Files

- .github/workflows/x402-settlement.yml: reusable production settlement workflow
- .github/workflows/x402-settlement-demo.yml: manual demo/testing workflow

## Settlement Engine

- src/settlement/sendScore.js: validates env, builds transaction, executes mint
- src/validation/addressValidator.js: wallet and amount validation helpers
- config/chainConfig.js: network configuration and explorer URL helpers

## Contract Interface

- src/contracts/ScoreToken.abi.json: ABI used by settlement engine
- src/contracts/scoreToken.js: ABI module export

## Project Metadata

- package.json: scripts and dependencies
- README.md: top-level navigation and integration entry

## Where To Look For Caller Behavior

For PR comment collection, maintainer command patterns, and operator UX flow, use:

- [caller-repo-template/README.md](https://github.com/kpj2006/caller-repo-template/blob/main/README.md)
- [caller-repo-template/docs/QUICKSTART.md](https://github.com/kpj2006/caller-repo-template/blob/main/docs/QUICKSTART.md)
- [caller-repo-template/docs/MAINTAINER_GUIDE.md](https://github.com/kpj2006/caller-repo-template/blob/main/docs/MAINTAINER_GUIDE.md)
