from Config import *
import time

class DBConnector():
    _selectedDBCursor = None
    _selectedDB = None
    _isBackTesting = False
    
    
    def __init__(self, isBackTesting = False) -> None:
        self._isBackTesting = isBackTesting
        self.selectDB(isBackTesting)
    
    def selectDB(self, isBackTesting = False):
        dbObjects = Config.getDBCursors(isBackTesting)
        DBConnector._selectedDBCursor = dbObjects[0]
        DBConnector._selectedDB = dbObjects[1]
        self.__initDB()
        
    def resetDB(self, skipConfirm = False):
        if not skipConfirm:
            confirm = input('Are you sure you want to reset DB? (Y): ')
            if confirm == 'Y':
                pass
            else:
                print('DB Reset aborted..')
                return
        cursor = self._selectedDBCursor
        cursor.execute('''DROP TABLE stocksTxn''')
        cursor.execute('''DROP TABLE strategy''')
        cursor.execute('''DROP TABLE stocks''')
        self._selectedDB.commit()
        self.__initDB()  
            
    def __initDB(self):
        cursor = self._selectedDBCursor
        cursor.execute('''CREATE TABLE IF NOT EXISTS stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name string,
        nseCode string UNIQUE
        );''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key string UNIQUE,
            value string
        );''')
        
        cursor.execute('''DROP TABLE IF EXISTS strategy;''')
        cursor.execute('''
        CREATE TABLE strategy (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name string UNIQUE,
        enable bool DEFAULT True
        );''')
        cursor.execute('''
        INSERT INTO strategy (name) VALUES 
        ('None'), ('SampleStrategy'), ('WeekHigh52');
        ''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS stocksTxn (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stockId INTEGER NOT NULL,
        txnDate DATETIME DEFAULT CURRENT_TIMESTAMP,
        txnTime string DEFAULT "",
        holdingStatus varchar(1),
        price float,
        quantity integer,
        strategy integer DEFAULT 1,
        stopLoss float,
        stopLossPercent float,
        targetPrice float,
        targetPercent float,
        status string,
        enable Boolean DEFAULT TRUE,
        syncStatus Boolean DEFAULT FALSE,
        FOREIGN KEY(stockId) REFERENCES stocks(id),
  		FOREIGN KEY(strategy) REFERENCES strategy(id),
  		UNIQUE(stockId, txnTime, holdingStatus, price, quantity, strategy, status)
        )''')
        
        self._selectedDB.commit()
        
    def addNewTxn(self, stockName, nseCode, holdingStatus:str, price:float, quantity:int, stopLossPercent:float, targetPercent:float, status:str, strategy=0, txnTime=None, stopLoss:float = None, targetPrice:float= None, syncStatus=0):
        stockId = self.addStocks(stockName, nseCode)
        if stopLoss is None:
            stopLoss = price - (stopLossPercent/100)*price
        if targetPrice is None:
            targetPrice = price + (targetPercent/100)*price
        self.addStocksTxn(stockId, holdingStatus, price, quantity, stopLoss, stopLossPercent, targetPrice, targetPercent, status, strategy, txnTime, syncStatus)
        
    
    def addStocks(self, name:str, nseCode:str):
        query = "INSERT OR IGNORE INTO stocks (name, nseCode) VALUES (?, ?)"
        response = self._selectedDBCursor.execute(query, (name, nseCode,))    
        self._selectedDB.commit() 
        stockID = self.selectDataFromTable('stocks', columnName='id', whereClause='nseCode="'+nseCode+'"')[0][0]
        return stockID
        
    def addStocksTxn(self, stockId:int, holdingStatus:str, price:float, quantity:int, stopLoss: float, stopLossPercent:float, targetPrice:float, targetPercent:float, status:str, strategy=0, txnTime=None, syncStatus=0):
        if txnTime is None:
            txnTime = int(time.time())        
        query = '''INSERT OR IGNORE INTO stocksTxn (stockId,holdingStatus,price,quantity,strategy,stopLoss,stopLossPercent,targetPrice,targetPercent,status,txnTime,syncStatus) 
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        '''
        self._selectedDBCursor.execute(query, (stockId,holdingStatus,price,quantity,strategy,stopLoss,stopLossPercent,targetPrice,targetPercent,status, txnTime, syncStatus))
        self._selectedDB.commit()
        
    def selectDataFromTable(self, table, whereClause=None, columnName='*'):
        query = '''SELECT {0} FROM {1} '''
        if whereClause is not None and whereClause!='':
            query += '''WHERE '''+whereClause
        query = query.format(columnName, table)
        self._selectedDBCursor.execute(query)
        resp = self._selectedDBCursor.fetchall()
        return resp
    
    def executeRawQuery(self, query, isSelectQuery=False):
        queryResponse = self._selectedDBCursor.execute(query)
        if isSelectQuery:
            queryResult = self._selectedDBCursor.fetchall()
            return (queryResponse, queryResult)
        else:
            self._selectedDB.commit()
        return (queryResponse)
    
    def getConfig(self, key):
        result = self.selectDataFromTable('config', 'key="'+key+'"', 'value')
        if len(result) > 0:
            return result[0][0]
        else:
            return None
    
    def setConfig(self, key, value):
        existingValue = self.getConfig(key)
        if existingValue is not None:
            self.executeRawQuery('UPDATE config SET value="'+str(value)+'" WHERE key="'+key+'"')
        else:
            self.executeRawQuery('INSERT INTO config (key, value) VALUES("'+key+'", "'+str(value)+'")')