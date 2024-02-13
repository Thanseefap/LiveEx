import pickle
import time
from datetime import datetime
from urllib.request import urlopen
import time as tm

import pandas as pd
from neo_api_client import NeoAPI


def getQuote(token, client):
    inst_tokens = [{"instrument_token": str(token), "exchange_segment": "nse_fo"}]
    tryNo = 0
    while tryNo <= 5:
        try:
            # get LTP and Market Depth Data
            ltp = client.quotes(instrument_tokens=inst_tokens, quote_type="ltp", isIndex=False)["message"][0]["ltp"]

            # OR Quotes API can be accessed without completing login by passing session_token, sid, and server_id
            if type(ltp) is not str:
                print(ltp)
                tryNo += 1
                time.sleep(1)
                continue
            return float(ltp)
        except Exception as e:
            print("Exception when calling get Quote api->quotes: %s\n" % e)
            tryNo += 1
            time.sleep(1)
            if tryNo == 5:
                return e


def loadTokenData():
    url = "https://lapi.kotaksecurities.com/wso2-scripmaster/v1/prod/" + "2024-01-21" + "/transformed/nse_fo.csv"
    response = urlopen(url)
    inst = pd.read_csv(response, sep=",")
    column_mapping = {'pSymbolName': 'instrumentName', 'pTrdSymbol': 'symbol', 'pSymbol': 'token'}
    inst.rename(columns=column_mapping, inplace=True)
    inst["expiry"] = inst.symbol.str[9:14]
    return inst


def dump(obj, name):
    fileObj = open(name + '.obj', 'wb')
    pickle.dump(obj, fileObj)
    fileObj.close()


def load(name):
    dbfile = open(name + '.obj', 'rb')
    db = pickle.load(dbfile)
    dbfile.close()
    return db


def placeOrder(users, instrument_token, instrument_symbol, transaction_type, premium, quantity):
    for user in users:
        user.order(instrument_token, instrument_symbol, transaction_type, premium, quantity)
