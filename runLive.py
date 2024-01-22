import calendar
from datetime import datetime, timedelta

from strategy import Strategy
import liveUtils


def formatDate(date):
    return date[-2:] + calendar.month_abbr[int(date[-5:-3])].upper() + date[2:4]


def getTokenDataDateFromat(date):
    map = {10: "O", 11: "N", 12: "D"}
    mid = map[date[5:7]] if date[5:7] in map else date[6:7]
    return date[2:4]+mid+date[-2:]



def getExpDate(tokenData):
    expDates = tokenData[tokenData.instrumentName.str.contains("BANKNIFTY")].expiry.unique()
    for i in range(7):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        if getTokenDataDateFromat(date) in expDates:
            return date
    return datetime.now().strftime("%Y-%m-%d")[2:4]+calendar.month_abbr[int(datetime.now().strftime("%Y-%m-%d")[5:7])].upper()


class Live:
    def __init__(self, client, indexToken):
        self.tokenData = liveUtils.loadTokenData()
        self.price = {}
        self.indexToken = indexToken
        self.client = client
        self.expDate = getExpDate(self.tokenData)
        self.currentDate = formatDate(datetime.now().strftime("%Y-%m-%d"))
        self.strategy = Strategy("sell")
        self.strategy.tokenData = self.tokenData

    def callback_method(self, client, message):
        print(message)
        for el in message:
            self.price[el['tk']] = el['ltp']
        if not self.strategy.started and datetime.now().strftime("%H:%M:%S") >= "00:00:00":
            self.strategy.start(client, self.price[self.indexToken], self.price)
        elif self.currentDate == self.expDate and datetime.now().strftime("%H:%M:%S") >= "15:29:00":
            self.strategy.end(self.price)
        elif self.strategy.started:
            self.strategy.piyushAdjustment(self.price[self.indexToken], self.price)
