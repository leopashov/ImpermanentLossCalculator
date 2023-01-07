from hashToLogsDecoder import hashToLogsDecode
import ast


def getTokenDeposits(logs):
    transfers = [log for log in logs if log["name"] == "Transfer"]

    return [
        transfer
        for transfer in transfers
        if ast.literal_eval(transfer["data"][0]["value"]) != 0
    ]


def main():
    decodedLogs = hashToLogsDecode(
        "polygon", "0x22f12eb7a7ec31a7bf01a58dcfc0faa73341b6d56d62a33dd8a0b41a6fdf6667"
    )

    deposits = getTokenDeposits(decodedLogs)
    print(deposits)
    for deposit in deposits:
        pass


if __name__ == "__main__":
    main()
