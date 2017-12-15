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

    def __init__(self, FXMH: FXMarketHistory, startDate: datetime, ref: Currency = Currency("EUR")):
        self.Ref = ref
        self.Currencies = []
        columns = ["return"]
        self.FXMH = FXMH
        if FXMH.CurrencyRef != ref:
            raise Exception("Wrong FXMarketHistory Reference Currency")
        Curr0 = list(FXMH.DataFrames)[0]
        self.DataFrame = FXMH.DataFrames[Curr0][["time"] + columns]
        self.DataFrame = self.DataFrame[self.DataFrame["time"] >= startDate]
        RenameColumns(self.DataFrame,columns,Curr0)
        self.DataFrame["time"] = self.DataFrame["time"].apply(lambda x:  DateCut(x))
        for curr in FXMH.DataFrames.keys():
            self.Currencies += [curr]
            if curr != Curr0:
                auxDF = FXMH.DataFrames[curr][["time"] + columns]
                self.DataFrame = pd.merge(self.DataFrame, auxDF,how = "left", right_on= "time", left_on = "time")
                RenameColumns(self.DataFrame,columns,curr)

    def AddAllocationHistory2(self, AH: AllocationHistory):
        Percentages = {}
        totalAmount = {}
        fees = {}

        for date in AH.History.keys():
            percent = {}
            amount = 0
            alloc = AH.History[date]
            for cur in alloc.Dictionary:
                allocCur = alloc.Dictionary[cur]
                percent[cur] = [allocCur.Percentage]
                amount += self.FXMH.GetFXMarket(date).ConvertPrice(allocCur.Price, self.Ref).Amount
            totalAmount[date] = amount
            Percentages[date] = percent
            fees[date] = alloc.Fees

        self.Allocation = Percentages
        self.Amount = totalAmount
        self.Fees = fees

    def GetAllocationDate(self, date: datetime):
        res = 0
        dates = list(self.Allocation)
        for idate in dates:
            if res == 0:
                res = idate
            else:
                if res < idate and idate <= date:
                    res = idate
        return res

    def AddAllocationHistory(self, AH: AllocationHistory):
        N = len(self.DataFrame)
        # p: percentage
        # v: value
        dict_p = {}
        dict_v = {}
        last_n = 0
        for alloc in AH.History:
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
        lastAllocDate = 0
        for (index, row) in self.DataFrame[1:].iterrows():
            ret = 0
            date = row["time"]
            AllocDate = self.GetAllocationDate(date)
            Alloc = self.Allocation[AllocDate]
            for curr in self.Currencies:
                allocItem = Alloc.get(curr)
                if allocItem == None:
                    percent = 0
                else:
                    percent = allocItem[0]
                ret += percent * row["return_" + curr.name]
            if AllocDate != lastAllocDate:
                Total_amount += [self.Amount[AllocDate]]
                lastAllocDate = AllocDate
                ret += self.Fees[AllocDate].Percentage * (- 1.00)
            else:
                ret /= (1 - self.Fees[AllocDate].Percentage)
                Total_amount += [Total_amount[-1] * (1 + ret)]

            Total += [Total[-1] * (1 + ret)]
        self.DataFrame["Total"] = Total
        self.DataFrame["Amount"] = Total_amount