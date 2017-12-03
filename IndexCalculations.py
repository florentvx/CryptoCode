from AllocationHistory import *


def DateCut(date: datetime):
    print(date)
    return datetime(date.year, date.month, date.day, date.hour, date.minute)

def RenameColumn(x: str, cur: Currency):
    if x=="time":
        return x
    else:
        return x + "_" + cur.name

def RenameColumns(DF: pd.DataFrame, columns: list, cur: Currency):
    cols = list(DF.columns)
    for i in range(len(cols)):
        str = cols[i]
        if str in columns:
            cols[i] = RenameColumn(str, cur)
    DF.columns = cols



class Index:

    def __init__(self, FXMH: FXMarketHistory, startDate: datetime, ref: CurrencyPair = CurrencyPair("XBT", "EUR")):
        self.Ref = ref
        self.Currencies = []
        columns = ["open","close","return"]
        if FXMH.CurrencyRef != ref.Y:
            raise Exception("Wrong FXMarketHistory Reference Currency")
        self.DataFrame = FXMH.DataFrames[ref.X][["time"] + columns]
        self.DataFrame = self.DataFrame[self.DataFrame["time"] >= startDate]
        RenameColumns(self.DataFrame,columns,ref.X)
        self.DataFrame["time"] = self.DataFrame["time"].apply(lambda x:  DateCut(x))
        for curr in FXMH.DataFrames.keys():
            self.Currencies += [curr]
            if curr != ref.X:
                auxDF = FXMH.DataFrames[curr][["time"] + columns]
                self.DataFrame = pd.merge(self.DataFrame, auxDF,how = "left", right_on= "time", left_on = "time")
                RenameColumns(self.DataFrame,columns,curr)
        print(self.DataFrame)

    def AddAllocationHistory(self, AH: AllocationHistory):
        N = len(self.DataFrame)
        dict = {}
        last_n = 0
        for alloc in AH.List:
            n = len(self.DataFrame[self.DataFrame["time"] <= alloc.Date])
            if n > last_n:
                last_n = n
                for curr in alloc.Dictionary.keys():
                    L = []
                    try:
                        L = dict[curr]
                        if n - 1 - len(L) > 0:
                            L += [L[-1] for i in range(n - 1 - len(L))]
                        L += [alloc.Dictionary[curr].Percentage]
                    except:
                        L = [0 for i in range(n - 1)]
                        L += [alloc.Dictionary[curr].Percentage]
                    dict[curr] = L
            if n > 0 and n == last_n:
                for curr in alloc.Dictionary.keys():
                    try:
                        dict[curr][-1] = alloc.Dictionary[curr].Percentage
                    except:
                        dict[curr] = [0 for i in range(n-1)] + [alloc.Dictionary[curr].Percentage]
        for curr in dict.keys():
            L = dict[curr]
            dict[curr] = L + [L[-1] for i in range(N - len(L))]
            self.DataFrame["Alloc_" + curr.name] = dict[curr]

    def IndexCalculations(self):
        for curr in self.Currencies:
            Index = [1000]
            for (index,row) in self.DataFrame[1:].iterrows():
                Index += [Index[-1] * (1 + row["return_" + curr.name])]
            self.DataFrame["Index_" + curr.name] = Index

        Total = [1000]
        for (index, row) in self.DataFrame[1:].iterrows():
            ret = 0
            for curr in self.Currencies:
                if curr != self.Ref.Y:
                    print(row["Alloc_" + curr.name])
                    ret += (row["Alloc_" + curr.name] * row["return_" + curr.name])
            Total += [Total[-1] * (1 + ret)]
        self.DataFrame["Total"] = Total