
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, text):
    with open(path, "wt") as f:
        f.write(text)

def avg(l):
    if (len(l) > 0):
        return (sum(l)/len(l))
    else:
        return None

trainingData = dict()

def convertCsvToDict(csvFileName, numberOfPeaks):
    dataString = readFile(csvFileName)
    allPeaks = []
    maxPeak = None
    for row in dataString.splitLines():
        row = row.split(",")
        for i in range(len(row) / 2):
            freq,mag = row[2*i],row[2*i+1]
            allPeaks.append((freq,mag))
            if maxPeak == None or mag > maxPeak:
                maxPeak = mag

    # here, we filter our peaks so that we ignore those that are less than 10%
    # of the maximum peak
    allPeaksFiltered = filter(lambda x : x > maxPeak/10,allPeaks)
    allPeaksFiltered.sort()

    indicesToSplit = []
    dists = []
    for i in range(len(allPeaksFiltered) - 1):
        dist = abs(allPeaksFiltered[j] - allPeaksFiltered[j + 1])
        if dist > min(indicesToSplit):
            indicesToSplit = sorted(indicesToSplit)[1:].append(dist)

    indicesToSplit.sort()

    groups = []
    for i in indicesToSplit:
        groups.append(allPeaksFiltered[:i])
        allPeaksFiltered = allPeaksFiltered[i:]
    groups.append(allPeaksFiltered)

    output = []
    for g in groups:
        avgFreq, avgMag = avg([s[0] for s in g]), avg([s[1] for s in g])
        output.append((avgFreq, avgMag))

    return sorted(output)



for s in ['empty','quarter','half','threeQuarters','full']:
    trainingData[s] = convertCsvToDict(s + '.csv', 7)
