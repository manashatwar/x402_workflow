                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          // Chain configuration for Monad networks
// Reference: https://docs.monad.xyz/developer-essentials/network-information
// x402 Guide: https://docs.monad.xyz/guides/x402-guide

export const chainConfig = {
  "monad-testnet": {
    chainId: 41454, // Monad Devnet/Testnet
    name: "Monad Testnet",
    rpcUrl: process.env.RPC_URL || "https://testnet.monad.xyz",
    explorerUrl: "https://testnet.monadvision.com",
    nativeCurrency: {
      name: "MON",
      symbol: "MON",
      decimals: 18,
    },
    // USDC contract on Monad testnet (example - verify actual address)
    usdcContract: "0x...", // Update with actual USDC testnet contract
    features: {
      tps: 10000,
      blockTime: "0.4s",
      finality: "single-slot",
    },
  },
  "monad-mainnet": {
    chainId: 41454, // Monad mainnet chain ID
    name: "Monad Mainnet",
    rpcUrl: process.env.RPC_URL || "https://rpc.monad.xyz",
    explorerUrl: "https://monadvision.com",
    nativeCurrency: {
      name: "MON",
      symbol: "MON",
      decimals: 18,
    },
    // USDC contract on Monad mainnet (example - verify actual address)
    usdcContract: "0x...", // Update with actual USDC mainnet contract
    features: {
      tps: 10000,
      blockTime: "0.4s",
      finality: "single-slot",
    },
  },
};

/**
 * Get chain configuration for a given network
 * @param {string} network - Network identifier (monad-testnet | monad-mainnet)
 * @returns {object} Chain configuration
 * @throws {Error} If network is not supported
 */
export function getChainConfig(network) {
  const config = chainConfig[network];
  if (!config) {
    throw new Error(
      `Unknown network: ${network}. Supported: monad-testnet, monad-mainnet`
    );
  }
  return config;
}

/**
 * Get block explorer URL for a transaction
 * @param {string} txHash - Transaction hash
 * @param {string} network - Network identifier
 * @returns {string} Explorer URL
 */
export function getExplorerTxUrl(txHash, network) {
  const config = getChainConfig(network);
  return `${config.explorerUrl}/tx/${txHash}`;
}

/**
 * Get block explorer URL for an address
 * @param {string} address - Wallet or contract address
 * @param {string} network - Network identifier
 * @returns {string} Explorer URL
 */
export function getExplorerAddressUrl(address, network) {
  const config = getChainConfig(network);
  return `${config.explorerUrl}/address/${address}`;
}
