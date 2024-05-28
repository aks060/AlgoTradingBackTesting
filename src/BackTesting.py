from classes.RunStrategy import *

class BackTesting():
    isBackTesting = True
    __runStrategyObj = None
    __testConfigs = dict()
    __result = list()
    
    def __init__(self, strategyName, testConfigs=None) -> None:
        self.__testConfigs = testConfigs
        iniBalance = 0.0
        if 'initialBalance' in testConfigs:
            iniBalance = testConfigs['initialBalance']
        self.__runStrategyObj = RunStrategy(strategyName, iniBalance)
        
    def run(self):
        '''@TODO: Implement this method'''
        pass
    
    def getResult(self) -> list:
        return self.__result