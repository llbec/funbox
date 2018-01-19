#include <fstream>
#include <ctime>

#include "arith_uint256.h"
#include "chain.h"
#include "chainparams.h"
#include "primitives/block.h"
#include "uint256.h"
#include "util.h"


#define BLOCK_INTERVAL 150
#define RAND_RANGE     30
#define SAME_TIMES     20

//2018/1/1/0:0:0
//#define START_TIME  1514736000

CChain CBlockList;



unsigned int CalculateNextWorkRequired(arith_uint256 bnAvg,
                                       int64_t nLastBlockTime, int64_t nFirstBlockTime,
                                       const Consensus::Params& params)
{
    // Limit adjustment step
    // Use medians to prevent time-warp attacks
    int64_t nActualTimespan = nLastBlockTime - nFirstBlockTime;
    LogPrint("pow", "  nActualTimespan = %d  before dampening\n", nActualTimespan);
    nActualTimespan = params.AveragingWindowTimespan() + (nActualTimespan - params.AveragingWindowTimespan())/4;
    LogPrint("pow", "  nActualTimespan = %d  before bounds\n", nActualTimespan);

    if (nActualTimespan < params.MinActualTimespan())
        nActualTimespan = params.MinActualTimespan();
    if (nActualTimespan > params.MaxActualTimespan())
        nActualTimespan = params.MaxActualTimespan();

    // Retarget
    const arith_uint256 bnPowLimit = UintToArith256(params.powLimit);
    arith_uint256 bnNew {bnAvg};
    bnNew /= params.AveragingWindowTimespan();
    bnNew *= nActualTimespan;

    if (bnNew > bnPowLimit)
        bnNew = bnPowLimit;

    /// debug print
    LogPrint("pow", "GetNextWorkRequired RETARGET\n");
    LogPrint("pow", "params.AveragingWindowTimespan() = %d    nActualTimespan = %d\n", params.AveragingWindowTimespan(), nActualTimespan);
    LogPrint("pow", "Current average: %08x  %s\n", bnAvg.GetCompact(), bnAvg.ToString());
    LogPrint("pow", "After:  %08x  %s\n", bnNew.GetCompact(), bnNew.ToString());

    return bnNew.GetCompact();
}

unsigned int GetNextWorkRequired(const CBlockIndex* pindexLast, const CBlockHeader *pblock, const Consensus::Params& params)
{
    unsigned int nProofOfWorkLimit = UintToArith256(params.powLimit).GetCompact();
	int i;

    // Genesis block
    if (pindexLast == NULL)
        return nProofOfWorkLimit;

    // Find the first block in the averaging interval
    const CBlockIndex* pindexFirst = pindexLast;
    arith_uint256 bnTot {0};
    for (i = 0; pindexFirst && i < params.nPowAveragingWindow; i++) {
        arith_uint256 bnTmp;
        bnTmp.SetCompact(pindexFirst->nBits);
        bnTot += bnTmp;
        pindexFirst = pindexFirst->pprev;
    }

    // Check we have enough blocks
    if (pindexFirst == NULL)
        return nProofOfWorkLimit;

    arith_uint256 bnAvg {bnTot / params.nPowAveragingWindow};

    return CalculateNextWorkRequired(bnAvg, pindexLast->GetMedianTimePast(), pindexFirst->GetMedianTimePast(), params);
}

double ConvertBitsToDouble(unsigned int nBits)
{
    int nShift = (nBits >> 24) & 0xff;

    double dDiff = (double)0x0000ffff / (double)(nBits & 0x00ffffff);

    while (nShift < 29)
    {
        dDiff *= 256.0;
        nShift++;
    }
    while (nShift > 29)
    {
        dDiff /= 256.0;
        nShift--;
    }

    return dDiff;
}

CAmount BnetGetBlockSubsidy(int nPrevBits, int nPrevHeight, const Consensus::Params& consensusParams, bool fSuperblockPartOnly)
{
    double dDiff;
    CAmount nSubsidyBase;

    if (nPrevHeight <= 4500 && Params().NetworkIDString() == CBaseChainParams::MAIN) {
        /* a bug which caused diff to not be correctly calculated */
        dDiff = (double)0x0000ffff / (double)(nPrevBits & 0x00ffffff);
    } else {
        dDiff = ConvertBitsToDouble(nPrevBits);
    }

    if (nPrevHeight < 5465) {
        // Early ages...
        // 1111/((x+1)^2)
        nSubsidyBase = (1111.0 / (pow((dDiff+1.0),2.0)));
        if(nSubsidyBase > 500) nSubsidyBase = 500;
        else if(nSubsidyBase < 1) nSubsidyBase = 1;
    } else if (nPrevHeight < 17000 || (dDiff <= 75 && nPrevHeight < 24000)) {
        // CPU mining era
        // 11111/(((x+51)/6)^2)
        nSubsidyBase = (11111.0 / (pow((dDiff+51.0)/6.0,2.0)));
        if(nSubsidyBase > 500) nSubsidyBase = 500;
        else if(nSubsidyBase < 25) nSubsidyBase = 25;
    } else {
        // GPU/ASIC mining era
        // 2222222/(((x+2600)/9)^2)
        nSubsidyBase = (2222222.0 / (pow((dDiff+2600.0)/9.0,2.0)));
        if(nSubsidyBase > 25) nSubsidyBase = 25;
        else if(nSubsidyBase < 5) nSubsidyBase = 5;
    }

    // LogPrintf("height %u diff %4.2f reward %d\n", nPrevHeight, dDiff, nSubsidyBase);
    CAmount nSubsidy = nSubsidyBase * COIN;

    // yearly decline of production by ~7.1% per year, projected ~18M coins max by year 2050+.
    for (int i = consensusParams.nSubsidyHalvingInterval; i <= nPrevHeight; i += consensusParams.nSubsidyHalvingInterval) {
        nSubsidy -= nSubsidy/14;
    }

    // Hard fork to reduce the block reward by 10 extra percent (allowing budget/superblocks)
    CAmount nSuperblockPart = (nPrevHeight > consensusParams.nBudgetPaymentsStartBlock) ? nSubsidy/10 : 0;

    return fSuperblockPartOnly ? nSuperblockPart : nSubsidy - nSuperblockPart;
}

unsigned int GetBlockInterval()
{
#if 0
	return (unsigned int)((rand() % (BLOCK_INTERVAL - 1)) + 1);
#else
	return (unsigned int)((rand() % (RAND_RANGE - 1)) + 1);;
#endif
}

void LogChainInfo()
{
	std::string strPrint = "";
	char astr[50];
	CBlockIndex *pBlock = NULL;
	pBlock = CBlockList.Genesis();
	int ih = CBlockList.Height() + 1;
	int itime = pBlock->nTime;
	int ibits = pBlock->nBits;
	std::time_t now = std::time(0);
    std::tm *ltm = std::localtime(&now);
	std::string filename = "";

	sprintf(astr, "out%2d%2d%2d.txt", ltm->tm_hour, ltm->tm_min, ltm->tm_sec);
	filename = astr;
	memset(astr,0,sizeof(astr));
	printf("file:%s\n",filename.c_str());

	std::ofstream out(filename.c_str());

	for (int i = 0; i < ih; i++)
	{
		sprintf(astr, "Block[%d]:\n", pBlock->nHeight);
		strPrint += astr;
		memset(astr,0,sizeof(astr));

		sprintf(astr, "TIME is %d, ", pBlock->nTime);
		strPrint += astr;
		memset(astr,0,sizeof(astr));

		sprintf(astr, "Interval is %d;  ", (pBlock->nTime - itime));
		strPrint += astr;
		memset(astr,0,sizeof(astr));
		itime = pBlock->nTime;

		sprintf(astr, "Diff is %d, ", pBlock->nBits);
		strPrint += astr;
		memset(astr,0,sizeof(astr));
		
		sprintf(astr, "Increment is %d;  ", (pBlock->nBits - ibits));
		strPrint += astr;
		memset(astr,0,sizeof(astr));
		ibits = pBlock->nBits;

		if(pBlock->pprev != NULL)
		{
			sprintf(astr, "Subsidy is %lld\n", BnetGetBlockSubsidy(pBlock->pprev->nBits, pBlock->pprev->nHeight, Params().GetConsensus(), false));
		}
		else
		{
			sprintf(astr, "Subsidy is %lld\n", 50 * COIN);
		}
		strPrint += astr;
		memset(astr,0,sizeof(astr));

		//strPrint += "\n";
		//printf("%s\n", strPrint.c_str());
		if (out.is_open()){
			out << strPrint.c_str();
		}
		strPrint = "";

		pBlock = CBlockList.Next(pBlock);
	}

	out.close();
}

int main(int argc, char * * argv)
{
	int uBlockNumber = 50000;
	int uBlockInterval;
	CBlockIndex * pNewBlock;
	CBlockIndex * pPreBlock = NULL;

	SelectParams(ChainNameFromCommandLine());
	
	printf("test start!\n");

	ParseParameters(argc, argv);

	CBlock &block = const_cast<CBlock&>(Params().GenesisBlock());

	pNewBlock = new CBlockIndex(block);
	//uBlockInterval = pNewBlock->nTime;
	pPreBlock = pNewBlock;
	uBlockInterval = GetBlockInterval();

	uBlockNumber += 1;
	for (int i = 1; i < uBlockNumber; i++)
	{
		if((i % SAME_TIMES) == 0){
			uBlockInterval = GetBlockInterval();
		}
		
		pNewBlock = new CBlockIndex();
		pNewBlock->pprev = pPreBlock;
		pNewBlock->nHeight = i;
		if((i / SAME_TIMES) % 2 == 0)
		{
			pNewBlock->nTime = (pPreBlock->nTime + BLOCK_INTERVAL) + uBlockInterval;
		}
		else
		{
			pNewBlock->nTime = (pPreBlock->nTime + BLOCK_INTERVAL) - uBlockInterval;
		}
		//pNewBlock->nTime = uBlockInterval;
		pNewBlock->nBits = GetNextWorkRequired(pPreBlock, NULL, Params().GetConsensus());

		pPreBlock = pNewBlock;
	}

	CBlockList.SetTip(pNewBlock);

	LogChainInfo();

	printf("test finish!\n");

	return 0;
}
