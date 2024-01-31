from datetime import datetime

import liveUtils
from Utils import *


def getOppTransaction(transactionType):
    return "sell" if transactionType == "buy" else "buy"


class LEG:

    def __init__(self, type, transactionType):
        self.type = type
        self.transactionType = transactionType
        self.Strike = None
        self.exp_date = None
        self.premium = None
        self.token = None
        self.currentAdjustmentLevel = 0
        self.realizedProfit = 0
        self.noOfAdjustments = 1
        self.shift = strikeDifference if type == "CE" else -strikeDifference
        self.hedge = None

    def getStrike(self, premiumTarget, atm, tokenData, client):
        """
        fetches the strike which has premium closest to premium target.
        :param premiumTarget: always less than self.premium.
        :param bankNiftyData:
        :param time:
        :return: symbol eg. BANKNIFTY29NOV40000CE
        """
        intialStrike = atm if atm else int(self.Strike)
        newStrike = intialStrike
        while abs(intialStrike - newStrike) <= 8000:
            symbol = index + self.exp_date + str(newStrike) + self.type
            token = tokenData[tokenData.symbol == symbol]["token"].iloc[0]
            premium = 0
            try:
                premium = liveUtils.getQuote(token, client)
            except Exception as e:
                print(e)
            if premium < premiumTarget:
                self.premium = premium
                return symbol
            newStrike = newStrike + self.shift

    def setLegPars(self, symbol, tokenData, priceDict, client):
        if self.token:
            liveUtils.order(client, self.token, getOppTransaction(self.transactionType), 1)
        self.Strike = symbol[-7:-2]
        self.token = tokenData[tokenData.symbol == symbol]["token"].iloc[0]
        self.premium = liveUtils.getQuote(self.token, client)
        if self.transactionType == "sell":
            self.setHedge(priceDict, 20, tokenData, client)
        liveUtils.order(client, self.token, self.transactionType, 1)
        print(self.type + " parameters set with strike {} and premium {}".format(self.Strike, self.premium), )

    def getLegProfit(self, priceDict):
        if self.hedge:
            return self.realizedProfit + self.getLegUnRealizedProfit(priceDict) + self.hedge.getLegProfit(priceDict)
        else:
            return self.realizedProfit + self.getLegUnRealizedProfit(priceDict)

    def getLegUnRealizedProfit(self, priceDict):
        try:
            if self.premium and self.transactionType == "sell":
                return self.premium - priceDict[self.token]
            elif self.premium and self.transactionType == "buy":
                return priceDict[self.token] - self.premium
            else:
                return 0
        except Exception as e:
            print("exception occurred", e)
            return self.premium

    def flush(self):
        self.Strike = None
        self.exp_date = None
        self.premium = 0
        self.token = None
        self.currentAdjustmentLevel = 0
        self.realizedProfit = 0
        self.hedge = None

    def reExecute(self, priceDict, tokenData, client):
        """
        when the current leg hits SL we do an adjustment in the leg to a farther strike
        :param client:
        :param priceDict:
        :param tokenData:
        :return:
        """
        if self.getLegUnRealizedProfit(priceDict) < - SLMap[self.currentAdjustmentLevel] * self.premium:
            initialStrike = self.Strike
            print(self.type + " leg adjustment at ", datetime.now())
            self.realizedProfit += self.getLegUnRealizedProfit(priceDict)
            if self.currentAdjustmentLevel == self.noOfAdjustments:
                self.exit(client)
                self.premium = 0
                self.currentAdjustmentLevel += 1
                self.hedge.realizedProfit += self.hedge.getLegUnRealizedProfit(priceDict)
                self.hedge.premium = 0
                return int(initialStrike)
            else:
                symbol = self.getStrike(adjustmentPercent * self.premium, None, tokenData, client)
                self.setLegPars(symbol, tokenData, priceDict, client)
                # self.setHedge(priceDict, 20, tokenData)
                self.currentAdjustmentLevel += 1
                return int(initialStrike)
        return 0

    def reEnter(self, priceDict, straddleCentre, tokenData, client):
        """
        when the spot price comes back to the intial straddle or strangle price we do a reentry.
        :param time:
        :param straddleCentre:
        :param bankNiftyData:
        :return:
        """
        if straddleCentre:
            print(self.type + " leg rematch at ", datetime.now())
            self.realizedProfit += self.getLegUnRealizedProfit(priceDict)
            symbol = index + self.exp_date + str(straddleCentre) + self.type
            self.setLegPars(symbol, tokenData, priceDict, client)
            # self.setHedge(priceDict, 20, tokenData)
            self.currentAdjustmentLevel -= 1
            return 0

    def setHedge(self, priceDict, hedgeDist, tokenData, client):
        transactionType = "buy" if self.transactionType == "sell" else "sell"
        self.hedge = LEG(self.type, transactionType) if not self.hedge else self.hedge
        self.hedge.type = self.type
        if hedgeDist > 10:
            hedgestrike = str(round((int(self.Strike) + hedgeDist * self.shift) / 500) * 500)
        else:
            hedgestrike = str(int(self.Strike) + hedgeDist * self.shift)
        symbol = index + self.exp_date + hedgestrike + self.type
        self.hedge.realizedProfit += self.hedge.getLegUnRealizedProfit(priceDict)
        print("hedge", end=" ")
        self.hedge.setLegPars(symbol, tokenData, priceDict, client)

    def updatePremium(self, priceDict):
        self.realizedProfit += self.getLegUnRealizedProfit(priceDict)
        self.premium = priceDict[self.token]

    def exit(self, client):
        print("exiting leg")
        liveUtils.order(client, self.token, getOppTransaction(self.transactionType), 1)
        self.hedge.exit(client)
