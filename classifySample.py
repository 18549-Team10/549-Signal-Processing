# given: single sample's peaks from container with unknown amount of liquid, map created from training data
# goal: classify sample with best guess of amount of liquid in container

def bestMatch(freq, mag, mapPeaks):
    minDist = None
    bestFreq, bestMag = None, None
    for (mapFreq, mapMag):
        dist = abs(mapFreq - freq)
        if minDist == None or dist < minDist:
            minDist = dist
            bestFreq, bestMag = mapFreq, mapMag
    return bestFreq, best Mag

def score(samplePeaks, mapPeaks):
    totalScore = 0
	for (freq,mag) in samplePeaks:
        matchFreq,matchMag = bestMatch(freq,mag, mapPeaks)
        freqDiff = abs(freq - matchFreq)
        magDiff = abs(mag - matchMag)
        totalScore += 1 / freqDiff
    return totalScore	

def classify(samplePeaks, trainingDataMap):
	bestScore = None
	bestMatch = []
	for fillLevel in trainingDataMap.keys():
		currScore = score(samplePeaks, trainingDataMap[fillLevel])
		if currScore > bestScore:
			bestScore = currScore
			bestMatch = [fillLevel]
		elif currScore == bestScore:
			bestMatch.append(fillLevel)
	return bestMatch