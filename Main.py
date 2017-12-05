
import matplotlib.pyplot as plt
from Requests import *
import krakenex

from Transaction import *
from IndexCalculations import *

p = Price(100.0, "EUR")


k = krakenex.API()

#ret = k.query_public("OHLC", req = {'pair': "XETHZUSD", 'since': str(1499000000)})

k.load_key("keys.txt")

#print(k.query_private('Balance'))
#print(k.query_private('TradesHistory'))
ledger = k.query_private('Ledgers')
Df = JsonToDataFrame(ledger,["time","amount","fee","balance"])

Df = Df.sort_values("time",0,True)

TL = TransactionList(Df)

print(TL.ToString)



FXEURMH = FXMarketHistory(["XBT","ETH","BCH"],240)
#FXBTCMH = FXMarketHistory(["ETH"], 240, ref = Currency("XBT"))

AH = AllocationHistory(TL,FXEURMH)

DF_BTC = FXEURMH.DataFrames[Currency("XBT")]
DF_ETH = FXEURMH.DataFrames[Currency("ETH")]


#DF_ETHBTC = FXBTCMH.DataFrames[Currency("ETH")]

FXEURMH.RefactorReturns(.25, Currency("BCH"))
DF_BCH = FXEURMH.DataFrames[Currency("BCH")]

print(AH.ToString)


I = Index(FXEURMH, AH.List[0].Date)
I.AddAllocationHistory(AH)
I.IndexCalculations()
print(I.DataFrame)

fig2 = plt.figure()
plt.plot(I.DataFrame["time"], I.DataFrame["Amount"])
plt.show()

fig1 = plt.figure()
plt.plot(I.DataFrame["time"], I.DataFrame["Index_XBT"],'-')
plt.plot(I.DataFrame["time"], I.DataFrame["Index_ETH"],'-')
plt.plot(I.DataFrame["time"], I.DataFrame["Index_BCH"],'-')
plt.plot(I.DataFrame["time"], I.DataFrame["Total"],'-')
plt.legend(["BTC", "ETH", "BCH", "Strat"])
plt.show()


fig = plt.figure()
plt.plot(DF_BTC["time"], DF_BTC["Index"],'-')
plt.plot(DF_ETH["time"], DF_ETH["Index"],'-')
#plt.plot(DF_ETH["time"], DF_BCH["Index"],'-')
plt.legend(["BTC", "ETH"])#, "BCH"])
plt.show()


def PrintExample():

    DF_BTC = OHLC(startDate = datetime(2017,1,1),freq = 240)
    DF_ETH = OHLC(X = "ETH", startDate = datetime(2017,1,1), freq = 240)

    DayPrices = ComputePricesPerDay(DF_BTC)

    print(len(DayPrices))

    plt.scatter(DayPrices["12"],DayPrices["-1"])
    plt.plot(DayPrices["12"],DayPrices["12"],'-')
    plt.show()

    start_BTC = DF_BTC["close"][0]
    start_ETH = DF_ETH["close"][0]


    fig = plt.figure()
    plt.plot(DF_BTC["time"], DF_BTC["close"] / start_BTC * 1000,'-')
    plt.plot(DF_ETH["time"], DF_ETH["close"] / start_ETH * 1000,'-')
    plt.legend(["BTC", "ETH"])
    plt.show()

    ComputeReturns(DF_BTC)
    ComputeReturns(DF_ETH)

    DF_BTC["mean_return"] = pd.rolling_mean(DF_BTC["return"], 10)
    DF_ETH["mean_return"] = pd.rolling_mean(DF_ETH["return"], 10)

    plt.plot(DF_BTC["time"], DF_BTC["mean_return"],'-')
    plt.plot(DF_ETH["time"], DF_ETH["mean_return"],'-')

    DF_BTC["std_return"] = pd.rolling_std(DF_BTC["return"], 10)
    DF_ETH["std_return"] = pd.rolling_std(DF_ETH["return"], 10)

    plt.plot(DF_BTC["time"], DF_BTC["std_return"],'-')
    plt.plot(DF_ETH["time"], DF_ETH["std_return"],'-')

    plt.legend(["BTC mean", "ETH mean", "BTC std", "ETH std"])
    plt.show()

