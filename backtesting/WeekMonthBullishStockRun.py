import sys, time, csv, random
sys.path.append(".")
from functions.selectionFunction import *
from backTestStrategy import *
import pickle

total_time_start = time.time()
cpu_time_start = time.process_time()

loop_time=[]
readFile = False
fileInputs=[]
inputFilePath=''
cache = False
args = sys.argv
if '--file' in args:
    readFile = True
    file = args[args.index('--file')+1]
    inputFilePath = file
    with open(file, mode ='r') as file:    
       csvFile = csv.DictReader(file)
       for lines in csvFile:
            fileInputs.append(dict(lines))
            
if '--cache' in args:
    cache = True
            
            
def cacheData(fileName, data):
    f=open(fileName,'wb')
    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

def retrieveCache(fileName):
    try:
        f=open(fileName,'rb')
        return (True, pickle.load(f))
    except Exception as e:
        return (False,)
        

def generateReport(stockFile, passbook):
    if passbook['totalBuyTxn'] ==0:
        return
    # transactions : date, type:S/B, qnt, price
    f = open(stockFile, 'w')
    f.write("Date,Type,Quantity,Price\n")
    for i in passbook['transactions']:
        for j in i:
            f.write(str(j)+',')
        f.write("\n")
    f.write("\n")
    f.write("Total,"+str(passbook['total']))        
 

# Get Selection Pool of Stocks
chartInk_selection = '''scan_clause=(+{cash}+(+latest+close+*+latest+volume+>=+500000000+and+latest+close+<=+2500+)+)+'''
stockSet = set()
gpercentChange = {'daily': 1, 'weekly':4, 'monthly':9}
candidates = getCandidates(chartInk_selection)
for i in candidates['data']:
    stockSet.add(i['nsecode'])

stockList = list(stockSet)

strategy = WeekMonthBullishStock()
days5year = 6*365

# @jit(nopython=False)
def runWeekMonthBullishBackTest(stopLossPercent=7, budget=2300, percentChange = gpercentChange):
    stockScanCount=1
    for i in stockSet:
        timeline = None
        print("Running on stock: "+i+"("+str(stockScanCount)+"/"+str(len(stockSet))+")")
        if cache:
            cachedData = retrieveCache('./backtesting/cache/'+i+'.pkl')
            if cachedData[0]:
                # print("Picking from cache")
                timeline = cachedData[1]
        if timeline is None:
            if stockScanCount%5 ==0:
                time.sleep(random.random())
            timeline = getStockData(i, str(int(time.time())))
            print(timeline)
            if cache:
                cacheData('./backtesting/cache/'+i+'.pkl', timeline)
        if len(timeline) < 4:
            continue
        #['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        print("Got Timeline of "+str(len(timeline))+" days..  Date: "+str(timeline[0][0])+" - "+str(timeline[-1][0]))
        count=1
        priceList = []
        stockWisePassbook = {
            'stockName': i,
            'total': 0,
            'totalBuyTxn': 0,
            'totalSellTxn':0,
            'totalLossTxn':0,
            'totalProfitTxn':0,
            'totalLoss':0,
            'totalProfit':0,
            'transactions': []
        }
        # transactions : date, type:S/B, qnt, price
        for j in timeline:
            priceList.append(j)
            if j[4] < 20:
                continue
            stockData = {
                'date': j[0],
                'buyingPrice': j[4],
                'currentPrice': j[4],
                'stopLossPercent': stopLossPercent
            }
            strategy.feedData(stockData)
            stockData['budget'] = budget
            
            if len(priceList) < 100:
                continue
            stockData['holdings'] = stockHoldings
            stockData['priceList'] = priceList
            stockData['nseCode'] = i
            stockData['percentChange'] = percentChange
            
            retVal = strategy.shouldBuy(stockData)
            #retVal : (True, noOfStocksinBudget, stopLossValue)
            if len(retVal) > 1 and retVal[0]:
                print("Found Stock")
                stockHoldingInfo ={
                    'nseCode': i,
                    'buyingPrice': j[4],
                    'buyingDate': j[0],
                    'quantity': retVal[1],
                    'stopLossPercent': stopLossPercent,
                    'stopLossValue': retVal[2],
                    'strategy': strategy
                }
                stockHoldings.append(stockHoldingInfo)
                passBook['buyTransactions'] = passBook['buyTransactions']+1
                passBook['transactionCount'] = passBook['transactionCount']+1
                stockWisePassbook['transactions'].append([stockHoldingInfo['buyingDate'], 'B', stockHoldingInfo['quantity'], stockHoldingInfo['buyingPrice']])
                print("Buying on "+str(stockHoldingInfo['buyingDate'])+" at price: Rs"+str(stockHoldingInfo['buyingPrice']))
                
                stockWisePassbook['totalBuyTxn'] = stockWisePassbook['totalBuyTxn'] + 1     
            for stock in stockHoldings:
                if stock['nseCode'] != i or stock['buyingDate'] == j[0]:
                    continue
                stockDataSL = stock.copy()
                stockDataSL['currentPrice'] = j[4]
                stockDataSL['priceList'] = priceList
                stockDataSL['percentChange'] = percentChange
                (sl, oldSl) = stock['strategy'].getSL(stockDataSL)
                stockDataSL['stopLossValue'] = sl
                #['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
                if sl>=j[3]:
                    profit = (int(stock['quantity'])*(sl-float(stock['buyingPrice'])))
                    passBook['total'] = passBook['total']+profit
                    passBook['transactionCount'] = passBook['transactionCount']+1
                    passBook['sellTransactions'] = passBook['sellTransactions']+1
                    
                    stockWisePassbook['total'] = stockWisePassbook['total'] + profit
                    stockWisePassbook['totalSellTxn'] = stockWisePassbook['totalSellTxn'] + 1
                    if profit > 0:
                        stockWisePassbook['totalProfitTxn'] = stockWisePassbook['totalProfitTxn'] + 1
                        stockWisePassbook['totalProfit'] = stockWisePassbook['totalProfit'] + profit
                        passBook['totalProfit']+=profit
                    else:
                        stockWisePassbook['totalLossTxn'] = stockWisePassbook['totalLossTxn'] + 1
                        stockWisePassbook['totalLoss'] = stockWisePassbook['totalLoss'] + profit
                        passBook['totalLoss']+=profit
                    stockWisePassbook['transactions'].append([j[0], 'S', stock['quantity'], sl])
                    stockHoldings.remove(stock)
                    print("Selling "+stock['nseCode']+" on date: "+str(j[0])+" at price: Rs"+str(sl))
            count+=1
        
        print()
        print("Stock Wise Report: ")
        print(stockWisePassbook)
        print()
        print()
        stockScanCount+=1
        
        generateReport('backtesting/report/'+i+'.csv', stockWisePassbook)

    print(passBook)
    print()
    print("Stocks still in holding: "+str(len(stockHoldings)))
    return passBook
    
    
if readFile and len(fileInputs)>0:
    print("Found "+str(len(fileInputs))+" params in File")
    tempFile = 'backTest_Temp.csv'
    fields = dict(fileInputs[0]).keys()
    print(fields)
    with open(tempFile, mode ='w') as file:    
       csvFile = csv.DictWriter(file, fieldnames = fields)
       csvFile.writeheader()
       for line in fileInputs:
            loop_time_start = time.time()
            print("Running for: "+str(line))
            if line['Run'] == 'FALSE':
                continue
            stockHoldings = []
            passBook = {
                "total": 0,
                "transactionCount":0,
                "sellTransactions":0,
                "buyTransactions":0,
                'totalLoss':0,
                'totalProfit':0,
            }
            if line['dayChange'] is None:
                percentCh = gpercentChange
            else:
                percentCh = {'daily': float(line['dayChange']), 'weekly': float(line['weekChange']), 'monthly':float(line['monthChange'])}
            
            passBk = runWeekMonthBullishBackTest(float(line['Stop Loss Percent']), float(line['budget']), percentCh)

            writeField = [{
                'Stop Loss Percent': line['Stop Loss Percent'],
                'Strategy': 'dayWeekMonthBullish',
                'budget': line['budget'],
                'Total': passBk['total'],
                'Txn Count': passBk['transactionCount'],
                'Sell Txn': passBk['sellTransactions'],
                'buy Txn': passBk['buyTransactions'],
                'Total Profit': passBk['totalProfit'],
                'Total Loss': passBk['totalLoss'],
                'Run': True
            }]
            csvFile.writerows(writeField)
            print()
            print()
            loop_time.append(time.time() - loop_time_start)
        
else:
    stockHoldings = []
    passBook = {
        "total": 0,
        "transactionCount":0,
        "sellTransactions":0,
        "buyTransactions":0,
        'totalLoss':0,
        'totalProfit':0,
    }
    runWeekMonthBullishBackTest()

print()
print()
print()
print("total time end: "+str(time.time() - total_time_start))
print("Total CPU Time: "+str(time.process_time() - cpu_time_start))
print("Loop Time: "+str(loop_time))