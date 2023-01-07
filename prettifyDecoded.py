""" present decoded logs as pandas dataframes"""

info = []
for dictionary in decodedTxs:
    if dictionary["name"] == "Transfer":
        data = {
            "Address": dictionary["address"],
            "From": dictionary["data"][0]["value"],
            "To": dictionary["data"][1]["value"],
            "Value": dictionary["data"][2]["value"],
        }
        info.append(data)
    elif dictionary["name"] == "Swap":
        data = {
            "Address": dictionary["address"],
            "From": dictionary["data"][0]["value"],
            "To": dictionary["data"][1]["value"],
            "Amount0": dictionary["data"][2]["value"],
            "Amount1": dictionary["data"][3]["value"],
            "Price": dictionary["data"][4]["value"],
        }
        info.append(data)

df0 = pd.DataFrame(info)
# print(df0)

df1 = pd.DataFrame(decodedTxs)
print(df1)
