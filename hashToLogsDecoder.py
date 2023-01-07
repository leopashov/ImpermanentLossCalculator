import json
import requests
import web3
import ast
import os
import eth_event
import pandas as pd
from dotenv import load_dotenv

"""Main fucntion hashToLogsDecode takes a:
    - chain name string (either "eth" or "polygon")
    - transaction hash string
and returns the decoded logs as a list of dictionaries """


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

    def getContractAbiAsList(self, address):
        address = self.getImplementationContractIfExists(address)
        endpoints = {
            "eth": f"https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={self.explorerKey}",
            "polygon": f"https://api.polygonscan.com/api?module=contract&action=getabi&address={address}&apikey={self.explorerKey}",
        }
        abi_endpoint = endpoints[self.network]
        responseString = requests.get(abi_endpoint).text
        responseDict = json.loads(responseString)
        abiString = (responseDict)["result"]
        if responseDict["status"] == "0":
            print(responseDict["result"])
            print("trying with ERC20 ABI")
            # try using ERC20
            abiString = self.getERC20AbiString()
        return json.loads(abiString)

    def getERC20AbiString(self):
        f = open("./ABIs/Erc20_abi.json")
        return f.read()

    def getWbtcAbiList(self):
        f = open("./ABIs/WBTC_Proxy_abi.json")
        abi = json.load(f)
        return abi

    def addTokenInfo(self, ABI, address, log):
        contract = self.w3.eth.contract(address=address, abi=ABI)
        try:
            tokenDecimals = contract.functions.decimals().call()
            tokenName = contract.functions.name().call()
            tokenSymbol = contract.functions.symbol().call()
        except:
            print("couldn't get info, setting to 18, NA")
            tokenDecimals = 18
            tokenName = "NA"
            tokenSymbol = "NA"
        # print(f"from addDecimals, log: ", log)
        log[0]["decimals"] = tokenDecimals
        log[0]["token name"] = tokenName
        log[0]["token symbol"] = tokenSymbol

    def decodeLogsFromReceipt(self, receipt):
        decodedLogs = []

        for log in receipt["logs"]:
            contractAddress = log["address"]
            # print(contractAddress)
            abi = self.getContractAbiAsList(contractAddress)
            decodedLog = self.getDecodedLog(abi, log)
            # print(decodedLog)
            if decodedLog[0]["decoded"] == False:
                # wrong ABI has been used (most likely due to nin EIP 1967 proxy), use specific corner case to load local abi
                if (
                    self.network == "polygon"
                    and decodedLog[0]["address"]
                    == "0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6"
                ):
                    # WBTC on polygon network - load abi from local files
                    abi = self.getWbtcAbiList()
                    decodedLog = self.getDecodedLog(abi, log)
            self.addTokenInfo(abi, contractAddress, decodedLog)
            decodedLogs.append(decodedLog)

        decodedList = []
        for logList in decodedLogs:
            for txDict in logList:
                if txDict["decoded"] == True:
                    decodedList.append(txDict)
        return decodedList

    def getDecodedLog(self, abi, log):
        topicMap = eth_event.get_topic_map(abi)
        # log must be a list
        logInListForm = [log]
        return eth_event.decode_logs(logInListForm, topicMap, True)

    def getImplementationContractIfExists(self, proxyAddress):
        """reads proxy contract with address 'proxyAddress's storage at specific slot as defined in EIP 1967
        to obtain the implementation contract address."""
        impl_contract = web3.Web3.toHex(
            self.w3.eth.get_storage_at(
                proxyAddress,
                "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc",
            )
        )
        if int(impl_contract, 16) != 0:
            return impl_contract
        else:
            return proxyAddress


def hashToLogsDecode(chain, hash):
    ch = Chain(chain)
    txHash = hash
    receipt = ch.w3.eth.get_transaction_receipt(txHash)
    decodedTxs = ch.decodeLogsFromReceipt(receipt)
    return decodedTxs


def main():
    print(
        hashToLogsDecode(
            "polygon",
            "0xda05efaeace434d3f501c44e58949f197b770dfdfef3f3c6f7c6559e1bba0ea8",
        )
    )


if __name__ == "__main__":
    main()
