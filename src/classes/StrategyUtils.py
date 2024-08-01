from StockData import *
import time
class StrategyUtils():
    
    @staticmethod
    def calculateMA(pricelist, days=50):
        sum = 0
        count = 0
        for i in pricelist[::-1]:
            if count >= days:
                break
            sum += i[4]
            count += 1
        return round(sum / days, 2)
    
    @staticmethod
    def getLow(symbol:str, interval:int, intervalType:str, currentTime=None, cacheEnabled = True):
        sd = StockData()
        if currentTime is None:
            currentTime = int(time.time())
        stockData = sd.getStockDataFromApi(symbol, currentTime, intervalType, {'cacheEnabled': cacheEnabled})
        if len(stockData) < interval:
            return -1
        lowData = stockData[-interval][3]
        return lowData
    
    @staticmethod
    def get52WeekHigh(*args):
        data = args[0]
        minExpectedLength = 52*5
        symbol = None
        interval = None
        intervalType = '1D'
        highData = -1
        stockData = None
        parsingType = 'CloseData'
        
        if 'symbol' in data:
            symbol = data['symbol']
        if 'interval' in data:
            interval = data['interval']
        if 'intervalType' in data:
            intervalType= data['intervalType']
        if 'stockData' in data:
            stockData = data['stockData']
            parsingType = 'FullData'
        if 'stockCloseData' in data:
            stockData = data['stockCloseData']
            parsingType = 'CloseData'
            
        if symbol is not None and interval is not None and intervalType is not None:
            sd = StockData()
            currentTime = int(time.time())
            stockData = sd.getStockDataFromApi(symbol, currentTime, intervalType)
            highData = stockData[-interval][3]
        elif stockData is not None and parsingType=='FullData':
            for i in stockData[len(stockData)-minExpectedLength:]:
                if i[0] == 0:
                    return -1
                # picking index as 2 for highest of the day
                highData = max(highData, i[2])
        elif stockData is not None and parsingType=='CloseData':
            for i in stockData[len(stockData)-minExpectedLength:]:
                if i[0] == 0:
                    return -1
                highData = max(highData, i)
        return highData
                