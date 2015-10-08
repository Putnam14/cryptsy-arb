import time
import Cryptsy

#time to hold in cache, in seconds - this only applies for google AppEngine
ttc = 5

lastFetchTime = 0

cryptsy_pubkey = 'Public Key' #Enter your Cryptsy Public Key between the apostrophes
cryptsy_privkey = 'Private Key' #Enter your Cryptsy Private Key between the apostrophes

def fetchMarketData():
    global lastFetchTime
    global cryptsy_pubkey
    global cryptsy_privkey
    global cryptsyHandle
    global marketData

    if getCachedTime():
        cryptsyHandle = Cryptsy.Cryptsy(cryptsy_pubkey, cryptsy_privkey)
        marketData = cryptsyHandle.getMarketDataV2()
        try:
            if marketData['success'] == 1:
                lastFetchTime = time.time()
        except:
            fetchMarketData()
        
def getLTCPrice():
    global cryptsyHandle
    cryptsyHandle = Cryptsy.Cryptsy(cryptsy_pubkey, cryptsy_privkey)
    r = cryptsyHandle.getSingleMarketData(3)
    try:
        return r['return']['markets']['LTC']['sellorders'][0]['price']
    except:
        getLTCPrice()

def getBTCUSD():
    global cryptsyHandle
    cryptsyHandle = Cryptsy.Cryptsy(cryptsy_pubkey, cryptsy_privkey)
    r = cryptsyHandle.getSingleMarketData(2)
    try:
        return r['price']
    except:
        getBTCUSD()


def getBalances():
    global cryptsyHandle
    cryptsyHandle = Cryptsy.Cryptsy(cryptsy_pubkey, cryptsy_privkey)
    r = cryptsyHandle.getInfo()
    return r['return']['balances_available']

def placeOrder(marketid, ordertype, quantity, price):
    global cryptsyHandle
    cryptsyHandle = Cryptsy.Cryptsy(cryptsy_pubkey, cryptsy_privkey)
    return cryptsyHandle.createOrder(marketid, ordertype, quantity, price)

def cancelOrder(marketid):
    global cryptsyHandle
    cryptsyHandle = Cryptsy.Cryptsy(cryptsy_pubkey, cryptsy_privkey)
    return cryptsyHandle.cancelMarketOrders(marketid)

def getCachedTime():
    return (time.time() - lastFetchTime) > ttc
