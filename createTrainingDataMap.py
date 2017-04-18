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
        print "empty list"
        return None

def convertCsvToDict(csvFileName, numberOfPeaks):
    dataString = readFile(csvFileName)
    allPeaks = []
    maxPeak = None
    for row in dataString.splitlines():
        row = row.split(",")
        for i in range(len(row) / 2):
            if not(row[2*i].isdigit()): continue
            freq,mag = int(row[2*i]),float(row[2*i+1])
            allPeaks.append((freq,mag))
            if maxPeak == None or mag > maxPeak:
                maxPeak = mag

    # here, we filter our peaks so that we ignore those that are less than 10%
    # of the maximum peak
    allPeaksFiltered = filter(lambda (x,y) : y > maxPeak/10,allPeaks)
    allPeaksFiltered.sort()

    indicesToSplit = []
    dists = []
    for i in range(len(allPeaksFiltered) - 1):
        dist = abs(allPeaksFiltered[i][0] - allPeaksFiltered[i + 1][0])
        if len(indicesToSplit) < 9:
            indicesToSplit.append(dist)
        elif dist > min(indicesToSplit):
            indicesToSplit = sorted(indicesToSplit)[1:]
            indicesToSplit.append(dist)

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

def createTrainingDataMap():
    global trainingData
    trainingData = dict()
    for s in ['empty', 'quarter','half','threeQuarters','full']:
        trainingData[s] = convertCsvToDict(s + '.csv', 9)
    return trainingData
