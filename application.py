import json
import requests
import web3
import ast
import os
from dotenv import load_dotenv


class Chain:
    def __init__(self, network):
        load_dotenv()
        self.network = network
        self.socket = ast.literal_eval(os.getenv("ALCHEMY_SOCKETS"))[network]
        self.w3 = web3.Web3(web3.Web3.HTTPProvider(self.socket))
        self.ETHERSCAN_TOKEN = os.getenv("ETHERSCAN_TOKEN")

    def isConnected(self):
        print(f"connected: ", self.w3.isConnected())


def main():
    ch = Chain("EthMainnet")
    ch.isConnected()
    w3 = ch.w3
    txHash = "0xb231b6247eb4bae5cada800bf0abb244b50d33701bc2e1d838006c354f55e0e0"
    receipt = w3.eth.get_transaction_receipt(txHash)

    # Iterate over the logs
    for log in receipt["logs"]:
        # Check if the log is a token transfer event
        smartContract = log["address"]
        abi_endpoint = f"https://api.etherscan.io/api?module=contract&action=getabi&address={smartContract}&apikey={ch.ETHERSCAN_TOKEN}"
        abi = (json.loads(requests.get(abi_endpoint).text))["result"]

        # f = open("./ABIs/Erc20_abi.json")
        # abi = json.load(f)
        print(abi)
        contract = w3.eth.contract(smartContract, abi=abi)
        receipt_event_signature_hex = w3.toHex(log["topics"][0])
        abi_events = [abi for abi in contract.abi if abi["type"] == "event"]

        # Determine which event in ABI matches the transaction log you are decoding
        for event in abi_events:
            # Get event signature components
            name = event["name"]
            inputs = [param["type"] for param in event["inputs"]]
            inputs = ",".join(inputs)
            # Hash event signature
            event_signature_text = f"{name}({inputs})"
            event_signature_hex = w3.toHex(w3.keccak(text=event_signature_text))
            # Find match between log's event signature and ABI's event signature
            if event_signature_hex == receipt_event_signature_hex:
                # Decode matching log
                decoded_logs = contract.events[event["name"]]().processReceipt(receipt)

                print(decoded_logs)


if __name__ == "__main__":
    main()
