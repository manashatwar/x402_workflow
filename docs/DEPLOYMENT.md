# Deployment (Reusable Repo)

This guide is only for operating this reusable settlement repository.

For caller-repo setup (PR triggers, /send command, contributor flow), use:
[caller-repo-template/docs/QUICKSTART.md](https://github.com/kpj2006/caller-repo-template/blob/main/docs/QUICKSTART.md)

## Prerequisites

- Node.js 20+
- npm 9+
- Deployed SCORE token contract on Monad
- Server wallet with MON for gas
- Thirdweb backend secret key

## Required Contract Capability

Contract must expose mint capability and the server wallet must be authorized to mint.

## Required Secret (Reusable Repo)

- THIRDWEB_SECRET_KEY: Thirdweb backend authentication

Other values are provided through workflow inputs or caller repo secrets.

## Local Install

```bash
npm install
```

## Manual Validation via Demo Workflow

1. Open GitHub Actions.
2. Run x402 Settlement Demo.
3. Provide recipient, amount, network, wallet key, contract, and RPC URL.
4. Confirm transaction hash appears in workflow output.

Use testnet first before any mainnet run.

## Production Integration Contract

Caller repositories must call reusable workflow:

- [.github/workflows/x402-settlement.yml](../.github/workflows/x402-settlement.yml)

Input/output details are documented in [WORKFLOWS.md](WORKFLOWS.md).

## Mainnet Cutover Checklist

1. Confirm contract and server wallet on mainnet.
2. Ensure minter permission is granted to server wallet.
3. Update caller-provided contract and RPC values.
4. Set workflow input network to monad-mainnet.
5. Run one low-amount verification settlement.

## Troubleshooting

Missing environment values:

- Verify caller workflow passes all required inputs and secrets.

Authorization or revert errors:

- Verify server wallet has mint authority.
- Verify correct contract for selected network.

Thirdweb errors:

- Verify backend secret key format and scope.

Explorer mismatch:

- Verify network key and RPC endpoint alignment.
