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
            
    def __initDB(self):
        cursor = self._selectedDBCursor
        cursor.execute('''CREATE TABLE IF NOT EXISTS stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name string,
        nseCode string UNIQUE
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
        
    def addStocks(self, name:str, nseCode:str):
        query = "INSERT OR IGNORE INTO stocks (name, nseCode) VALUES (?, ?)"
        response = self._selectedDBCursor.execute(query, (name, nseCode,))    
        self._selectedDB.commit() 
        return response
        
    def addStocksTxn(self, stockId:int, holdingStatus:str, price:float, quantity:int, stopLoss: float, stopLossPercent:float, targetPrice:float, targetPercent:float, status:str, strategy=0, txnTime=None):
        if txnTime is None:
            txnTime = int(time.time())        
        query = '''INSERT OR IGNORE INTO stocksTxn (stockId,holdingStatus,price,quantity,strategy,stopLoss,stopLossPercent,targetPrice,targetPercent,status,txnTime) 
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        '''
        self._selectedDBCursor.execute(query, (stockId,holdingStatus,price,quantity,strategy,stopLoss,stopLossPercent,targetPrice,targetPercent,status, txnTime))
        self._selectedDB.commit()
        
    def selectDataFromTable(self, table, whereClause=None):
        query = '''SELECT * FROM {0} '''
        if whereClause is not None and whereClause!='':
            query += '''WHERE '''+whereClause
        query = query.format(table)
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