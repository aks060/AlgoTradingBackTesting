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
