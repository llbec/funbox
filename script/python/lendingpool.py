#!/usr/bin/python3
from web3 import Web3

lendingpool_abi = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "asset",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "rateMode",
                "type": "uint256"
            },
            {
                "internalType": "address",
                "name": "onBehalfOf",
                "type": "address"
            }
        ],
        "name": "repay",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "user",
                "type": "address"
            }
        ],
        "name": "getUserAccountData",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "totalCollateralETH",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "totalDebtETH",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "availableBorrowsETH",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "currentLiquidationThreshold",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "ltv",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "healthFactor",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

w3 = Web3(Web3.HTTPProvider('https://http-mainnet.hecochain.com'))

lendingPool = w3.eth.contract(
    address='0x1BeB0e1d334a5289b235a4bdF8CA54146627A11a',
    abi=lendingpool_abi
)

# 地址和私钥
accountAddress = ''
accountPrivateKey = ''
# 还款资产
hfil = ''
# 还款金额
amount = 1000000000000000000
# 贷款方式
debtmode = 2
# 代还地址
onBehalfOf = ''

nonce = w3.eth.get_transaction_count(accountAddress)

repay_txn = lendingPool.functions.repay(hfil, amount, debtmode, onBehalfOf).buildTransaction({
    'chainId': 128,
    'gas': 7000000,
    'gasPrice': w3.toWei('3', 'gwei'),
    'nonce': nonce,
})

signed_Repaytxn = w3.eth.account.sign_transaction(
    repay_txn, private_key=accountPrivateKey)

w3.eth.send_raw_transaction(signed_Repaytxn.rawTransaction)
