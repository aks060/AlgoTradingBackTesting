from BackTesting import *
from classes.Config import *
import time


def configEnvironment():
    Config.setupEnvironment()


def generateCsv(result, fileName = 'Report.csv'):
    finalTxn = {}
    totalProfit = 0
    totalTransactions = 0
    for i in result:
        txnId = i['txnId']
        if txnId not in finalTxn.keys():
            finalTxn[txnId]={}
        newDict = {
         'name': i['name'],
         'nseCode': i['nseCode'],
         'qnt': i['qnt'],   
        }
        if 'name' not in finalTxn[txnId]:
            finalTxn[txnId] = newDict
        if i['txnType'] == 'B':
            finalTxn[txnId]['buyingPrice'] = i['price']
            finalTxn[txnId]['totalBuyingPrice'] = i['total']
            finalTxn[txnId]['buyingDate'] = time.strftime('%d-%m-%Y', time.gmtime(i['date']))
        else:
            finalTxn[txnId]['sellingPrice'] = i['price']
            finalTxn[txnId]['totalSellingPrice'] = i['total']
            finalTxn[txnId]['sellingDate'] = time.strftime('%d-%m-%Y', time.gmtime(i['date']))
        if 'buyingDate' in finalTxn[txnId] and 'sellingDate' in finalTxn[txnId]:
            finalTxn[txnId]['profit'] = i['total'] - finalTxn[txnId]['totalBuyingPrice']
    
    file = open(fileName, 'w+')
    file.write('txnId, name, nseCode, quantity, buyingPrice, totalBuyingPrice, buyingDate, sellingPrice, totalSellingPrice, sellingDate, Profit\n')
    for i in finalTxn.items():
        data = i[1]
        buyingPrice = 0
        totalBuyingPrice = 0
        buyingDate = 'NA'
        sellingPrice = 0
        totalSellingPrice = 0
        sellingDate = 'NA'
        if 'buyingPrice' in data:
            buyingPrice = data['buyingPrice']
        if 'totalBuyingPrice' in data:
            totalBuyingPrice= data['totalBuyingPrice']
        if 'buyingDate' in data:
            buyingDate= data['buyingDate']
        if 'sellingPrice' in data:
            sellingPrice= data['sellingPrice']
        if 'totalSellingPrice' in data:
            totalSellingPrice= data['totalSellingPrice']
        if 'sellingDate' in data:
            sellingDate= data['sellingDate']
        profit = totalSellingPrice-totalBuyingPrice
        totalProfit+= profit
        totalTransactions+=1
        file.write(str(i[0])+','+data['name']+','+data['nseCode']+','+str(data['qnt'])+','+str(buyingPrice)+','+str(totalBuyingPrice)+','+buyingDate+','+str(sellingPrice)+','+str(totalSellingPrice)+','+sellingDate+','+str(profit)+'\n')
    file.write("\n\nTotalProfit,"+str(totalProfit)+"\nTotalTransactions,"+str(totalTransactions))
    file.close()
    return(totalProfit, totalTransactions)


configEnvironment()
config = {
    "initialBalance": [10000, 20000, 50000, 100000],
    'stopLossPercent':[40, 30, 20],
    'targetPercent':[80, 60, 40],
    'marketCap':10000,
    'isBackTesting': True,
    'maxBuyLimitPerStock': 3000,
    'useCache': True,
    'buyMaxLimit': True
}
# bk = BackTesting(strategyName="WeekHigh52", testConfigs=config)
reportSummary = {}
for i in config['initialBalance']:
    for jj in range(0, len(config['stopLossPercent'])):
        j = config['stopLossPercent'][jj]
        k = config['targetPercent'][jj]
        print("\n"*5)
        print("Running for initialBalance: "+str(i)+"  stopLossPercent: "+str(j)+"  targetPercent: "+str(k)+"\n")
        newConfig = {
            "initialBalance": i,
            'stopLossPercent':j,
            'targetPercent':k,
            'marketCap':10000,
            'isBackTesting': True,
            'maxBuyLimitPerStock': 3000,
            'useCache': True,
            'buyMaxLimit': True
        }
        bk = BackTesting(strategyName="WeekHigh52", testConfigs=newConfig)
        bk.run()
        profit, txnCount = generateCsv(bk.getResult(), "Report_Bal"+str(i)+"_SL"+str(j)+"_TP"+str(k)+".csv")
        reportSummary[str(i)+'_'+str(j)+'_'+str(k)] = {
            'profit': profit,
            'transactionCount': txnCount
        }
        
        print(reportSummary)
        