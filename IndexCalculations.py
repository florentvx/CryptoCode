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
        self.FXMH = FXMH
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

    def AddAllocationHistory(self, AH: AllocationHistory):
        N = len(self.DataFrame)
        # p: percentage
        # v: value
        dict_p = {}
        dict_v = {}
        last_n = 0
        for alloc in AH.List:
            n = len(self.DataFrame[self.DataFrame["time"] <= alloc.Date])
            if n > last_n:
                last_n = n
                for curr in alloc.Dictionary.keys():
                    try:
                        L_p = dict_p[curr]
                        L_v = dict_v[curr]
                        if n - 1 - len(L_p) > 0:
                            L_p += [L_p[-1] for i in range(n - 1 - len(L_p))]
                            L_v += [L_v[-1] for i in range(n - 1 - len(L_v))]
                        L_p += [alloc.Dictionary[curr].Percentage]
                        L_v += [alloc.Dictionary[curr].Amount]
                    except:
                        L_p = [0 for i in range(n - 1)]
                        L_v = [0 for i in range(n - 1)]
                        L_p += [alloc.Dictionary[curr].Percentage]
                        L_v += [alloc.Dictionary[curr].Amount]
                    dict_p[curr] = L_p
                    dict_v[curr] = L_v
            if n > 0 and n == last_n:
                for curr in alloc.Dictionary.keys():
                    try:
                        dict_p[curr][-1] = alloc.Dictionary[curr].Percentage
                        dict_v[curr][-1] = alloc.Dictionary[curr].Amount
                    except:
                        dict_p[curr] = [0 for i in range(n-1)] + [alloc.Dictionary[curr].Percentage]
                        dict_v[curr] = [0 for i in range(n-1)] + [alloc.Dictionary[curr].Amount]

        for curr in dict_p.keys():
            L_p = dict_p[curr]
            L_v = dict_v[curr]
            dict_p[curr] = L_p + [L_p[-1] for i in range(N - len(L_p))]
            dict_v[curr] = L_v + [L_v[-1] for i in range(N - len(L_v))]
            self.DataFrame["Alloc_" + curr.name] = dict_p[curr]
            self.DataFrame["Amount_" + curr.name] = dict_v[curr]


    def IndexCalculations(self):
        for curr in self.Currencies:
            Index = [1000]
            for (index,row) in self.DataFrame[1:].iterrows():
                Index += [Index[-1] * (1 + row["return_" + curr.name])]
            self.DataFrame["Index_" + curr.name] = Index

        Total = [1000]
        Total_amount = [0]
        for (index, row) in self.DataFrame[1:].iterrows():
            ret = 0
            add = 0
            for curr in self.Currencies:
                if curr != self.Ref.Y:
                    ret += (row["Alloc_" + curr.name] * row["return_" + curr.name])
                    add += self.FXMH.GetFXMarket(row["time"]).ConvertPrice(Price(row["Amount_" + curr.name],curr), self.Ref.Y).Amount
                else:
                    add += row["Amount_" + curr.name]
            Total += [Total[-1] * (1 + ret)]
            Total_amount += [add]
        self.DataFrame["Total"] = Total
        self.DataFrame["Amount"] = Total_amount