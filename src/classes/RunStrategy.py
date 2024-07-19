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
        
    def syncTransactions(self, type='B'):
        '''
        @TODO Override this method in child class to sync Transactions with Broker
        '''
        dbConn = DBConnector(self.isBackTesting)
        getPendingTxn = dbConn.executeRawQuery('''SELECT st.id, s.id, s.name, s.nseCode, st.price, st.quantity FROM stocksTxn as st INNER JOIN stocks as s WHERE st.stockId=s.id AND st.syncStatus=0 AND st.holdingStatus="'''+type+'"')
        return getPendingTxn
            
    def run(self):
        self._strategy.selectStocks()
        self._strategy.triggerBuyStock()
        self.syncTransactions('B')
        self._strategy.triggerSellStock()
        self.syncTransactions('S')
        
        txn = self._strategy.getOnHoldTransactions()
       
        return txn            
            
    def generateReport(self):
        pass