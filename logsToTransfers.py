from hashToLogsDecoder import hashToLogsDecode
import ast
import math
from pycoingecko import CoinGeckoAPI


def getTokenDeposits(logs):
    transfers = [log for log in logs if log["name"] == "Transfer"]

    return [
        transfer
        for transfer in transfers
        if ast.literal_eval(transfer["data"][0]["value"]) != 0
    ]


def getInitialParams(deposits):
    tokenTuples = []
    for deposit in deposits:
        tokenTuples.append(
            (
                deposit["address"],
                (deposit["data"][2]["value"] / 10 ** deposit["decimals"]),
            )
        )
    # returns token 1 address, token2 address, initial price ratio
    return (tokenTuples[0][0], tokenTuples[1][0], tokenTuples[0][1] / tokenTuples[1][1])


def getIL(deposits, coinList, cg):
    initialParams = getInitialParams(deposits)
    initialRatio = initialParams[2]
    currentRatio = getCurrentPriceRatio(
        initialParams[0], initialParams[1], coinList, cg
    )
    return calculateIL(initialRatio, currentRatio)


def calculateIL(initialRatio, currentRatio):
    PR = currentRatio / initialRatio
    IL = (2 * math.sqrt(PR) / (1 + PR)) - 1
    return abs(IL) * 100


def getTokenId(tokenAddress, coinList):
    for token in coinList:
        if str(tokenAddress).lower() in token["platforms"].values():
            return token["id"]
    return None


def getTokenPrice(tokenAddress, coinList, cg):
    tokenId = getTokenId(tokenAddress, coinList)
    return cg.get_price(ids=tokenId, vs_currencies="usd")[tokenId]["usd"]


def getCurrentPriceRatio(token1Address, token2Address, coinList, cg):
    token1Price = getTokenPrice(token1Address, coinList, cg)
    token2Price = getTokenPrice(token2Address, coinList, cg)
    PR = token2Price / token1Price
    return PR


def main():
    cg = CoinGeckoAPI()
    decodedLogs = hashToLogsDecode(
        "polygon", "0x22f12eb7a7ec31a7bf01a58dcfc0faa73341b6d56d62a33dd8a0b41a6fdf6667"
    )

    deposits = getTokenDeposits(decodedLogs)
    # print(getInitialPriceRatio(deposits))

    coinList = cg.get_coins_list(include_platform=True)
    # tokenId = getTokenId(0xC02AAA39B223FE8D0A0E5C4F27EAD9083C756CC2, coinList)
    # print(tokenId)
    # getTokenPrice(
    #     "0xC02AAA39B223FE8D0A0E5C4F27EAD9083C756CC2",
    #     coinList,
    #     cg,
    # )
    print(
        getIL(
            deposits,
            coinList,
            cg,
        )
    )


if __name__ == "__main__":
    main()
