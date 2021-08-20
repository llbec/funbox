import { task } from "hardhat/config";
import { deployContract } from "./helpers/contracts-deploy"
import { setHRE } from "./helpers/utils"

type tplotOptions = {
    [key: string]: string
}

//Test Token
const Test_TOKEN: tplotOptions = {
    hecotest: "0x049f8b2dac2A53238511601026A06ac5281655c7",
    heco: "",
}

const HecoTest_Banks: tplotOptions = {
    CoinBank: "0x6dcED40FF523ea4480506314D39cEfD55cC670b5",
    CoinBankHalf: "0x4C18b3129946fC3ae9a66530f66fc650c3d510EE",
    ProxyBank: "0xc7b275Fa0Ae160041B6B3D60472ae4dF3BD44919"
}

task('erc20', 'deploy an erc20 token for test, suggest once')
    .addParam('name', 'Test Erc20 Token')
    .addParam('symbol', 'TE20T')
    .setAction(async (args, hre) => {
        setHRE(hre);
        const contract = deployContract("erc20Token", [args.name, args.symbol], true);
        console.log((await contract).address);
    });

task('proxy', 'deploy proxy contracts')
    .setAction(async (args, hre) => {
        setHRE(hre);
        const coinbank = deployContract("CoinBank", [], true);
        await (await coinbank).deployed();
        const coinbankhalf = deployContract("CoinbankHalf", [], true);
        await (await coinbankhalf).deployed();
        const bankproxy = deployContract("PiggyBank", [(await coinbank).address, Test_TOKEN[hre.network.name]], true);
        console.log('\nbank1: %s\nbank2: %s\nproxy: %s', (await coinbank).address, (await coinbankhalf).address, (await bankproxy).address);
        /*const bankproxy = deployContract("PiggyBank", [HecoTest_Banks["CoinBank"]], true);
        console.log('\nBank Proxy: %s', (await bankproxy).address)*/
    });