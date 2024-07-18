from Strategy import *

class RunStrategy():
    isBackTesting = False
    _strategy = None
    __stockData = list()
    isLive = False                 # Set it to True if System is Live
    
    def __init__(self, strategyName, initialBalance, configParams=None, stockData=None, startDate=None, endDate=None):
        if configParams is not None:
            if 'isBackTesting' in configParams:
                self.isBackTesting = configParams['isBackTesting']
            if 'noWait' in configParams:
                self.__doWait = False
            if 'isLive' in configParams:
                self.isLive = configParams['isLive']
            else:
                self.isLive = False
        if stockData is not None:
            self.__stockData = stockData
            self._strategy._updateStockList(stockData)
        self._strategy = registeredStrategy[strategyName](initialBalance, self.isBackTesting)
        self._strategy.configParams(configParams)
            
    def run(self):
        self._strategy.selectStocks()
        self._strategy.triggerBuyStock()
        self._strategy.triggerSellStock()
        
        txn = self._strategy.getOnHoldTransactions()
        
        if self.isLive:
            for i in txn:
                # TODO: Add logic to execute transactions using Broker API here.
                pass
        
        return txn            
            
    def generateReport(self):
        pass