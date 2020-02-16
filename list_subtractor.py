# Just a handy program for figuring out the delta between two lists of Chinese characters

from hanziconv import HanziConv


class MyList(list):
    def __init__(self, *args):
        super(MyList, self).__init__(args)

    def __sub__(self, other):
        return self.__class__(*[item for item in self if item not in other])


with open("hsk_4.txt", encoding="utf-8-sig") as f:
    hsk4 = f.readlines()
    hsk4 = [x.strip() for x in hsk4]
    hsk4 = [HanziConv.toSimplified(x) for x in hsk4]

with open("hsk_5.txt", encoding="utf-8-sig") as f:
    hsk5 = f.readlines()
    hsk5 = [x.strip() for x in hsk5]

with open("output.txt", 'w', encoding="utf-8-sig") as f:

    for word in hsk5:
        if word not in hsk4:
            f.write(word.strip() + "\r")
        else:
            print("DUPLICATE: " + word.strip())
