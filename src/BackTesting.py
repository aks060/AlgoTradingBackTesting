from classes.RunStrategy import *
import time, random, os, tempfile, shutil

class BackTesting(RunStrategy):
    isBackTesting = True
    __testConfigs = dict()
    __result = list()
    __doWait = True
    __startDate = None
    __endDate = None
    __useCache = False
    __stockData = StockData(isBackTesting=True)
    
    def __init__(self, strategyName, testConfigs=None) -> None:
        self.__testConfigs = testConfigs
        iniBalance = 0.0
        if 'initialBalance' in testConfigs:
            iniBalance = self.__testConfigs['initialBalance']
        if 'startDate' in testConfigs:
            self.__startDate = testConfigs['startDate']
        if 'endDate' in testConfigs:
            self.__endDate = testConfigs['endDate']
        if 'marketCap' in testConfigs:
            self._marketCap = testConfigs['marketCap']
        if 'stockList' in testConfigs:
            self._stocksList = testConfigs['stockList']
        if 'noWait' in testConfigs:
            self.__doWait = False
        if 'useCache' in testConfigs:
            self.__useCache = testConfigs['useCache']
        if not self.__useCache:
            if os.path.exists(tempfile.gettempdir()+'/AlgoTradingBackTesting'):
                shutil.rmtree(tempfile.gettempdir()+'/AlgoTradingBackTesting')
            os.mkdir(tempfile.gettempdir()+'/AlgoTradingBackTesting')
        else:
            self.__doWait = False
        super().__init__(strategyName, iniBalance, testConfigs)
        self.isLive = False
        
    def __selectStocks(self):
        return self.__stockData.getStocksFromChartInk("(+{cash}+(+market+cap+>=+"+str(self._marketCap)+"+)+)+")
    
    def __fetchStockData(self, stockList):
        currentTime = int(time.time())
        stockPriceTimeline = {}
        stockListData = stockList['data']
        count =1
        maxDataLen = 0
        timeLine=set()
        maxDataLenStock = None
        for i in stockListData:
            print(str(count)+"/"+str(stockList['recordsFiltered'])+" Getting data for "+i['nsecode']+"...")
            data = self.__stockData.getStockDataFromApi(i['nsecode'], currentTime, '1D', {"cacheEnabled": True})
            if len(data) == 0:
                print("No data found. Skipping...")
                continue
            if len(data) > maxDataLen:
                maxDataLenStock = i['nsecode']
            maxDataLen = max(maxDataLen, len(data))
            startTime = data[0][0]
            print("Got data from "+str(time.strftime('%d-%m-%Y', time.localtime(startTime))))
            stockPriceTimeline[i['nsecode']] = {'name': i['name'], 'nsecode': i['nsecode'], 'data': data}          
            print()
            count+=1
            if self.__doWait:
                time.sleep(random.random())
        return (stockPriceTimeline,maxDataLen)
        
        
    def run(self):
        self._strategy.cleanData()
        stockList = self.__selectStocks()
        stockListData = stockList['data']
        print("Found total "+str(stockList['recordsFiltered'])+" records")
        print("Getting data for each stock... \n")
        stockPriceTimeline, maxDataLen = self.__fetchStockData(stockList)       
        for i in range(52*5, maxDataLen):
            print("Running for loop "+str(i)+".. Total left: "+str(maxDataLen-1-i))
            strategyData = []
            week10thLow = {}
            currentTime = None
            for j in stockPriceTimeline.items():
                if len(j[1]['data']) < maxDataLen:
                    padLen = maxDataLen - len(j[1]['data'])
                    stockPriceTimeline[j[0]]['data'] = [[0,0,0,0,0,0]]*padLen + stockPriceTimeline[j[0]]['data']
                    j[1]['data']=stockPriceTimeline[j[0]]['data']
                currentTime = j[1]['data'][i][0]
                if currentTime == 0:
                    continue
                stockData = {'nsecode': j[1]['nsecode'], 'name': j[1]['name'], 'close': j[1]['data'][i][4], 'currentTime': currentTime}
                close52WeekHigh = StrategyUtils.get52WeekHigh({'stockData': j[1]['data'][:i+1]})
                if j[1]['data'][i][4] >= close52WeekHigh and close52WeekHigh>0:
                    strategyData.append(stockData)
            try:
                self._strategy.triggerSellStock({'currentTime': currentTime})
                self._strategy.configParams({'stockList': strategyData})
                self._strategy.triggerBuyStock({'stockList': strategyData})
            except Exception as e:
                print(e)
                raise e
                    
                
    def getResult(self) -> list:
        return self._strategy.get_transactionHistory()