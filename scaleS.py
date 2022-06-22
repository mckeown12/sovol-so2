import re
from tqdm import tqdm
import pandas as pd
import numpy as np

with open('./so-2 data file/material code/laser/sunflower.nc', 'r') as f:
    gString = f.read()

p = re.compile('S(\d+)')
x = p.sub(lambda x: 'S'+str(int(x.group(1))/2), gString)


def getComponent(Letter, gcode):
    comp = re.compile(Letter+'(\d*\.?\d+)')
    x =  comp.search(gcode)
    if x is None:
        return x
    f = float(x[1])
    intIsh = int(f)
    if intIsh == f:
        return intIsh
    return f

def gCodeToDf(gcode):
    linez = []
    for line in tqdm(gcode.split('\n')):
        myDict = {}
        for letter in ['G', 'M', 'X', 'Y', 'F', 'S']:
            myDict[letter] = getComponent(letter, line)
        linez.append(myDict)
    return pd.DataFrame(linez)

def dictToGStringLine(d):
    myStr = ''
    for k,v in d.items():
        if not np.isnan(v):
            if v == int(v):
                v = int(v)
            myStr = myStr + ' ' + str(k) + str(v)
    return myStr[1:]

def dfToGCode(df):
    myListOfDicts = df.to_dict(orient='records')
    lines = []
    for l in tqdm(myListOfDicts):
        lines.append(dictToGStringLine(l))
    return '\n'.join(lines)

# print(gString)
df = gCodeToDf(gString)
gcode = dfToGCode(df)

print('gString: ', gString[:200])
print('gcode: ', gcode[:200])