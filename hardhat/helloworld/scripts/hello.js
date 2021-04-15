const Web3 = require('web3')

async function getChainId() {
	    const web3 = new Web3('https://http-mainnet.hecochain.com')
	    let chainId = await web3.eth.getChainId()
	    console.log(`chain id: ${chainId}`)
	    return chainId
}

getChainId()
	.then(() => process.exit(0))
	.catch(error =>{
		console.error(error);
		process.exit(1);
	});
