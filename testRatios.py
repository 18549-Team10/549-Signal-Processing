import test

def frange(start, stop, step):
    out = []
    i = start
    while i < stop: 
        out.append(i)
        i += step
    return out

def testRatios(numTrials = 1000):
    tested = set()
    bestRatio, bestScore, allRatios = None, None, []
    for ratio in frange(.01,2,.01):
        score = test.test(numTrials,ratio)
        allRatios.append(score)
        if bestScore == None or score > bestScore:
            bestRatio, bestScore = ratio, score
    for ratio in range(2,100):
        score = test.test(numTrials,ratio)
        allRatios.append(score)
        if bestScore == None or score > bestScore:
            bestRatio, bestScore = ratio, score
    return bestRatio, bestScore, allRatios