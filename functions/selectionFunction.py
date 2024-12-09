from functions.mainFunctions import *
from backtesting.backTestStrategy import *
from datetime import datetime


def getCandidates(scan_clause):
    # Removed global session and used temp session. Fix Issue #24
    tmpSession = requests.session()
    res = tmpSession.get(getConfig('scanner')).content.decode()
    
    # TODO: Implement Scanner Parser as per requirement
    
    # Implement scanner Parser as per requirement
    # Example for Chartink
    csrf_str = 'csrf-token" content="'
    ind = res.find(csrf_str)+len(csrf_str)
    csrf_token = ''
    for i in range(ind, ind+100):
        if res[i] == '"':
            break
        csrf_token += res[i]
    # print("csrf token: "+csrf_token) 
    
    #Change Screener Header value as per requirement
    screener_head = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Csrf-Token': csrf_token
    }
    urlString = 'process?'+scan_clause
    res = json.loads(tmpSession.post(getConfig('scanningURL').format(urlString,), headers=screener_head).content.decode())
    return res


def isW(close, p):
    # print("Running isW")
    if close[p[0]] > close[p[2]] and close[p[2]] < close[p[4]]:
        return True
    return False

def testisW(close, p):
    # print("Running testisW")
    wShape = 0.025
    if close[p[0]] > close[p[2]] and close[p[2]] < close[p[4]]:
        if abs(close[p[1]] - close[p[3]])/close[p[1]] <= wShape:
            return True
    return False


def getW(pricelist=None, log=True, test=False):
    dates = []
    close = []
    errorCount = -1
    if test:
        errorCount = 0
    diff = .01
    p = [0, 0, 0, 0]
    m = [-1, 1, -1, 1]
    ind = 0
    recentW = False
    for i in pricelist:
        dates.append(i[0])
        close.append(i[4])
    prevPt = len(close)-1
    for i in range(len(close)-1, 0, -1):
        sign = 1
        if prevPt - i > 4:
            p = [0, 0, 0, 0, 0]
            ind = 0
            prevPt = i-1
        if ind == 4:
            p.append(i)
            if test:
                if isW(close, p) != testisW(close, p):
                    print("isW Result: "+str(isW(close, p)))
                    print("testisW Result: "+str(testisW(close, p)))
                    print("for params:")
                    wdates = []
                    for i in p:
                        wdates.append(dates[i])
                    print(wdates)

                    errorCount += 1
                    print()

            if not ((not test and isW(close, p)) or (test and testisW(close, p))):
                p = [0, 0, 0, 0, 0]
                ind = 0
                prevPt = i-1
            else:
                w_cord = []
                if dates[p[0]] == dates[-1]:
                    if log:
                        print("W found at: ")
                    for i in range(0, len(p)):
                        if log:
                            print("p"+str(i+1)+": "+dates[p[i]])
                        w_cord.append(dates[p[i]])
                    recentW = True
                return (True, recentW, w_cord, errorCount)
        if close[i]-close[prevPt] < 0:
            sign = -1
        if abs(close[i]-close[prevPt])/100 < diff:
            prevPt += 1
            sign = 0
        if m[ind] == sign:
            p[ind] = prevPt
            prevPt = i+1
            ind += 1
        prevPt -= 1

    return (False, recentW, [], errorCount)

