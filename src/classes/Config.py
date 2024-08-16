import json, sqlite3, os, sys, requests, copy

class Config():
    '''
    Config class to set configuration files, secret file, initializing database and brocker session.
    \nInstantiation of this class is restricted.
    '''
    __configFilePath=os.path.dirname(os.path.abspath(sys.argv[0]))+'/'+"config.json"
    __secretFilePath=os.path.dirname(os.path.abspath(sys.argv[0]))+'/'+"secret.json"
    __stockDB = 'stocks.db'
    __backtestingDB = 'backtestingStocks.db'
    __configValues = {}
    __secretValues = {}
    __dbConnections = list()
    __brokerSession = requests.session()
    
    # To restrict object creation, self is removed from parameter
    def __init__() -> None:
        raise Exception("Object cannot be created for Config class")
    
    @staticmethod
    def setupEnvironment(isBacktesting = False):
        return (copy.deepcopy(Config.getBrokerSession()), Config.getDBCursors(isBacktesting))
    
    @staticmethod
    def setConfigFiles(configFilePath=None, secretFilePath=None):
        if configFilePath is not None:
            Config.__configFilePath = configFilePath
        if secretFilePath is not None:
            Config.__secretFilePath = secretFilePath
        Config.__loadConfigurations()
        
    @staticmethod
    def getConfigValues(index):
        Config.__loadConfigurations()
        if index not in Config.__configValues:
            return None
        else:
            return Config.__configValues[index]
    
    @staticmethod
    def getDBCursors(isBackTesting = False):
        Config.__initDBConnections()
        if not isBackTesting:
            return (Config.__dbConnections[0].cursor(), Config.__dbConnections[0])
        else:
            return (Config.__dbConnections[1].cursor(), Config.__dbConnections[1])
    
    @staticmethod
    def __loadConfigurations():
        config = open(Config.__configFilePath, 'r')
        Config.__configValues = json.loads(config.read())
        config.close()
        secret = open(Config.__secretFilePath, 'r')
        Config.__secretValues = json.loads(secret.read())
        
    @staticmethod
    def __initDBConnections():
        stockDB = sqlite3.connect(Config.__stockDB)
        backTestDB = sqlite3.connect(Config.__backtestingDB)
        Config.__dbConnections = [stockDB, backTestDB]
        
    @staticmethod
    def getBrokerSession():
        Config.__loadConfigurations()
        username = Config.__secretValues['Broker']['username']
        password = Config.__secretValues['Broker']['password']
        url = Config.__secretValues['Broker']['url']
        
        # TODO: Implement Broker Session
        # eg: req = Config.__brokerSession.post(url)
        
    