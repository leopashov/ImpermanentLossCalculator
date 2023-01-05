import web3


def main():
    w3 = web3.Web3(web3.Web3.HTTPProvider(avado_url))


if __name__ == "__main__":
    main()
