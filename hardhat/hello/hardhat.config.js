/**
 * @type import('hardhat/config').HardhatUserConfig
 */
module.exports = {
  solidity: "0.7.3",
  defaultNetwork: "heco",
  networks: {
    heco: {
      url: "https://http-mainnet-node.huobichain.com",
      chainId: 128
    },
    heco_test: {
      url: "https://http-testnet.hecochain.com",
      chainId: 256
    }
  }
};
