import requests, datetime, json
from Config import Config
from DBConnector import *
import tempfile, os, time, pickle

class StockData():
    __isBackTesting=False
    __config = list()
    __requestHeader = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
        'Cache-Control' : 'no-cache, must-revalidate'
    }
    _s = requests.session()    
    
    def __new__(cls, config=None, isBackTesting=False):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StockData, cls).__new__(cls)
        return cls.instance
    
    def __init__(self, config=None, isBackTesting=False):
        #Overwritting config values
        if config is not None:
            self.__config = config
        self.__isBackTesting = isBackTesting
            
    def __splitDateRange(self, startDate, endDate, intervalDays=70) -> list:
        '''
        Splitting date range in `intervalDays` days chunks.
        '''
        dateSplit = startDate.split('-')
        objStartDate = datetime.date(day=int(dateSplit[0]), month=int(dateSplit[1]), year=int(dateSplit[2]))
        dateSplit = endDate.split('-')
        objEndDate = datetime.date(day=int(dateSplit[0]), month=int(dateSplit[1]), year=int(dateSplit[2]))
        
        dateSplitList = []
        startingDate = objStartDate
        while(startingDate<=objEndDate):
            lst = [startingDate.strftime("%d-%m-%Y")]
            if (objEndDate - startingDate).days > intervalDays:
                newDate = startingDate + datetime.timedelta(days=intervalDays)
                lst.append(newDate.strftime("%d-%m-%Y"))
            else:
                newDate = objEndDate
                lst.append(objEndDate.strftime("%d-%m-%Y"))
            dateSplitList.append(lst)
            startingDate = newDate + datetime.timedelta(days=1)
        return dateSplitList      
            
    def getStockDataFromNSE(self, symbol, startDate, endDate) -> list:
        '''
        symbol : NSE symbol of the stock
        startDate : starting date range (inclusive), Format: DD-MM-YYYY
        endDate : ending date range (inclusive), Format: DD-MM-YYYY
        
        @Returns list<dict>
        '''
        
        if symbol is None or startDate is None or endDate is None:
            raise Exception("Symbol, StartDate and EndDate are required in getStockData")
        
        tempSession = requests.session()
        #Splitting into date range in 70 days chunks as API is giving 70 days data per request
        dateList = self.__splitDateRange(startDate, endDate, 70)
        stockData = []
        header = self.__requestHeader
        header['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        header['Host'] = 'www.nseindia.com'
        tempSession.get('https://www.nseindia.com', headers=header)
        for i in dateList:
            data = json.loads(tempSession.get('https://www.nseindia.com/api/historical/cm/equity?symbol='+symbol+'&from='+i[0]+'&to='+i[1], headers=header).content.decode())
            for j in data['data']:
                stockData.append(j)

        return stockData
    
    def __getStockDataFromApi_Live(self, *args):
        global s
        url = Config.getConfigValues('stockDataURL').format(*args)
        #convert to required format:
        data = json.loads(self._s.get(url, headers=self.__requestHeader).content.decode())
        stockTimeLine = []
        if data['s'] != 'ok':
            return stockTimeLine
        for i in range(0, len(data['t'])):
            lst = []
            lst.append(data['t'][i])
            lst.append(data['o'][i])
            lst.append(data['h'][i])
            lst.append(data['l'][i])
            lst.append(data['c'][i])
            lst.append(data['v'][i])
            stockTimeLine.append(lst)
        return stockTimeLine
    
    def __getNearestIndex(self, data, indexVal):
        for i in range(0, len(data)):
            if data[i] == indexVal:
                return i
            elif data[i] > indexVal:
                return i-1
        return len(data)-1
        
    def getStockDataFromApi(self, *args):
        '''
            Fetch Stock CSV data from internet, based on url format provided in config file
            :args arguments to pass in url
            :returns dictionary data {'s': 'ok', 't': [..], 'o': [..], 'h': [..], 'l': [..], 'c':[..], 'v':[..]} -> status, time, open, high, low, close, volume
        '''
        global s
        cacheEnabled = True
        if 'cacheEnabled' in args[-1]:
            cacheEnabled = args[-1]['cacheEnabled']
        
        cacheFound = False
        
        if cacheEnabled:
            symbol = args[0]
            dirPath = tempfile.gettempdir()+'/AlgoTradingBackTesting/'
            cacheFile = dirPath+symbol+'_'+args[2]+'.pk'
            if os.path.exists(cacheFile):
                cFile = open(cacheFile, 'rb')
                cacheFound = True
            else:
                if not os.path.exists(dirPath):
                    os.mkdir(dirPath)
                cFile = open(cacheFile, 'wb+')
            if cacheFound:
                result = pickle.load(cFile)
                timeInd = self.__getNearestIndex(result['index'], args[1])
                finalResult = result['data'][:timeInd+1]
                return finalResult
            else:
                result = self.__getStockDataFromApi_Live(args[0], int(time.time()), args[2])
                index = []
                for i in result:
                    index.append(i[0])
                dumpData = {
                    'data': result,
                    'index': index
                }
                timeInd = self.__getNearestIndex(index, args[1])
                finalResult = result[:timeInd+1]
                pickle.dump(dumpData, cFile)
                cFile.close()
                return finalResult
        else:
            return self.__getStockDataFromApi_Live(args)
                
    
    def getStocksFromChartInk(self, scan_clause):
        tmpSession = requests.session()
        res = tmpSession.get(Config.getConfigValues('scanner')).content.decode()
        csrf_str = 'csrf-token" content="'
        ind = res.find(csrf_str)+len(csrf_str)
        csrf_token = ''
        for i in range(ind, ind+100):
            if res[i] == '"':
                break
            csrf_token += res[i]
    
        screener_head = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Csrf-Token': csrf_token
        }
        urlString = 'process?scan_clause='+scan_clause
        res = json.loads(tmpSession.post(Config.getConfigValues('scanningURL').format(urlString,), headers=screener_head).content.decode())
        return res
