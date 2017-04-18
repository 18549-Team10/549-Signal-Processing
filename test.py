import createTrainingDataMap
import classifySample

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

sample = readFile("samplePeaks.csv")

fingerprints = createTrainingDataMap.createTrainingDataMap()

def unstringify(s):
    s = s.split(",")
    freqs, mags = [], []
    for i in range(len(s)):
        if i % 2 == 0: # frequency
            freqs.append(int(s[i].strip("(")))
        else: # magnitude
            mags.append(float(s[i].strip(")").strip(" ")))
    return zip(freqs,mags)

print(classifySample.classify(unstringify(sample), fingerprints))
