from StockData import *
from StrategyUtils import *
import copy, time

class Strategy():
    isBackTesting = False
    _strategyName = ''
    _initialBalance = 0.0
    _currentBalance = 0.0
    _stocksList = list()
    _transactionHistory = list()       # {'name', 'nseCode', 'qnt', 'price', 'total', 'txnType', 'date'}
    _PLHistory = list()
    _aditionalParameters = dict()
    _dbConnector = None
    _configParams = None
    _strategyId = -1
    
    def __init__(self, strategyName:str, initialBalance) -> None:
        self._strategyName = strategyName
        self._initialBalance = float(initialBalance)
        self._currentBalance = self._initialBalance
        
    def get_StrategyName(self):
        return self._strategyName
    
    def get_strategyId(self):
        return self._strategyId
    
    def get_currentBalance(self):
        return self._currentBalance
    
    def get_stocksList(self):
        return copy.deepcopy(self._stocksList)
    
    def get_transactionHistory(self):
        return copy.deepcopy(self._transactionHistory)
    
    def get_PLHistory(self):
        return copy.deepcopy(self._PLHistory)
        
    def _setBalance(self, newBalance: float):
        self._currentBalance = newBalance
        
    def _addProfit(self, profitAmount: float):
        self._currentBalance += profitAmount
        self._PLHistory.append({"amount": profitAmount, "type": "P"})
        
    def _addLoss(self, lossAmount:float):
        self._currentBalance -= lossAmount
        self._PLHistory.append({"amount": lossAmount, "type": "L"})
        
    def _updateStockList(self, newStockList: list):
        '''
        Provide stock list manually to the strategy.
        '''
        self._stocksList = newStockList
        
    def configParams(self, *args):
        raise Exception("Method not implemented, Please overwrite this method")
        pass
    
    def selectStocks(self, *args):
        '''
        This method will fetch and select the stocks from APIs based on the conditions met for the strategy.
        '''
        raise Exception("Method not implemented, Please overwrite this method")
        pass
    
    def triggerBuyStock(self, *args):
        raise Exception("Method not implemented, Please overwrite this method")
        pass
    
    def triggerSellStock(self, *args):
        raise Exception("Method not implemented, Please overwrite this method")
        pass
    
    def cleanData(self):
        if not self.isBackTesting:
            inp = input('You are trying to delete production data. Are you sure? (Type `sure`)')
            if inp == 'sure':
                self._dbConnector.executeRawQuery('''DELETE FROM stocksTxn WHERE strategy='''+str(self._strategyId), False)
            else:
                print('Skipping deletion')
                return True
        else:
            self._dbConnector.executeRawQuery('''DELETE FROM stocksTxn WHERE strategy='''+str(self._strategyId), False)


class SampleStrategy(Strategy):
    
    _strategyName = 'SampleStrategy'
    
    def __init__(self, initialBalance: float) -> None:
        super().__init__(self._strategyName, initialBalance)
        
    def configParams(self, *args):
        pass
    
    def selectStocks(self, *args):
        largeCapStocks = StockData.getStocksFromChartInk("(+{cash}+(+market+cap+>+10000+)+)+")
        self._stocksList = largeCapStocks['data']
                
    def triggerBuyStock(self, *args):
        # Buy stock is price is less than 1000
        for i in self.__stocksList:
            nseCode = i['nseCode']
            name = i['name']
            price = i['close']
            qnt = 1
            if float(price) < 1000 and self._currentBalance>0:
                cost = qnt*price
                self._transactionHistory.append({'name': name, 'nseCode': nseCode, 'qnt': qnt, 'price': price, 'total': cost, 'txnType': 'B'})                
                self._currentBalance -= cost
            
    def triggerSellStock(self, *args):
        # Sell stocks already in hold if profit min 5% and set SL at 2%, no shorting
        loop = False
        if 'keepRunning' in args:
             loop = True
        pass
    
    
class WeekHigh52(Strategy):
    '''
    Config Params:
        stopLossPercent:float
        targetPercent:float
        marketCap:int  (in Crores)
    '''
    
    _strategyName = 'WeekHigh52'
    _stockData = StockData()
    _stopLossPercent = 30
    _targetPercent = 60
    _marketCap = 1000
    _strategyId = 3
    _txnDBEntry = dict()
    _maxBuyLimitPerStock = 1000
    
    def __init__(self, initialBalance: float, isBackTesting=False) -> None:
        super().__init__(self._strategyName, initialBalance)
        self.isBackTesting = isBackTesting
        self._dbConnector = DBConnector(isBackTesting)
        WeekHigh52._strategyId = self._dbConnector.selectDataFromTable('strategy', 'name="'+WeekHigh52._strategyName+'"')[0][0]
        
    def configParams(self, *args):
        configParam = args[0]
        if configParam is None:
            self._configParams = configParam
            return
        # print(configParam[0])
        if self._configParams is None:
            self._configParams = configParam
        else:
            self._configParams.update(configParam)
        if 'stopLossPercent' in configParam:
            self._stopLossPercent = configParam['stopLossPercent']
        if 'targetPercent' in configParam:
            self._targetPercent = configParam['targetPercent']
        if 'marketCap' in configParam:
            self._marketCap = configParam['marketCap']
        if 'stockList' in configParam:
            self._stocksList = configParam['stockList']
        if 'maxBuyLimitPerStock' in configParam:
            self._maxBuyLimitPerStock = configParam['maxBuyLimitPerStock']
    
    def selectStocks(self, *args):
            weekhigh52 = self._stockData.getStocksFromChartInk("(+{cash}+(+weekly+max(+52+,+weekly+high+)+<=+latest+low+and+market+cap+>=+"+str(self._marketCap)+"+)+)+")
            self._stocksList = weekhigh52['data']
        
    def getOnHoldTransactions(self):
        return self._dbConnector.executeRawQuery('''SELECT st.*, s.* FROM stocksTxn st INNER JOIN stocks s ON st.stockId=s.id WHERE st.status='Hold' AND st.strategy='''+str(self._strategyId), True)[1]
        
    def __addTransactionToDB(self, stockName, nseCode, holdingStatus, price, qnt, stopLoss, targetPrice, status, txnTime=None):
        self._dbConnector.addStocks(stockName, nseCode)
        stockID = self._dbConnector.selectDataFromTable('stocks', 'nseCode = "'+nseCode+'"')[0][0]
        self._dbConnector.addStocksTxn(stockID, holdingStatus, price, qnt, stopLoss, self._stopLossPercent, targetPrice, self._targetPercent, status, self._strategyId, txnTime)
        txnId = self._dbConnector.selectDataFromTable('stocksTxn', 'stockId = "'+str(stockID)+'" AND holdingStatus="'+holdingStatus+'" AND price="'+str(price)+'" AND quantity="'+str(qnt)+'" AND strategy="'+str(self._strategyId)+'" AND status="'+status+'"')[0][0]   
        return txnId
    
    def triggerBuyStock(self, *args):
        data = None
        if len(args)>0:
            data = args[0]
        if data is not None and 'stockList' in data and 'currentTime' in data['stockList']:
            currentTime = data['stockList']['currentTime']
        else:
            currentTime = int(time.time())
        # Buy stock is price is less than 1000
        for i in self._stocksList:
            nseCode = i['nsecode']
            name = i['name']
            price = i['close']
            qnt = 1
            if 'currentTime' in i:
                currentTime = i['currentTime']
            if float(price) < self._maxBuyLimitPerStock and self._currentBalance>0:
                print("Purchasing Stock...")
                if self._configParams is not None and 'buyMaxLimit' in self._configParams and self._configParams['buyMaxLimit']:
                    qnt = int(self._maxBuyLimitPerStock/price)
                cost = qnt*price
                self._currentBalance -= cost
                stopLoss = price - (self._stopLossPercent/100)*price
                targetPrice = price + (self._targetPercent/100)*price
                txnId = self.__addTransactionToDB(name, nseCode, 'B', price, qnt, stopLoss, targetPrice, 'Hold', currentTime)
                self._transactionHistory.append({'txnId': txnId, 'name': name, 'nseCode': nseCode, 'qnt': qnt, 'price': price, 'total': cost, 'txnType': 'B', 'status': 'Hold', 'date': currentTime})                
                if nseCode not in self._txnDBEntry:
                    self._txnDBEntry[nseCode] = list()
                self._txnDBEntry[nseCode].append(txnId)
            elif self._currentBalance <= 0:
                print("BALANCE IS OVER.. Cannot BUY MORE STOCKS")
                        
            
    def triggerSellStock(self, *args):
        # Sell stocks already in hold if profit min 5% and set SL at 2%, no shorting
        '''
            Conditions:
            1. Run scanner at 3 PM
            2. Cost > 52 week high
            3. Fixed stop loss = 30%
            4. Fix Target = 60%
            5. Trailing stop loss = last 10th week low
        '''
        data = None
        if len(args)>0:
            data = args[0]
        strategyTxn = self._dbConnector.executeRawQuery('''
        SELECT st.id, st.stockId, st.txnDate, st.txnTime, st.holdingStatus, 
        st.price, st.quantity, st.strategy, st.stopLoss, st.stopLossPercent,
        st.targetPrice, st.targetPercent, st.status, st.enable, st.syncStatus, 
        s.name, s.nseCode
        FROM stocksTxn st INNER JOIN stocks s ON st.stockId=s.id WHERE st.status='Hold' AND st.holdingStatus='B' AND st.strategy='''+str(self._strategyId), True)[1]
        for i in strategyTxn:
            txnId = i[0]
            nseCode = i[16]
            
            name = i[15]
            price = i[5]
            qnt = i[6]
            currentStopLoss = i[8]
            stopLossPercent = i[9]
            targetPrice = i[10]
            targetPricePercent = i[11]
            if data is not None and 'currentTime' in data:
                currentTime = data['currentTime']
            else:
                currentTime = int(time.time())
            get10WeekLow = StrategyUtils.getLow(nseCode, 10, '1W', currentTime)
            latestCloseData = self._stockData.getStockDataFromApi(nseCode, currentTime, '1D')
            if len(latestCloseData) ==0:
                latestClose = 0
                #Error
            else:
                latestClose = latestCloseData[-1][4]
            if currentStopLoss >= latestClose:
                print("Stop Loss already triggered")
                self._currentBalance+=(currentStopLoss*qnt)
                self._transactionHistory.append({'txnId': txnId, 'name': name, 'nseCode': nseCode, 'qnt': qnt, 'price': currentStopLoss, 'total': currentStopLoss*qnt, 'txnType': 'S', 'status': 'Hold', 'date': currentTime})                
                self._dbConnector.executeRawQuery("UPDATE stocksTxn SET holdingStatus='S', status='Executed' WHERE id="+str(txnId))
            
            # Check if stock is increasing, update the stopLoss as well.
            newCalculatedStopLoss = latestClose - (stopLossPercent/100)*latestClose
            newStopLoss = max(get10WeekLow, max(currentStopLoss, newCalculatedStopLoss))
            
            # Check if stock broke the target Price as well, set stopLoss to 1% less than Target Price
            if latestClose > targetPrice:
                newStopLoss = max(newStopLoss, targetPrice - 0.01*targetPrice)
            
            if currentStopLoss!= newStopLoss:
                self._dbConnector.executeRawQuery("UPDATE stocksTxn SET stopLoss ='"+str(newStopLoss)+"', status='Hold', syncStatus='False' WHERE id="+str(txnId))
                    
registeredStrategy = {'SampleStrategy' : SampleStrategy, 'WeekHigh52' : WeekHigh52}