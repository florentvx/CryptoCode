from IndexCalculations import *

XCRate0 = XChangeRate(100, Currency("XBT"),Currency("EUR"))
XCRate1 = XChangeRate(110, Currency("XBT"),Currency("EUR"))
XCRate2 = XChangeRate(150, Currency("XBT"),Currency("EUR"))


FXMH = FXMarketHistory()
FXMH.AddXChangeRate(datetime(2017,1,1), XCRate0)

print(FXMH.ToString)


FXMH.AddXChangeRate(datetime(2017,2,1), XCRate1)
FXMH.AddXChangeRate(datetime(2017,3,1), XCRate2)

print(FXMH.ToString)


#TODO: Implement a sorted Dictionary - in order to store Allocation and FXMarket
#TODO: Be able to create manually everything (FXMarket History, Allocation History)
#TODO: Separate with a Download Function the request from kraken and the init (FXMarketHistory)
#TODO: PDLs
