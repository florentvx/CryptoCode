from enum import Enum, auto

class Currency(Enum):
    NONE = "NONE"
    EUR = "EUR"
    USD = "USD"
    XBT = "XBT"
    ETH = "ETH"
    BCH = "BCH"

    @property
    def ToID(self):
        return str(self._name_)

    @property
    def ToString(self):
        if self == Currency.NONE:
            return "None"
        elif self == Currency.EUR:
            return "Euro"
        elif self == Currency.XBT:
            return "BitCoin"
        elif self == Currency.ETH:
            return "Ether"
        elif self == Currency.BCH:
            return "BitCoinCash"
        else:
            Exception("Currency Error")

    @property
    def Prefix(self):
        if self == Currency.EUR or self == Currency.USD:
            return "Z"
        else:
            return "X"

class Price:

    def __init__(self, amount: float, currency):

        self.Amount = amount

        if(type(currency) == Currency):
            self.Currency = currency
        elif(type(currency) == str):
            try:
                self.Currency = Currency[currency]
            except:
                self.Currency = Currency.NONE
        else:
            self.Currency = Currency.NONE

    @property
    def ToString(self):
        return str(self.Amount) + " " + self.Currency.ToString

class CurrencyPair:

    def __init__(self, X, Y):
        self.X = Price(0,X).Currency
        self.Y = Price(0,Y).Currency

    @property
    def ToString(self):
        return self.X.ToString + " / " + self.Y.ToString

    @property
    def RequestID(self):
        if self.X != Currency.BCH:
            return self.X.Prefix + self.X.ToID + self.Y.Prefix + self.Y.ToID
        else:
            return self.X.ToID + self.Y.ToID


class XChangeRate:

    def __init__(self, rate: float, X, Y):

        self.Rate = rate
        if rate > 1.0:
            self.CurPair = CurrencyPair(X,Y)
        else:
            self.CurPair = CurrencyPair(Y,X)

    @property
    def ToString(self):
        return str(self.Rate) + " " + self.CurPair.ToString