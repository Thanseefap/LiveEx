from NorenRestApiPy.NorenApi import NorenApi
from neo_api_client import NeoAPI

import userDetails


def fetchDetails(id):
    return userDetails.users[id]


class User:
    def __init__(self, Id):
        self.userDetails = fetchDetails(Id)
        self.client = self.login()

    def login(self):
        if self.userDetails["broker"] == "shoonya":
            api = NorenApi(host='https://api.shoonya.com/NorenWClientTP/',
                                    websocket='wss://api.shoonya.com/NorenWSTP/')
            api.login(userid=self.userDetails["userid"], password=self.userDetails["password"], twoFA=input(), vendor_code=self.userDetails["vendorCode"], api_secret=self.userDetails["secret"], imei=self.userDetails["imei"])
            return api
        elif self.userDetails["broker"] == "kotakNeo":
            client = NeoAPI(consumer_key="q4RDblWAAJJ6udMrdIa9lS4IxGAa", consumer_secret="vQzreB9Z5NzLbMYA1t5I0kvnBYIa",
                            environment='Prod', on_message=None, on_error=None, on_close=None, on_open=None)
            client.login(mobilenumber="+919447497574", password="Haya@2020")
            client.configuration.edit_sid = "sid"
            client.configuration.edit_token = "token"
            # client.session_2fa(input())
            return client

    def order(self, instrument_token, instrument_symbol, transaction_type, premium, quantity):
        try:
            # if self.userDetails["broker"] == "kotakNeo":
            #     order_id = self.client.place_order(exchange_segment="nse_fo", product="NRML", price="", order_type="MKT", quantity=quantity, validity="DAY", trading_symbol="",
            #                transaction_type="", amo="", disclosed_quantity="", market_protection="", pf="", trigger_price="",
            #                tag="")
            #     print(transaction_type + " : " + str(instrument_symbol) + " at " + str(premium))
            #     return order_id
            # elif self.userDetails["broker"] == "shoonya":
            #     order_id = self.client.place_order(buy_or_sell='B', product_type='C',
            #             exchange='NSE', tradingsymbol='CANBK-EQ',
            #             quantity=1, discloseqty=0,price_type='SL-LMT', price=200.00, trigger_price=199.50,
            #             retention='DAY', remarks='my_order_001')
            print(transaction_type + " : " + str(instrument_symbol) + " at " + str(premium))
        except Exception as e:
            print("Exception when calling OrderApi->place_order: %s\n" % e)