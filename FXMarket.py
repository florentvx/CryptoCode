
from Requests import *
from Prices import *




class FXMarket:

    def __init__(self, XChangeRates: list):
        self.FX = []
        for xRate in XChangeRates:
            if type(xRate) == XChangeRate:
                self.FX += [xRate]
            else:
                raise Exception("Wrong Input")

    def GetFXRate(self, X: Currency, Y: Currency):
        if X == Y:
            return 1.0
        for xRate in self.FX:
            if xRate.CurPair.X == X:
                if xRate.CurPair.Y == Y:
                    return xRate.Rate
            if xRate.CurPair.Y == X:
                if xRate.CurPair.X == Y:
                    return 1 / xRate.Rate
        raise Exception("Undefined XChangeRate")

    def ConvertPrice(self, input: Price, output: Currency):
        rate = self.GetFXRate(input.Currency, output)
        return Price(input.Amount * rate, output)

    def Sum(self, price : Price, Delta : Price):
        return Price(price.Amount + self.ConvertPrice(Delta, price.Currency).Amount, price.Currency)

    @property
    def ToString(self):
        res = "FX Market" + '\n'
        for xRate in self.FX:
            res += xRate.ToString + '\n'
        return res


#1 (default), 5, 15, 30, 60, 240, 1440, 10080, 21600

class FXMarketHistory:

    def __init__(self, CurrencyList: list, freq: int, ref: Currency = Currency.EUR):
        self.CurrencyRef = ref
        self.DataFrames = {}
        for cur in CurrencyList:
            DF = OHLC(X = cur, Z = ref.name, startDate = datetime.datetime(2017,1,1), freq = freq)
            DF["return"] = DF["close"]/DF["close"].shift(1) - 1
            Index = [1000]
            for (index,row) in DF[1:].iterrows():
                Index += [Index[-1] * (1 + row["return"])]
            DF["Index"] = Index
            self.DataFrames[Currency(cur)] = DF

    def RefactorReturns(self, factor: float, X: Currency):
        DF = self.DataFrames[X]
        DF["return"] = (DF["close"]/DF["close"].shift(1) - 1) * factor
        Index = [1000]
        for (index,row) in DF[1:].iterrows():
            Index += [Index[-1] * (1 + row["return"])]
        DF["Index"] = Index
        self.DataFrames[Currency(X)] = DF

    def GetFXMarket(self, date: datetime):
        XChangeRates = []
        for cur in self.DataFrames.keys():
            DF = self.DataFrames[cur]
            lastRow = DF[DF["time"] <= date].tail(1)
            if len(lastRow) > 0:
                XChangeRates += [XChangeRate(float(lastRow["close"]), cur, "EUR")]
            else:
                return FXMarket([])

        return FXMarket(XChangeRates)
