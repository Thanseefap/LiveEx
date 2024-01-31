import calendar
import time
from datetime import datetime, timedelta

import Utils
from strategy import Strategy
import liveUtils


def formatDate(date):
    return date[-2:] + calendar.month_abbr[int(date[-5:-3])].upper() + date[2:4]


def getTokenDataDateFromat(date):
    map = {10: "O", 11: "N", 12: "D"}
    mid = map[date[5:7]] if date[5:7] in map else date[6:7]
    return date[2:4] + mid + date[-2:]


def getExpDate(tokenData):
    expDates = tokenData[tokenData.instrumentName.str.contains("BANKNIFTY")].expiry.unique()
    for i in range(7):
        date = getTokenDataDateFromat((datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"))
        if date in expDates:
            return date
    return datetime.now().strftime("%Y-%m-%d")[2:4] + calendar.month_abbr[
        int(datetime.now().strftime("%Y-%m-%d")[5:7])].upper()


def getQuote(client, tokens):
    inst_tokens = [{"instrument_token": "26009", "exchange_segment": "mcx_fo"}]
    for el in tokens:
        inst_tokens.append({"instrument_token": el, "exchange_segment": "mcx_fo"})
    noOfTry = 0
    while noOfTry <= 5:
        # get LTP and Market Depth Data
        try:
            ltp = client.quotes(instrument_tokens=inst_tokens, quote_type="ltp", isIndex=False)["message"]
            if type(ltp) is not list:
                print(ltp)
                noOfTry += 1
                time.sleep(1)
                continue
            return ltp
        except Exception as e:
            print("Exception when calling get Quote api->quotes: %s\n" % e)
            noOfTry += 1
            time.sleep(1)


class Live:
    def __init__(self, client, indexToken):
        self.tokenData = liveUtils.loadTokenData()
        self.price = {}
        self.indexToken = indexToken
        self.expDate = getExpDate(self.tokenData)
        self.currentDate = formatDate(datetime.now().strftime("%Y-%m-%d"))
        self.strategy = Strategy("sell")
        self.strategy.tokenData = self.tokenData

    def callback_method(self, client):
        tokens = self.getAllTokens()
        message = getQuote(client, tokens)
        # print(datetime.now().strftime("%H:%M:%S"), end=" ")
        # print(message)
        for el in message:
            self.price[el['instrument_token']] = float(el['ltp'])
        if not self.strategy.started and datetime.now().strftime("%H:%M:%S") >= "00:00:00":
            self.strategy.start(client, self.price[self.indexToken], self.price)
        elif self.currentDate == self.expDate and datetime.now().strftime("%H:%M:%S") >= "15:29:00":
            self.strategy.end(self.price)
        elif self.strategy.started:
            self.strategy.piyushAdjustment(self.price[self.indexToken], self.price, client)

    def getAllTokens(self):
        return [self.strategy.straddle.ce.token, self.strategy.straddle.pe.token,
                self.strategy.straddle.ce.hedge.token, self.strategy.straddle.pe.hedge.token] if self.strategy.started else []