from hashToLogsDecoder import hashToLogsDecode
import ast
import math


def getTokenDeposits(logs):
    transfers = [log for log in logs if log["name"] == "Transfer"]

    return [
        transfer
        for transfer in transfers
        if ast.literal_eval(transfer["data"][0]["value"]) != 0
    ]


def getInitialPriceRatio(deposits):
    tokenTuples = []
    for deposit in deposits:
        tokenTuples.append(
            (
                deposit["token symbol"],
                (deposit["data"][2]["value"] / 10 ** deposit["decimals"]),
            )
        )
    return tokenTuples[0][1] / tokenTuples[1][1]


def getCurrentPriceRatio():
    # call coingecko price data and divide (In same order!)
    # just call as above to ensure order.
    pass


def calculateIL(initialRatio, currentRatio):
    PR = currentRatio / initialRatio
    IL = (2 * math.sqrt(PR) / (1 + PR)) - 1
    return IL


def main():
    decodedLogs = hashToLogsDecode(
        "polygon", "0x22f12eb7a7ec31a7bf01a58dcfc0faa73341b6d56d62a33dd8a0b41a6fdf6667"
    )

    deposits = getTokenDeposits(decodedLogs)
    print(getInitialPriceRatio(deposits))


if __name__ == "__main__":
    main()
