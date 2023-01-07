import json
import requests
import web3
import ast
import os
import eth_event
import pandas as pd
from dotenv import load_dotenv


class Chain:
    def __init__(self, network):
        # network = 'eth' or 'polygon'
        load_dotenv()
        self.networkParams = ast.literal_eval(os.getenv("NETWORK_PARAMETERS"))[network]
        self.network = network
        self.socket = self.networkParams["alchemySocket"]
        self.w3 = web3.Web3(web3.Web3.HTTPProvider(self.socket))
        self.explorerKey = self.networkParams["explorerKey"]

    def isConnected(self):
        print(f"connected: ", self.w3.isConnected())

    def getTxReceiptFromHash(self, txHash):
        return self.w3.eth.get_transaction_receipt(txHash)

    def getContractAbiAsList(self, Address):
        endpoints = {
            "eth": f"https://api.etherscan.io/api?module=contract&action=getabi&address={Address}&apikey={self.explorerKey}",
            "polygon": f"https://api.polygonscan.com/api?module=contract&action=getabi&address={Address}&apikey={self.explorerKey}",
        }
        abi_endpoint = endpoints[self.network]
        abiString = (json.loads(requests.get(abi_endpoint).text))["result"]
        return json.loads(abiString)

    def decodeLogsFromReceipt(self, receipt):
        decodedLogs = []

        for log in receipt["logs"]:
            contractAddress = log["address"]
            abi = self.getContractAbiAsList(contractAddress)
            topicMap = eth_event.get_topic_map(abi)
            # log must be a list
            logInListForm = [log]
            decodedLog = eth_event.decode_logs(logInListForm, topicMap, True)
            decodedLogs.append(decodedLog)

        decodedList = []
        for logList in decodedLogs:
            for txDict in logList:
                if txDict["decoded"] == True:
                    decodedList.append(txDict)
        return decodedList


def main():
    ch = Chain("polygon")
    ch.isConnected()
    txHash = "0x08476ade7709a629d15c393dbdc35298a378668f2cd45ec73575e6ce4de483fc"
    receipt = ch.w3.eth.get_transaction_receipt(txHash)
    decodedTxs = ch.decodeLogsFromReceipt(receipt)
    info = []
    for dictionary in decodedTxs:
        if dictionary["name"] == "Transfer":
            data = {
                "Address": dictionary["address"],
                "From": dictionary["data"][0]["value"],
                "To": dictionary["data"][1]["value"],
                "Value": dictionary["data"][2]["value"],
            }
        elif dictionary["name"] == "Swap":
            data = {
                "Address": dictionary["address"],
                "From": dictionary["data"][0]["value"],
                "To": dictionary["data"][1]["value"],
                "Amount0": dictionary["data"][2]["value"],
                "Amount1": dictionary["data"][3]["value"],
                "Price": dictionary["data"][4]["value"],
            }
        # WHY DUPLICATES?!
        info.append(data)
    df = pd.DataFrame(info)
    print(df)

    # df = pd.DataFrame(decodedTxs)
    # print(df)
    # print(df.loc[0]["data"])


if __name__ == "__main__":
    main()
