import { task } from "hardhat/config";
import "@nomiclabs/hardhat-waffle";
import "@nomiclabs/hardhat-etherscan";

require('dotenv').config();

const path = require('path');
const secretKey = process.env.SECRETKEY || '';

require(`${path.join(__dirname, 'tasks')}/deploy.ts`);

// This is a sample Hardhat task. To learn how to create your own go to
// https://hardhat.org/guides/create-task.html
task("accounts", "Prints the list of accounts", async (args, hre) => {
  const accounts = await hre.ethers.getSigners();

  for (const account of accounts) {
    console.log(await account.address);
  }
});

task("readenv", "Prints process.env", async (args, hre) => {
  const _env = process.env;
  console.log(_env);
});

// You need to export an object to set up your config
// Go to https://hardhat.org/config/ to learn more

export default {
  solidity: "0.8.4",
  defaultNetwork: "hecotest",
  networks: {
    hardhat: {},
    hecotest: {
      chainId: 256,
      url: "https://http-testnet.hecochain.com",
      accounts: ["0x35550f30bc7ac8e797c5405755e85e39edc72a3de78d69eab04a72a41a99f6e2"],
      gas: 9500000,
      gasPrice: 8000000000,
    },
    heco: {
      chainId: 128,
      url: "https://http-mainnet-node.huobichain.com",
      accounts:[secretKey],
      gas: 9500000,
      gasPrice: 8000000000,
    }
  },
  typechain: {
    outDir: "src/types",
    target: "ethers-v5",
  },
  etherscan: {
    // Your API key for Etherscan
    // Obtain one at https://etherscan.io/
    apiKey: process.env.ETHERSCAN_API_KEY
  }
};