import json, requests, time

# Functions

def calculateMAMain(pricelist, days=50):
    sum = 0
    count = 0
    for i in pricelist[::-1]:
        if count >= days:
            break
        sum += i[4]
        count += 1
    return round(sum / days, 2)

s = requests.session()

def getConfig(key=None)-> json:
    """
    @returns config.json file data
    """
    try:
        configFile = open('config.json', 'r')
        configData = json.loads(configFile.read())
        configFile.close()
        if key is not None:
            if key in configData:
                return configData[key]
            else:
                print("Key not found in config file")
                return None
        return configData
    except FileNotFoundError as e:
        print("File config.json not found. More details::")
        print(e)
    except Exception as e:
        print("Error while reading data. More info::")
        print(e)


def getStockData(*args):
    """
        Fetch Stock CSV data from internet, based on url format provided in config file
        :args arguments to pass in url
        :returns dictionary data {'s': 'ok', 't': [..], 'o': [..], 'h': [..], 'l': [..], 'c':[..], 'v':[..]} -> status, time, open, high, low, close, volume
    """
    global s
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
    }
    url = getConfig('stockDataURL').format(*args)
    #convert to required format:
    data = json.loads(s.get(url, headers=header).content.decode())
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
        

# print(getStockData('BSE', str(int(time.time()))))