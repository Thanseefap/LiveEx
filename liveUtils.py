import pickle
from datetime import datetime
from urllib.request import urlopen
import time as tm

from neo_api_client import NeoAPI
import pandas as pd


# on_message, on_open, on_close and on_error is a call back function we will provide the response for the subscribe method.
# access_token is an optional one. If you have barrier token then pass and consumer_key and consumer_secret will be optional.
# environment by default uat you can pass prod to connect to live server
def login(on_message, on_error):
    client = NeoAPI(consumer_key="q4RDblWAAJJ6udMrdIa9lS4IxGAa", consumer_secret="vQzreB9Z5NzLbMYA1t5I0kvnBYIa",
                    environment='Prod', on_message=on_message, on_error=on_error, on_close=None, on_open=None)
    client.login(mobilenumber="+919447497574", password="Haya@2020")
    # client.configuration.edit_sid = "sid"
    # client.configuration.edit_token = "token"
    client.session_2fa(input())
    return client


def getQuote(token, client):
    inst_tokens = [{"instrument_token": token, "exchange_segment": "nse_fo"}]
    try:
        # get LTP and Market Depth Data
        ltp = client.quotes(instrument_tokens=inst_tokens, quote_type="ltp", isIndex=False)

        # OR Quotes API can be accessed without completing login by passing session_token, sid, and server_id
        return ltp
    except Exception as e:
        print("Exception when calling get Quote api->quotes: %s\n" % e)




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


def connection():
    while "15:30:00" >= datetime.now().strftime("%H:%M:%S") >= "09:00:00":
        try:
            order(None, "BUY", 0, 0)
            tm.sleep(180)
        except:
            continue


def order(client, instrument_token, transaction_type, quantity):
    try:
        # order_id = client.place_order(exchange_segment="nse_fo", product="NRML", price="", order_type="MKT", quantity=quantity, validity="DAY", trading_symbol="",
        #            transaction_type="", amo="", disclosed_quantity="", market_protection="", pf="", trigger_price="",
        #            tag="")
        print(transaction_type + " : " + instrument_token)
        # return order_id
    except Exception as e:
        print("Exception when calling OrderApi->place_order: %s\n" % e)
