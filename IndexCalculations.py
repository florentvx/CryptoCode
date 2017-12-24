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

    def __init__(self, AH : AllocationHistory, FXMH: FXMarketHistory):
        self.Currencies = AH.Currencies
        self.CurrencyRef = FXMH.CurrencyRef

        Spots = {}
        Allocs = {}
        Total = []
        Dates = []
        for cur in self.Currencies + [self.CurrencyRef]:
            Spots[cur] = []
            Allocs[cur] = []
        for date in AH.History.Keys:
            Dates += [date]
            alloc = AH.GetAllocation(date)[0]
            Total += [alloc.Total.Amount]
            FX = FXMH.GetFXMarket(date)
            for cur in self.Currencies:
                Spots[cur] += [FX.GetFXRate(cur, self.CurrencyRef)]
                try:
                    Allocs[cur] += [alloc.Dictionary[cur].Percentage]
                except:
                    Allocs[cur] += [0]
            Allocs[self.CurrencyRef] += [alloc.Dictionary[self.CurrencyRef].Percentage]

        DF = pd.DataFrame()
        DF["date"] = Dates

        DF["Total"] = Total
        for cur in self.Currencies + [self.CurrencyRef]:

            if cur != self.CurrencyRef:
                DF["Spot_" + cur.ToString] = Spots[cur]
            DF["Alloc_" + cur.ToString] = Allocs[cur]
        self.DataFrame = DF