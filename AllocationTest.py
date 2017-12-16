from IndexCalculations import *

XCRate0 = XChangeRate(100, Currency("XBT"),Currency("EUR"))
XCRate1 = XChangeRate(110, Currency("XBT"),Currency("EUR"))
XCRate2 = XChangeRate(150, Currency("XBT"),Currency("EUR"))


FXMarket0 = FXMarket([XCRate0])
FXMarket1 = FXMarket([XCRate1])
FXMarket2 = FXMarket([XCRate2])

#TODO: Implement a sorted Dictionary - in order to store Allocation and FXMarket
#TODO: Be able to create manually everything (FXMarket History, Allocation History)
#TODO: Separate with a Download Function the request from kraken and the init (FXMarketHistory)
#TODO: PDLs
