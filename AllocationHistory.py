from FXMarket import *
from Transaction import *
from copy import deepcopy
from datetime import datetime

class AllocationElement:

    def __init__(self, percentage: float, amount: float, currency: Currency):
        if percentage <= 1.0:
            self.Percentage = percentage
        else:
            Exception("Allocation Element > 100%")
        self.Amount = amount
        self.Currency = currency

    @property
    def ToString(self):
        return "( " + str(int(self.Percentage * 10000.0) / 100.0) + \
               " %, " + str(self.Amount) + " " + self.Currency.ToString + " )"


class Allocation:

    def __init__(self, dictionary: dict, date: datetime = datetime(2000,1,1), fees = AllocationElement(0., 0., Currency.NONE)):
        self.Date = date
        self.Dictionary = dictionary
        self.Fees = fees

    def FirstDeposit(self, date: datetime, firstDeposit: Price):
        self.Date = date
        if self.Dictionary == {}:
            if firstDeposit.Amount >= 0:
                firstAlloc = AllocationElement(1., firstDeposit.Amount, firstDeposit.Currency)
                self.Dictionary[firstDeposit.Currency] = firstAlloc
            else:
                Exception("First Deposit Strictly Positive")
        else:
            Exception("Wrong Use of First Deposit")

    def AddTransaction(self, transaction: Transaction, FXMarket: FXMarket):

        res = deepcopy(self.Dictionary)
        fees = AllocationElement(0.,0,Currency.NONE)

        try:
            res[transaction.Received.Currency].Amount += transaction.Received.Amount
        except:
            res[transaction.Received.Currency] = \
                AllocationElement(0.,transaction.Received.Amount, transaction.Received.Currency)

        if transaction.Type == TransactionType.Trade:

            # Changing the Amounts

                # Paid

            try:
                alloc = res[transaction.Paid.Currency]
                alloc.Amount -= transaction.Paid.Amount
                if alloc.Amount < 0:
                    raise Exception("Paid more than available")
            except:
                raise Exception("Paid in unavailable currency")

                # Fees

            try:
                fAlloc = res[transaction.Fees.Currency]
                fAlloc.Amount -= transaction.Fees.Amount
                if fAlloc.Amount < 0:
                    raise Exception("Paid more than available (fees)")
                fees = AllocationElement(0., transaction.Fees.Amount, transaction.Fees.Currency)
            except:
                raise Exception("Paid in unavailable currency (fees)")


        # Changing the Percentages

        total = Price(0,Currency.NONE)
        for cur in res.keys():
            if total.Currency == Currency.NONE:
                total = Price(res[cur].Amount, res[cur].Currency)
            else:
                total = FXMarket.Sum(total, res[cur])
        if fees.Currency != Currency.NONE:
            total = FXMarket.Sum(total, Price(fees.Amount, fees.Currency))
        for cur in res.keys():
            res[cur].Percentage = res[cur].Amount / FXMarket.ConvertPrice(total, cur).Amount
        if fees.Currency != Currency.NONE:
            fees.Percentage = fees.Amount / FXMarket.ConvertPrice(total, fees.Currency).Amount
        return Allocation(res, transaction.Date, fees)

    @property
    def ToString(self):
        res =  "Allocation: " + " " + str(self.Date) + '\n'
        for cur in self.Dictionary.keys():
            res += cur.ToString + ": " + self.Dictionary[cur].ToString + '\n'
        res += '\n'
        res += "Fees: " + self.Fees.ToString
        res += '\n'
        return res


class AllocationHistory:

    def __init__(self, TL: TransactionList, FXH: FXMarketHistory, Currency: Currency = Currency.EUR):
        alloc = Allocation({})
        alloc.FirstDeposit(datetime(2000,1,1), Price(0, Currency))
        self.List = []
        for transaction in TL.List:
            FXMarket = FXH.GetFXMarket(transaction.Date)
            if len(FXMarket.FX) > 0:
                try:
                    self.List += [self.List[-1].AddTransaction(transaction,FXMarket)]
                except:
                    self.List += [alloc.AddTransaction(transaction,FXMarket)]


    @property
    def ToString(self):
        res = "Allocation History" + '\n'
        for alloc in self.List:
            res += alloc.ToString + '\n'
        return res