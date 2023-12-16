import sys, time
sys.path.append(".")
        
        
#Strategy Classes

class WeekMonthBullishStock():
    
    __buyingPrice=None
    __currentPrice=None
    __date=None
    __stopLoss=0
    __stopLossPercent=7
    __targetPrice=None
    __targetPercent=None
    __nseSymbol=None
    
    def feedData(self, stockData) -> None:
        if 'date' in stockData:
            self.__date = stockData['date']
        if 'buyingPrice' in stockData:
            self.__buyingPrice = stockData['buyingPrice']
        if 'currentPrice' in stockData:
            self.__currentPrice = stockData['currentPrice']
        if 'targetPrice' in stockData:
            self.__targetPrice = stockData['targetPrice']
        if 'targetPercent' in stockData:
            self.__targetPercent = stockData['targetPercent']
        if 'stopLossPercent' in stockData:
            self.__stopLossPercent = stockData['stopLossPercent']
            self.__stopLoss = self.__currentPrice - ((self.__stopLossPercent/100)*self.__currentPrice)
        if 'stopLoss' in stockData:
            self.__stopLoss = stockData['stopLoss']
            self.__stopLossPercent = (self.__currentPrice - self.__stopLoss)*100/self.__currentPrice
        if 'nseSymbol' in stockData:
            self.__nseSymbol = stockData['nseSymbol']
            
    def shouldBuy(self, stockData) -> bool:
        if 'priceList' not in stockData:
            raise ValueError("PriceList params are required for shouldBuy function")
    
        if 'holdings' not in stockData or 'nseCode' not in stockData:
            raise ValueError("holdings and nseCode are required in stockData for shouldBuy function")
        
        #No Repeat Buy
        for i in stockData['holdings']:
            if stockData['nseCode'] == i['nseCode']:
                return (False, )
        
        currentPrice = self.__currentPrice
        day1Value = stockData['priceList'][-2][4]
        day2Value = stockData['priceList'][-3][4]
        week1Value = stockData['priceList'][-8][4]
        month1Value = stockData['priceList'][31][4]
        month3Value = stockData['priceList'][91][4]
        if ((currentPrice - float(day1Value))/float(day1Value))*100 >= float(stockData['percentChange']['daily']):
            # if ((currentPrice - float(day2Value))/float(day2Value))*100 >= float(stockData['percentChange']['daily']):
                if ((currentPrice - float(week1Value))/float(week1Value))*100 >= float(stockData['percentChange']['weekly']):
                    if ((currentPrice - float(month1Value))/float(month1Value))*100 >= float(stockData['percentChange']['monthly']):
                        if ((currentPrice - float(month3Value))/float(month3Value))*100 >= float(stockData['percentChange']['monthly']):
                            budget = stockData['budget']
                            qnt = budget//currentPrice
                            stopLossValue = currentPrice - (self.__stopLossPercent/100)*currentPrice
                            return (True, qnt, stopLossValue)
        return (False, )
    
    def getSL(self, stockData) -> float:
        if 'buyingPrice' in stockData:
            self.__buyingPrice = stockData['buyingPrice']
        if 'currentPrice' in stockData:
            self.__currentPrice = stockData['currentPrice']
        if 'stopLossPercent' in stockData:
            self.__stopLossPercent = stockData['stopLossPercent']
        if 'stopLossValue' in stockData:
            self.__stopLoss = stockData['stopLossValue']
        
        if self.__buyingPrice is None:
            print("Buying Price is not set..")
            return -1
        if self.__currentPrice is None:
            print("Current Price is not set..")
            return -1
        
        newCalculatedStopLoss = self.__currentPrice - ((self.__stopLossPercent/100)*self.__currentPrice)
        newStopLoss = max(newCalculatedStopLoss, self.__stopLoss)
        
        currentPrice = self.__currentPrice
        day1Value = stockData['priceList'][-1][4]
        day2Value = stockData['priceList'][-2][4]
        week1Value = stockData['priceList'][-8][4]
        month1Value = stockData['priceList'][31][4]
        month3Value = stockData['priceList'][91][4]
        
        if ((currentPrice - float(week1Value))/float(week1Value))*100 < float(stockData['percentChange']['weekly']) or \
            ((currentPrice - float(month1Value))/float(month1Value))*100 < float(stockData['percentChange']['monthly']) or \
            ((currentPrice - float(month3Value))/float(month3Value))*100 < float(stockData['percentChange']['monthly']):
                    newStopLoss = max(newStopLoss, currentPrice)
        return (newStopLoss, self.__stopLoss)