#!/usr/bin/python
import time
import Cryptsy
import operator
import sys
import gc
import logging

#Your current Cryptsy fee rate
fee_ratio = 0.005
cryptsy_pubkey = 'Public Key' #Enter your Cryptsy Public Key between the apostrophes
cryptsy_privkey = 'Private Key' #Enter your Cryptsy Private Key between the apostrophes

#Logging information
logger = logging.getLogger('trader')
hdlr = logging.FileHandler('/var/tmp/trader.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)
ttc = 5
lastFetchTime = 0

#What percentage of total account balance to trade at one time
if len(sys.argv) == 2:
    ratio = float(sys.argv[1])
else:
    ratio = 0.99
	
logger.info("Starting to trade")

#From Cryptsy.py, import current market data into an array
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
        
#Returns the current price of LTC in BTC		
def getLTCPrice():
    global cryptsyHandle
    cryptsyHandle = Cryptsy.Cryptsy(cryptsy_pubkey, cryptsy_privkey)
    r = cryptsyHandle.getSingleMarketData(3)
    try:
        return r['return']['markets']['LTC']['sellorders'][0]['price']
    except:
        getLTCPrice()

#Returns the current price of BTC in USD
def getBTCUSD():
    global cryptsyHandle
    cryptsyHandle = Cryptsy.Cryptsy(cryptsy_pubkey, cryptsy_privkey)
    r = cryptsyHandle.getSingleMarketData(2)
    try:
        return r['price']
    except:
        getBTCUSD()

#Returns all account balances for each cryptocurrency
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

def ff(f):
    return format(f, '.8f')

#Main program functions, finding arbitrage opportunities between each cryptocurrency's LTC and BTC spread
def main():
    ltcMarkets = []
    btcMarkets = []

    Fetching = True
    tries = 0
    while Fetching:
        try:
            logger.info("Fetching market data.")
            fetchMarketData()
            logger.info("Got market data!")
            Fetching = False
        except:
            tries += 1
            logger.info("ERROR: Could not fetch market data. Number of tries: " + ff(tries))
            if tries > 5:
                sys.exit("ERROR: Could not fetch market data after five tries.")

    logger.info("Processing market data.")
    for marketName in marketData['return']['markets']:
        try:
            lo_sell = marketData['return']['markets'][marketName]['sellorders'][0]['price']
            hi_buy  = marketData['return']['markets'][marketName]['buyorders'][0]['price']
            sell_quantity = marketData['return']['markets'][marketName]['sellorders'][0]['quantity']
            buy_quantity = marketData['return']['markets'][marketName]['buyorders'][0]['quantity']
            sn = marketData['return']['markets'][marketName]['primarycode']
            marketid = marketData['return']['markets'][marketName]['marketid']
            if marketData['return']['markets'][marketName]['secondarycode'] == 'LTC':
                ltcMarkets.append({'market': marketName, 'hi_buy': hi_buy, 'lo_sell': lo_sell, 'sellquant': sell_quantity, 'buyquant': buy_quantity, 'sn': sn, 'marketid': marketid})
            if marketData['return']['markets'][marketName]['secondarycode'] == 'BTC':
                btcMarkets.append({'market': marketName, 'hi_buy': hi_buy, 'lo_sell': lo_sell, 'sellquant': sell_quantity, 'buyquant': buy_quantity, 'sn': sn, 'marketid': marketid})
        except:
            logger.info("Could not process market data.")
            pass

    tries = 0
    Fetching = True
    while Fetching:
        try:
            logger.info("Fetching LTC price.")
            ltc_price = float(getLTCPrice())
            logger.info("LTC Price: " + format(ltc_price, '.8f'))
            Fetching = False
        except:
            tries += 1
            logger.info("ERROR: Could not fetch LTC price. Number of tries: " + ff(tries))
            if tries > 5:
                sys.exit("ERROR: Could not fetch LTC price after five tries.")

    tries = 0
    Fetching = True
    while Fetching:
        try:
            logger.info("Fetching balances.")
            balances = getBalances()
            btc_balance = float(balances['BTC'])
            ltc_balance = float(balances['LTC'])
            Fetching = False
        except:
            tries += 1
            logger.info("ERROR: Could not fetch balances. Number of tries: " + ff(tries))
            if tries > 5:
                sys.exit("ERROR: Could not fetch balances after five tries.")
    #Core
    logger.info("Processing arbitrage opportunities!")
    for lmkt in ltcMarkets:
        for bmkt in btcMarkets:
            if lmkt['sn'] == bmkt['sn']:
                logger.info("Processing " + lmkt['sn'])
                try:
                    sn              = lmkt['sn']
                    ltc_marketid    = lmkt['marketid']
                    btc_marketid    = bmkt['marketid']
                    ltc_hi_buy      = float(lmkt['hi_buy'])
                    btc_hi_buy      = float(bmkt['hi_buy'])
                    ltc_buy_quant    = float(lmkt['buyquant'])
                    btc_buy_quant    = float(bmkt['buyquant'])
                    ltc_sell_quant    = float(lmkt['sellquant'])
                    btc_sell_quant    = float(bmkt['sellquant'])
                    ltc_lo_sell     = float(lmkt['lo_sell'])
                    btc_lo_sell     = float(bmkt['lo_sell'])
                    ltc_hi_buy_btc  = ltc_hi_buy * ltc_price
                    ltc_lo_sell_btc = ltc_lo_sell * ltc_price
                    if btc_hi_buy > ltc_lo_sell_btc: #Can be bought for LTC and sold for BTC with an exchange rate to LTC greater than original LTC cost
                        logger.info("**********")
                        logger.info("Profit to be made buying " + sn + " for " + ff(ltc_lo_sell) + " LTC (" + ff(ltc_lo_sell_btc) + " BTC) and selling for " + ff(btc_hi_buy) + " BTC.")
                        num_purchasable = (ltc_balance / ltc_lo_sell) * ratio
                        logger.info("Able to purchase: " + ff(num_purchasable) + " shares")
                        logger.info("LTC Sell Quantity: " + ff(ltc_sell_quant))
                        logger.info("BTC Buy Quantity: " + ff(btc_buy_quant))
                        if num_purchasable > ltc_sell_quant:
                            logger.info("Quantity purchasable greater than quantity available to buy")
                            if ltc_sell_quant > btc_buy_quant:
                                num_purchasable = btc_buy_quant
                                logger.info("Available to buy greater than available to sell. Revising...")
                            else:
                                num_purchasable = ltc_sell_quant
                        if num_purchasable > btc_buy_quant:
                            logger.info("Quantity purchasable greater than quantity available to sell")
                            num_purchasable = btc_buy_quant
                        logger.info("Quantity: " + ff(num_purchasable) + " shares")
                        total_fees      = (num_purchasable * ltc_lo_sell_btc) * fee_ratio
                        total_profit    = ((btc_hi_buy - ltc_lo_sell_btc) * num_purchasable) - total_fees
                        profit_per      = btc_hi_buy - ltc_lo_sell_btc
                        total_value     = ltc_lo_sell_btc * num_purchasable
                        logger.info("Calculated total profit: " + ff(total_profit))
                        logger.info("Profit per share: " + ff(profit_per))
                        logger.info("Total value: " + ff(total_value))
                        logger.info("**********")
                        if total_value > 0.00000010 and total_profit > 0.00000001:
                            logger.info("Buying " + ff(num_purchasable) + " " + sn + " @ " + ff(ltc_lo_sell) + " LTC (" + ff(ltc_lo_sell_btc) + "), selling @ " + ff(btc_hi_buy) + " BTC (Fees: " + ff(total_fees) + ", " + ff(total_profit) + " BTC profit)")
                            r = placeOrder(ltc_marketid, 'Buy', num_purchasable, ltc_lo_sell)
                            logger.info(str(r))
                            onHand = 0
                            tries = 0
                            Buying = True
                            while Buying:
                                try:
                                    balances = getBalances()
                                    onHand = balances[sn]
                                    logger.info("Have: " + onHand + " " + sn)
                                    logger.info("Buying: " + ff(num_purchasable) + " " + sn)
                                    if float(onHand) >= float(num_purchasable):
                                        Buying = False
                                        cancelOrder(ltc_marketid)
                                        logger.info("Buying successful.")
                                    else:
                                        logger.info("Order not fulfilled yet.")
                                        tries += 1
                                        time.sleep(.5)
                                    if tries > 4:
                                        cancelOrder(ltc_marketid)
                                        logger.info("Order cancelled")
                                        Buying = False
                                        logger.info("Have " + onHand + " " + sn)
                                except:
                                    break
                            time.sleep(.5)
                            balances = getBalances()
                            onHand = balances[sn]
                            if float(onHand) > 0.00000000:
                                logger.info("Attempting to sell coin.")
                                r = placeOrder(btc_marketid, 'Sell', onHand, btc_hi_buy)
                                logger.info(str(r))

                    if ltc_hi_buy_btc > btc_lo_sell: #Can be bought for BTC and sold for LTC with an exchange rate to BTC greater than original BTC cost
                        logger.info("**********")
                        logger.info("Profit to be made buying " + sn + " for " + ff(btc_lo_sell) + " BTC and selling for " + ff(ltc_hi_buy) + " LTC (" + ff(ltc_hi_buy_btc) + " BTC)")
                        num_purchasable = (btc_balance / btc_lo_sell) * ratio
                        logger.info("Able to purchase: " + ff(num_purchasable) + " shares")
                        logger.info("BTC Sell Quantity: " + ff(btc_sell_quant))
                        logger.info("LTC Buy Quantity: " + ff(ltc_buy_quant))
                        if num_purchasable > btc_sell_quant:
                            logger.info("Quantity purchasable greater than quantity available to buy")
                            if btc_sell_quant > ltc_buy_quant:
                                num_purchasable = ltc_buy_quant
                                logger.info("Available to buy greater than available to sell. Revising...")
                            else:
                                num_purchasable = btc_sell_quant
                        if num_purchasable > ltc_buy_quant:
                            logger.info("Quantity purchasable greater than quantity available to sell")
                            num_purchasable = ltc_buy_quant
                        logger.info("Quantity: " + ff(num_purchasable) + " shares")
                        total_fees      = (num_purchasable * btc_lo_sell) * fee_ratio
                        total_profit    = ((ltc_hi_buy_btc - btc_lo_sell) * num_purchasable) - total_fees
                        profit_per      = ltc_hi_buy_btc - btc_lo_sell
                        total_value     = btc_lo_sell * num_purchasable
                        logger.info("Calculated total profit: " + ff(total_profit))
                        logger.info("Profit per share: " + ff(profit_per))
                        logger.info("Total value: " + ff(total_value))
                        logger.info("**********")
                        if total_value > 0.00000010 and total_profit > 0.0000001:
                            logger.info("Buying " + ff(num_purchasable) + " " + sn + " @ " + ff(btc_lo_sell) + " BTC, selling @ " + ff(ltc_hi_buy) + " LTC (" + ff(ltc_hi_buy_btc) + " BTC (Fees: " + ff(total_fees) + ", " + ff(total_profit) + " BTC profit)")
                            r = placeOrder(btc_marketid, 'Buy', num_purchasable, btc_lo_sell)
                            logger.info(str(r))
                            onHand = 0
                            tries = 0
                            Buying = True
                            while Buying:
                                try:
                                    balances = getBalances()
                                    onHand = balances[sn]
                                    logger.info("Have: " + onHand + " " + sn)
                                    logger.info("Buying: " + ff(num_purchasable) + " " + sn)
                                    if float(onHand) >= float(num_purchasable):
                                        Buying = False
                                        logger.info("Buying successful")
                                        cancelOrder(btc_marketid)
                                    else:
                                        logger.info("Order not fulfilled yet.")
                                        tries += 1
                                        time.sleep(.5)
                                    if tries > 4:
                                        cancelOrder(btc_marketid)
                                        logger.info("Order cancelled") 
                                        Buying = False
                                        logger.info("Have " + onHand + " " + sn)
                                except:
                                    break
                            time.sleep(.5)
                            balances = getBalances()
                            onHand = balances[sn]
                            if float(onHand) > 0.00000000:
                                logger.info("Attempting to sell coin")
                                r = placeOrder(ltc_marketid, 'Sell', onHand, ltc_hi_buy)
                                logger.info(str(r))

                except:
                    pass

def wait():
    logger.info("Waiting 5 seconds.....")
    time.sleep(1)
    logger.info("Waiting 4 seconds....")
    time.sleep(1)
    logger.info("Waiting 3 seconds...")
    time.sleep(1)
    logger.info("Waiting 2 seconds..")
    time.sleep(1)
    logger.info("Waiting 1 second.")
    time.sleep(1)

while True:
    main()
    wait()
    gc.collect()
