import requests, datetime, json
from classes.Config import Config

class StockData():
    isBackTesting=False
    __config = list()
    __requestHeader = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
        'Cache-Control' : 'no-cache, must-revalidate'
    }
    
    
    def __new__(cls, config=None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StockData, cls).__new__(cls)
        return cls.instance
    
    def __init__(self, config=None):
        #Overwritting config values
        if config is not None:
            self.__config = config
            
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
    
    def getStockDataFromApi(self, *args):
        '''
            Fetch Stock CSV data from internet, based on url format provided in config file
            :args arguments to pass in url
            :returns dictionary data {'s': 'ok', 't': [..], 'o': [..], 'h': [..], 'l': [..], 'c':[..], 'v':[..]} -> status, time, open, high, low, close, volume
        '''
        global s
        url = Config.getConfigValues('stockDataURL').format(*args)
        #convert to required format:
        data = json.loads(s.get(url, headers=self.__requestHeader).content.decode())
        stockTimeLine = []
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
            
        