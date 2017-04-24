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

def weightedAvg(l):
    # requires: l is a list of tuples, each of the form (value, weight)
    totalWeight = sum(map(lambda (x,y) : y, l))
    return sum(map(lambda (x,y) : x*y, l)) / totalWeight

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
    # allPeaksFiltered = allPeaks
    allPeaksFiltered = filter(lambda (x,y) : y > maxPeak/50,allPeaks)
    allPeaksFiltered.sort()

    dists = []
    for i in range(1, len(allPeaksFiltered)):
        dist = abs(allPeaksFiltered[i][0] - allPeaksFiltered[i - 1][0])
        dists.append((dist,i))

    indicesToSplit = sorted([i for (dist,i) in sorted(dists)[len(dists) - numberOfPeaks:]])
    print (indicesToSplit)

    groups = []
    j  = 0
    for i in indicesToSplit:
        groups.append(allPeaksFiltered[:i-j])
        allPeaksFiltered = allPeaksFiltered[i-j:]
        j = i
    groups.append(allPeaksFiltered)
    # print groups
    output = []
    maxMag = None
    for g in groups:
        avgFreq, avgMag = weightedAvg(g), avg([s[1] for s in g])
        if maxMag == None or avgMag > maxMag: maxMag = avgMag
        output.append((avgFreq, avgMag))
    
    # output = map(lambda (x,y) : (x,1.0*y/maxMag), output) # lowers best accuracy from about .59 to .537

    return sorted(output)

def createTrainingDataMap():
    global trainingData
    trainingData = dict()
    for s in ['empty','quarter','half','threeQuarters','full']:
        trainingData[s] = convertCsvToDict(s + '.csv', 10)
    print trainingData
    return trainingData

# FIXED RATIO: .07
# peaks success close
#     2    .499  .602
#     3    .540  .431
#     4    .539  .463
#     5    .444  .359
#     6    .511  .458
#     7    .480  .448

# BEST RATIO
# peaks  ratio  success  close
#     2     .2     .516   .641
#     3    .15     .584   .466
#     4    .07     .552   .478
#     5    .02     .488   .342
#     6    1.9     .549   .508
#     7    .09     .517   .443
#     8    .11     .601   .573
#     9    .09     .597   .449
#    10    .07     .616   .474
#    11    .02     .606   .482
#    12    .04     .601   .461

# BEST RATIO with cutting bottom <cut>
# peaks     cut  ratio  success  close
#    10     1/5    .14     .419   .274
#    10    1/50    .01     .643   .485
#    10  no cut    .01     .609   .325
#    10  no cut      0     .575   .412
#    10    1/50      0     .559   .448
#    10    1/50   .005     .609   .482
#    10    1/50   .015     .587   .536

# with weighted avg of peaks, rather than normal avg
# peaks    cut  ratio  success  close
#    10   1/50    .