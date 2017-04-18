import createTrainingDataMap
import classifySample
import random

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

fingerprints = createTrainingDataMap.createTrainingDataMap()

def test(numTrials = 1, ratio = 1.0):
    correct = 0
    for i in range(numTrials):
        sample = []
        while len(sample) == 0: # error catching in case we choose an empty line
            sampleCsv = random.choice(['empty','quarter','half','threeQuarters','full'])
            samplePeaksString = readFile(sampleCsv + ".csv")
            samplePeaks = random.choice(samplePeaksString.splitlines()).split(",")
            for i in range(len(samplePeaks) / 2):
                if not(samplePeaks[2*i].isdigit()): continue
                freq,mag = int(samplePeaks[2*i]),float(samplePeaks[2*i+1])
                sample.append((freq,mag))

        calculated = classifySample.classify(sample, fingerprints, ratio)
        # if len(calculated) > 1 or calculated[0] != sampleCsv:
        #     print "expected:", sampleCsv, "calculated:", calculated
        correct += calculated[0] == sampleCsv
    return 1.0 * correct / numTrials
    
