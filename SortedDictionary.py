

class SortedList():

    def __init__(self):
        self.List = []
        self.N = 0

    def MatchPos(self, value, i0, iN):
        if self.N == 0:
            return (None,None)
        else:
            if value < self.List[0]:
                return (-1, False)
            elif value > self.List[self.N - 1]:
                return (self.N - 1,False)
            else:

                continueFunction = True
                while(continueFunction):

                    if i0 >= iN or min(i0,iN) < 0  or max(i0,iN - 1) >= self.N:
                        return (None, False)

                    if i0 + 1 == iN:
                        x = self.List[i0]
                        if x > value:
                            return (i0 - 1, False)
                        else:
                            return (i0, x == value)

                    elif i0 + 2 == iN:
                        x= self.List[i0]
                        if x == value:
                            return (i0, True)
                        elif x > value:
                            return (i0 - 1, False)
                        else:
                            x1 = self.List[i0 + 1]
                            if x1 <= value:
                                return (i0 + 1,  x1 == value)
                            else:
                                return(i0,False)

                    else:
                        i = int((iN - i0)/2) + i0
                        x = self.List[i]
                        if x == value:
                            return (i,True)
                        elif x < value:
                            i0 = i + 1
                        else:
                            iN = i + 1

    def Get(self,i):
        return self.List[i]

    def Match(self, value):
        return self.MatchPos(value, 0, self.N)



    def Add(self, value):
        if self.N == 0:
            self.List = [value]
            self.N = 1
            return (-1,False)
        else:
            (i,test) = self.Match(value)
            if i == -1:
                self.List = [value] + self.List
                self.N += 1
            else:
                if not(test):
                    if i == self.N:
                        self.List = self.List[:(i+1)] + [value]
                    else:
                        self.List = self.List[:(i+1)] + [value] + self.List[(i+1):]
                    self.N += 1
            return (i,test)

    def AddList(self, List):
        for x in List:
            self.Add(x)


class SortedDictionary:
    def __init__(self):
        self.Keys = SortedList()
        self.Dictionary = {}

    def Add(self, key, value):
        self.Keys.Add(key)
        self.Dictionary[key] = value

    def Get(self, key):
        if self.Keys.N == 0:
            return (None,None)
        else:
            (i,test) = self.Keys.Match(key)
            return (self.Dictionary[self.Keys.Get(i)],test)

    @property
    def ToString(self):
        res = ""
        for i in range(self.Keys.N):
            key = self.Keys.Get(i)
            res += str(key) + " : " + str(self.Dictionary[key]) + "\n"
        return res





