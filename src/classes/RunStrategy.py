from classes.Strategy import *

class RunStrategy():
    __strategy = None
    __stockData = list()
    __startDate = None
    __endDate = None
    
    def __init__(self, strategyName, initialBalance, configParams=None, stockData=None, startDate=None, endDate=None):
        self.__strategy = registeredStrategy[strategyName](strategyName, initialBalance)
        if configParams is not None:
            self.__strategy.configParams(configParams)
        if stockData is not None:
            self.__stockData = stockData
            self.__strategy._updateStockList(stockData)
        if startDate is not None:
            self.__startDate = startDate
        if endDate is not None:
            self.__endDate = endDate
            
    def generateReport(self):
        pass