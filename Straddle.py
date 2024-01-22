from Leg import *
import runLive


class STRADDLE:
    def __init__(self,transactionType):
        self.ce = LEG("CE", transactionType)
        self.pe = LEG("PE", transactionType)
        self.realizedProfit = 0
        self.strikeStack = []
        self.mean=[]
        self.buy = True if transactionType == "buy" else False

    def getProfit(self, priceDict):
        return self.ce.getLegProfit(priceDict) + self.pe.getLegProfit(priceDict)

    def setupStraddle(self, atm, client, tokenData, priceDict):
        self.ce.exp_date = runLive.getExpDate(tokenData)
        self.pe.exp_date = runLive.getExpDate(tokenData)
        symbolce = self.ce.getStrike(initialPremium, atm, tokenData, client)
        symbolpe = self.pe.getStrike(initialPremium, atm, tokenData, client)
        self.ce.setLegPars(symbolce, tokenData, priceDict, client)
        self.pe.setLegPars(symbolpe, tokenData, priceDict, client)
        self.strikeStack = []
        self.mean.append(atm)

    def adjust(self, priceDict, spot, tokenData, client):
        cestrike = self.ce.reExecute(priceDict, tokenData, client) if self.pe.currentAdjustmentLevel==0 else 0
        pestrike = self.pe.reExecute(priceDict, tokenData, client) if self.ce.currentAdjustmentLevel==0 else 0
        if cestrike:
            self.strikeStack.append(cestrike)
            self.mean.append(spot)
        elif pestrike:
            self.strikeStack.append(pestrike)
            self.mean.append(spot)

    def reEnter(self, priceDict, spot, tokenData, client):
        if self.ce.currentAdjustmentLevel >= 1 and spot < self.mean[-2]:
            self.mean.pop()
            self.pe.updatePremium(priceDict)
            self.ce.reEnter(priceDict, self.strikeStack.pop(), tokenData, client)
            print("after rematch the premiums are, ce - {}, pe - {}".format(self.ce.premium, self.pe.premium))
        elif self.pe.currentAdjustmentLevel >= 1 and spot > self.mean[-2]:
            self.mean.pop()
            self.ce.updatePremium(priceDict)
            self.pe.reEnter(priceDict, self.strikeStack.pop(), tokenData, client)
            print("after rematch the premiums are, ce - {}, pe - {}".format(self.ce.premium, self.pe.premium))

    def exit(self, priceDict):
        profit = self.getProfit(priceDict)
        self.ce.flush()
        self.pe.flush()
        self.realizedProfit = 0
        self.strikeStack = 0
        return profit

    def refreshData(self, tokenData):
        self.ce.exp_date = getExpDate(tokenData)
        self.ce.refreshData(tokenData)
        self.pe.exp_date = getExpDate(tokenData)
        self.pe.refreshData(tokenData)


def getExpDate(tokenData):
    exp_date = tokenData.iloc[0]["symbol"][5:12]
    if len(exp_date) <= 3:
        exp_date = tokenData.iloc[-1]["symbol"][5:12]
    return exp_date
