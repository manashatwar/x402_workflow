#!/usr/bin/env node
/**
 * Mints non-transferable ERC-20 tokens on Monad for score distribution
 */

import { createThirdwebClient } from "thirdweb";
import { prepareContractCall, sendTransaction } from "thirdweb";
import { privateKeyToAccount } from "thirdweb/wallets";
import { monadTestnet } from "thirdweb/chains";
import { getContract } from "thirdweb";
import { ethers } from "ethers";
import fs from "fs";

const monadMainnet = {
  id: 41454,
  name: "Monad",
  nativeCurrency: { name: "MON", symbol: "MON", decimals: 18 },
  rpcUrls: {
    default: { http: [process.env.RPC_URL || "https://rpc.monad.xyz"] },
  },
  blockExplorers: {
    default: { name: "MonadVision", url: "https://monadvision.com" },
  },
};

function validateEnv() {
  const required = [
    "THIRDWEB_SECRET_KEY",
    "SERVER_WALLET",
    "SCORE_TOKEN_CONTRACT",
    "RECIPIENT_WALLET",
    "SCORE_AMOUNT",
    "NETWORK",
    "ISSUE_NUMBER",
    "REPO_NAME",
  ];

  const missing = required.filter((key) => !process.env[key]);

  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(", ")}`
    );
  }

  const contractAddress = process.env.SCORE_TOKEN_CONTRACT.trim().replace(
    /['"]/g,
    ""
  );
  if (!ethers.isAddress(contractAddress)) {
    throw new Error(`Invalid SCORE_TOKEN_CONTRACT address`);
  }

  const recipientAddress = process.env.RECIPIENT_WALLET.trim().replace(
    /['"]/g,
    ""
  );
  if (!ethers.isAddress(recipientAddress)) {
    throw new Error(`Invalid RECIPIENT_WALLET address`);
  }

  const amount = parseInt(process.env.SCORE_AMOUNT, 10);
  if (isNaN(amount) || amount <= 0) {
    throw new Error(`Invalid SCORE_AMOUNT: ${process.env.SCORE_AMOUNT}`);
  }
}

function getChainConfig() {
  const network = process.env.NETWORK;

  if (network === "monad-testnet") {
    return monadTestnet;
  } else if (network === "monad-mainnet") {
    return monadMainnet;
  } else {
    throw new Error(
      `Unsupported network: ${network}. Use 'monad-testnet' or 'monad-mainnet'`
    );
  }
}

function getExplorerUrl(txHash, network) {
  if (network === "monad-testnet") {
    return `https://testnet.monadvision.com/tx/${txHash}`;
  } else if (network === "monad-mainnet") {
    return `https://monadvision.com/tx/${txHash}`;
  }
  return "";
}

async function main() {
  try {
    console.log("🚀 Starting x402 score settlement on Monad...\n");

    validateEnv();

    const recipient = process.env.RECIPIENT_WALLET.trim().replace(/['"]/g, "");
    const scoreAmount = process.env.SCORE_AMOUNT.trim();
    const network = process.env.NETWORK.trim();
    const issueNumber = process.env.ISSUE_NUMBER.trim();
    const repoName = process.env.REPO_NAME.trim();
    const tokenContract = process.env.SCORE_TOKEN_CONTRACT.trim().replace(
      /['"]/g,
      ""
    );

    console.log("Configuration:");
    console.log(`  Network: ${network}`);
    console.log(`  Recipient: ${recipient}`);
    console.log(`  Score Amount: ${scoreAmount}`);
    console.log(`  Token Contract: ${tokenContract}`);
    console.log(`  Issue: ${repoName}#${issueNumber}\n`);

    const client = createThirdwebClient({
      secretKey: process.env.THIRDWEB_SECRET_KEY,
    });

    const chain = getChainConfig();

    const account = privateKeyToAccount({
      client,
      privateKey: process.env.SERVER_WALLET.trim(),
    });

    console.log(`📝 Using server wallet: ${account.address}\n`);

    const contract = getContract({
      client,
      chain,
      address: tokenContract,
    });

    console.log("⚙️  Preparing mint transaction...");

    // Convert score amount to token units (18 decimals)
    const tokenAmount = BigInt(scoreAmount) * BigInt(10 ** 18);

    const transaction = prepareContractCall({
      contract,
      method: "function mint(address to, uint256 amount) external",
      params: [recipient, tokenAmount],
    });

    console.log("📤 Sending transaction to Monad...");
    const result = await sendTransaction({
      transaction,
      account,
    });

    const txHash = result.transactionHash;
    console.log(`✅ Transaction confirmed!`);
    console.log(`   Tx Hash: ${txHash}\n`);

    const explorerUrl = getExplorerUrl(txHash, network);

    if (process.env.GITHUB_OUTPUT) {
      const output = `TX_HASH=${txHash}\nEXPLORER_URL=${explorerUrl}\n`;
      fs.appendFileSync(process.env.GITHUB_OUTPUT, output);
      console.log("📋 Output variables set for GitHub Actions");
    }

    process.env.TX_HASH = txHash;
    process.env.EXPLORER_URL = explorerUrl;

    console.log("\n🎉 Score settlement completed successfully!");
    console.log(`   ${scoreAmount} tokens minted to ${recipient}`);
    console.log(`   Explorer: ${explorerUrl || "N/A"}\n`);

    process.exit(0);
  } catch (error) {
    console.error("\n❌ Error during score settlement:");
    console.error(error.message);

    if (error.stack) {
      console.error("\nStack trace:");
      console.error(error.stack);
    }

    // Set error message for GitHub Actions
    if (process.env.GITHUB_OUTPUT) {
      const errorMsg = error.message.replace(/\n/g, " ");
      fs.appendFileSync(
        process.env.GITHUB_OUTPUT,
        `ERROR_MESSAGE=${errorMsg}\n`
      );
    }

    process.env.ERROR_MESSAGE = error.message;

    process.exit(1);
  }
}

// Run the script
main();
