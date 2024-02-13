from datetime import datetime

import Straddle
import Utils


class Strategy:

    def __init__(self, transactionType):
        self.straddle = Straddle.STRADDLE(transactionType)
        self.mtm = 0
        self.tokenData = None
        self.SL = {"0": 0.3, "1": 1}
        self.rematchStack = []
        self.shift = 200
        self.currentAdjustmentLevel = 0
        self.noOfAdjustments = 1
        self.hedgeStrategyDirection = None
        self.started = False

    def start(self, client, spot, priceDict, users):
        print("trade started")
        self.straddle.setupStraddle(spot, client, self.tokenData, priceDict, users)
        print("straddle mean is ", self.straddle.mean)
        # self.straddle.ce.setHedge(priceDict, 20, self.tokenData)
        # self.straddle.pe.setHedge(priceDict, 20, self.tokenData)
        # self.hedgeAdjustment(spot, priceDict)
        self.started = True

    def end(self, client, priceDict, users):
        print("trade ended")
        self.started = False
        self.hedgeStrategyDirection = None
        return self.straddle.exit(client,priceDict, users)

    def piyushAdjustment(self, spot, priceDict, client, users):
        if datetime.now().strftime("%S") in ["00", "01"]:
            print(priceDict)
            print("mtm is {} ce premium is {}, pe premium is {}".format(round(self.straddle.getProfit(priceDict),2), self.straddle.ce.getLegUnRealizedProfit(priceDict), self.straddle.pe.getLegUnRealizedProfit(priceDict)))
            print("ce adjustment level - " + str(self.straddle.ce.currentAdjustmentLevel) + " pe adjustment level - " + str(self.straddle.pe.currentAdjustmentLevel))
        if Utils.oneSideFullHitFlag and (
                self.straddle.pe.currentAdjustmentLevel == Utils.noOfAdjustment + 1 or self.straddle.ce.currentAdjustmentLevel == Utils.noOfAdjustment + 1):
            return
        self.straddle.reEnter(priceDict, spot, self.tokenData, client, users)
        self.straddle.adjust(priceDict, spot, self.tokenData, client, users)

    def hedgeAdjustment(self, spot, priceDict):
        ce = self.straddle.ce.data
        pe = self.straddle.pe.data
        if self.hedgeStrategyDirection != "CE" and (
                (spot > float(self.straddle.mean) and int(priceDict[3:5]) % 5 == 4) or spot > float(
                self.straddle.mean) + Utils.strikeDifference / 4):
            print("hedge shifted to ce side")
            self.straddle.ce.setHedge(priceDict, 1, self.tokenData)
            self.straddle.pe.setHedge(priceDict, 20, self.tokenData)
            self.hedgeStrategyDirection = "CE"
            try:
                print("mtm is {}, spot is {}, ce premium is {}, pe premium is {}, hedge premium is {}, priceDict is {}"
                      .format(self.getMTM(priceDict), spot,
                              ce[ce.priceDict == priceDict]["close"].iloc[0],
                              pe[pe.priceDict == priceDict]["close"].iloc[0],
                              self.straddle.ce.hedge.data[self.straddle.ce.hedge.data.priceDict == priceDict][
                                  "close"].iloc[0], priceDict))
            except Exception as e:
                print(e)
        if self.hedgeStrategyDirection != "PE" and (
                (spot < float(self.straddle.mean) and int(priceDict[3:5]) % 5 == 4) or spot < float(
                self.straddle.mean) - Utils.strikeDifference / 4):
            print("hedge shifted to pe side")
            self.straddle.pe.setHedge(priceDict, 1, self.tokenData)
            self.straddle.ce.setHedge(priceDict, 20, self.tokenData)
            self.hedgeStrategyDirection = "PE"
            try:
                print("mtm is {}, spot is {}, ce premium is {}, pe premium is {}, hedge premium is {}, priceDict is {}"
                      .format(self.getMTM(priceDict), spot,
                              ce[ce.priceDict == priceDict]["close"].iloc[0],
                              pe[pe.priceDict == priceDict]["close"].iloc[0],
                              self.straddle.pe.hedge.data[self.straddle.pe.hedge.data.priceDict == priceDict][
                                  "close"].iloc[0], priceDict))
            except Exception as e:
                print(e)
        # temp = self.straddle.ce.hedge if self.hedgeStrategyDirection == "CE" else self.straddle.pe.hedge
        # print("mtm is {}, spot is {}, ce premium is {}, pe premium is {}, hedge premium is {} priceDict is {}"
        #       .format(self.getMTM(priceDict), spot,
        #               ce[ce.priceDict == priceDict]["close"].iloc[0], pe[pe.priceDict == priceDict]["close"].iloc[0],
        #               temp.data[temp.data.priceDict == priceDict]["close"].iloc[0], priceDict))

    def overNightHedge(self, priceDict):
        if self.hedgeStrategyDirection == "CE":
            self.straddle.pe.setHedge(priceDict, 3, self.tokenData)
        else:
            self.straddle.ce.setHedge(priceDict, 3, self.tokenData)

    def exitOverNightHedge(self, priceDict):
        if self.hedgeStrategyDirection == "CE":
            self.straddle.pe.setHedge(priceDict, 20, self.tokenData)
        else:
            self.straddle.ce.setHedge(priceDict, 20, self.tokenData)

    def checkForAdjustmentByPoints(self, priceDict):
        currentPrice = self.tokenData[self.tokenData.priceDict == priceDict]["close"]
        if currentPrice >= currentPrice + self.shift:
            return "up"
        if currentPrice <= currentPrice - self.shift:
            return "down"
        return None

    def refreshData(self):
        if self.started:
            print("refreshing data")
            self.straddle.refreshData(self.tokenData)

    def getMTM(self, priceDict):
        return round(self.straddle.getProfit(priceDict), 2)
