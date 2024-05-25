class Strategy():
    isBackTesting = False
    __strategyName = ''
    __initialBalance = 0.0
    __currentBalance = 0.0
    __stocksList = list()
    __transactionHistory = list()
    __PLHistory = list()
    __aditionalParameters = dict()
    
    def __init__(self, strategyName:str, initialBalance:float) -> None:
        self.__strategyName = strategyName
        self.__initialBalance = initialBalance
        
    def _setBalance(self, newBalance: float):
        self.__currentBalance = newBalance
        
    def _addProfit(self, profitAmount: float):
        self.__currentBalance += profitAmount
        self.__PLHistory.append({"amount": profitAmount, "type": "P"})
        
    def _addLoss(self, lossAmount:float):
        self.__currentBalance -= lossAmount
        self.__PLHistory.append({"amount": lossAmount, "type": "L"})
        
    def _updateStockList(self, newStockList: list):
        self.__stocksList = newStockList
        
    def configParams(self, *args):
        raise Exception("Method not implemented, Please overwrite this method")
        pass
    
    def selectStocks(self, *args):
        raise Exception("Method not implemented, Please overwrite this method")
        pass
    
    def triggerBuyStock(self, *args):
        raise Exception("Method not implemented, Please overwrite this method")
        pass
    
    def triggerSellStock(self, *args):
        raise Exception("Method not implemented, Please overwrite this method")
        pass
    
    
class SampleStrategy(Strategy):
    
    def __init__(self, strategyName: str, initialBalance: float) -> None:
        super().__init__(strategyName, initialBalance)
        
    def configParams(self, *args):
        pass
    
    def selectStocks(self, *args):
        pass
    
    def triggerBuyStock(self, *args):
        pass
    
    def triggerSellStock(self, *args):
        pass