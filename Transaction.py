from enum import Enum, auto
import pandas as pd
import datetime

from Prices import *


class TransactionType(Enum):
    NONE = auto()
    Deposit = auto()
    Trade = auto()

    @property
    def ToString(self):
        if self == TransactionType.NONE:
            return "None"
        elif self == TransactionType.Deposit:
            return "Deposit"
        elif self == TransactionType.Trade:
            return "Trade"
        else:
            raise Exception("Transaction Type Error")

class Transaction:

    def __init__(self, type: TransactionType, date: datetime, paid: Price, received: Price, fees: Price):
        self.Type = type
        self.Date = date
        self.Paid = paid
        self.Received = received
        self.Fees = fees
        self.XRate = XChangeRate(paid.Amount / received.Amount, paid.Currency,received.Currency)


    @property
    def ToString(self):
        return str(self.Date) + " " + self.Type.ToString + '\n' + \
               "Paid: " + self.Paid.ToString + '\n' + \
               "Received: " + self.Received.ToString + '\n' + \
               "Fees: " + self.Fees.ToString + '\n' + \
               "XChange Rate: " + self.XRate.ToString

class TransactionList:

    def __init__(self, data : pd.DataFrame):
        paidPrice = Price(0,Currency.NONE)
        receivedPrice = Price(0,Currency.NONE)
        fees = Price(0,Currency.NONE)
        self.List = []
        for (index, row) in data.iterrows():
            if row["type"] == "deposit":
                self.List += [Transaction(
                    TransactionType.Deposit,
                    row["time"],
                    Price(0,Currency.NONE),
                    Price(row["amount"],row["asset"][1:]),
                    Price(row["fee"],Currency.NONE))]
            elif row["type"] == "trade":
                print(row["asset"])
                asset = row["asset"]
                asset = asset[(len(asset) - 3):]
                if row["amount"] > 0:
                    receivedPrice = Price(row["amount"],asset)
                elif row["amount"] < 0:
                    paidPrice = Price(-row["amount"],asset)
                else:
                    raise Exception("Amount free Price")
                if row["fee"] > 0:
                    if fees.Amount == 0:
                        fees = Price(row["fee"],row["asset"][1:])
                    else:
                        raise Exception("Double fees Problem")
                if paidPrice.Amount > 0 and receivedPrice.Amount > 0:
                    if fees.Amount > 0:
                        self.List += [Transaction(
                            TransactionType.Trade,
                            row["time"],
                            paidPrice,
                            receivedPrice,
                            fees)]
                        paidPrice = Price(0,Currency.NONE)
                        receivedPrice = Price(0,Currency.NONE)
                        fees = Price(0,Currency.NONE)
                    else:
                        raise Exception("No fee trade")
            else:
                raise Exception("Trade type Unknown")

    def ToString(self):
        res = '\n' + "Transactions List: " + '\n'
        i = 0
        for tr in self.List:
            res += str(i) + ":" + '\n' + tr.ToString + '\n' + '\n'
            i += 1
        return res