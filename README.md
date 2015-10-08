superCryptsy
===========

superCryptsy is a Python script for simple Cryptsy arbitrage, based off of <a href="https://github.com/dnase/cryptsy-arb">cryptsy-arb</a> by <a href="https://github.com/dnase/">dnase</a>.

This script will find cryptocurrencies where the coin can be bought in the BTC or LTC market and sold for a profit in the opposite market based on converstion rates between BTC and LTC.

Improvements over dnase's script include:
  - Automatic selling of the coin in the opposite market
  - Check to see if what is bought in one market can actually be sold in the other market
  - Better reporting of trade details (Currently is logged, but can easily be converted to print)

Make sure to edit superCryptsy.py and put in your Cryptsy public and private API keys.

>No special libraries or dependencies. Works best on Python 2.7, I haven't tested on 3.3+

>Credit to https://github.com/ScriptProdigy/CryptsyPythonAPI for the Cryptsy API interface. I hacked it up a bit for my purposes.

>Run with "python superCryptsy.py [max % to spend in BTC/LTC as float]"

>i.e.

>python superCryptsy.py 0.25

>or

>chmod +x superCryptsy.py
>./superCryptsy.py 0.33

>Default max percentage to spend on a buy order is 99%.

USE AT YOUR OWN RISK. SEE GPL.txt FOR LICENSE TERMS.

Please make donations to dnase, 

DOGE:
DT9U2LmozyHMT3XCNxj85jQqxWSf6CSKur

BTC:
1PJTKx1N7yssPNo1URsQt9AsL3KPcTSnN7
