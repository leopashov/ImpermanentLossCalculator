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

    def isConnected(self):
        print(f"connected: ", self.w3.isConnected())


def main():
    ch = Chain("polygon")
    ch.isConnected()


if __name__ == "__main__":
    main()
