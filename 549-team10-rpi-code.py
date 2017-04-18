# Simple example of reading the MCP3008 analog input channels and printing
# them all out.
# Author: Tony DiCola
# License: Public Domain
import time
import createTrainingDataMap
import classifySample

################################################################################
# if file does not work, try running with sudo
################################################################################

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

import RPi.GPIO as GPIO

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter
import copy

# Software SPI configuration:
##3.3V = 1 (ADC)
##5V   = 2 (amp)
##GND  = 6
##CLK  = 23
##MISO = 21
##MOSI = 19
##CS   = 24
##mcp  = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
##GPIO4 = 7

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

#transducer output setup
GPIO.setmode(GPIO.BOARD)

# Globals for sampling rates
VOLT_3v3 = 0.0000013

import pigpio

GPIO=4

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def avg(l):
    if (len(l) > 0):
        return (sum(l)/len(l))
    else:
        return None

def top_x_avg(l, x):
    copy_l = copy.deepcopy(l)
    top_x_l = []
    for i in range(x):
        if len(l) > 0: top_x_l.append(copy_l.pop(copy_l.index(max(copy_l))))
    return avg(top_x_l)

freqs = []
sampleFreqs = range(600,1500,100)

# set up frequencies
for freq in sampleFreqs:
    new_square = []
#                                  ON       OFF      MICROS
    new_square.append(pigpio.pulse(1<<GPIO, 0,       1000000/(2*freq)))
    new_square.append(pigpio.pulse(0,       1<<GPIO, 1000000/(2*freq)))
    freqs.append(new_square)

# GPIO.output(3, output)
# Main program loop.
allSamplesValues = []
def testFrequency(f):
    next_values = []
    pi = pigpio.pi() # connect to local Pi
    pi.set_mode(GPIO, pigpio.OUTPUT)
    pi.wave_add_generic(f)
    wid = pi.wave_create()
    if wid < 0: print "error generating wave"; return -2
    pi.wave_send_repeat(wid)
    for i in range(3000):
        val = mcp.read_adc(0)
        next_values.append(val)
        time.sleep(VOLT_3v3)
    pi.wave_tx_stop()
    pi.wave_delete(wid)
    pi.stop()
    allSamplesValues.append(next_values)
    return next_values

allTrials = []
def testFrequencyRange(numTimes, pulse):
    handles = []
    opt_frequency = None
    opt_response = None
    frequencies = {}
    responses = []

    frq = range(500, 1500, 1) #frq[range(n/2)]

    for i in range(numTimes):
        runningSum = 0
        numTrials = 0
        trials = []

        for j in range(len(freqs)):

            freq = freqs[j]
            # Call test frequency function
            try:
                sample_freq_results = testFrequency(freq)
            except:
                print "pigpio failed on the %dth iteration" % i
                break
                
            if (sample_freq_results == -2):
                continue
            else:
                numTrials += 1
                # Use result to add a plot
                Fs = 0.0000013
                Ts = 1/Fs
                #t = np.arange(0, 1500, 100)
                n = len(sample_freq_results)
                #        t = np.arange(0, len(sample_freq_results)/2, 0.5)
                #print(avg(sample_freq_results))
                freq_response = np.fft.fft(sample_freq_results)/n
                freq_response = freq_response[range(n/2)]
                freq_response = freq_response[500:]
                #freq_response = butter_bandpass_filter(freq_response, 500, 1500, 75000)
                handle, = plt.plot(frq, abs(freq_response))
                #print("Index of Maximum Response = " + str())
                max_response_index = abs(freq_response).tolist().index(max(abs(freq_response).tolist()))
                peak_val = frq[max_response_index]
                peak_mag_response = abs(freq_response[max_response_index])
                #print("Peak Value = " + str())
                #print("Peak Mag. Response = " + str(abs()))

                handles.append(handle)
                time.sleep(0.01)
                avgVal = top_x_avg(abs(freq_response).tolist(),5)
                runningSum += avgVal
                #print("Peak Val = " + str(peak_val))
                #print("Peak Mag. Response = " + str(peak_mag_response))
                trials.append(peak_val)
                trials.append(peak_mag_response)
        allTrials.append(trials)
        #check average against max of previous frequencies
        #average = runningSum/trials       
        #if (average > opt_response):
        #    opt_frequency = sampleFreqs[j]
        #    opt_response = average 
    return [opt_frequency, opt_response, handles]

def getSamplePeaks(freqsToTest):
    frq = range(500, 1500, 1)
    peaks = []
    for i in range(len(freqsToTest)):
        sample = testFrequency(freqsToTest[i])        
        n = len(sample)
        freq_response = np.fft.fft(sample)/n
        freq_response = freq_response[range(n/2)]
        freq_response = freq_response[500:]

        max_response_index = abs(freq_response).tolist().index(max(abs(freq_response).tolist()))
        peak_val = frq[max_response_index]
        peak_mag_response = abs(freq_response[max_response_index])
        peaks.append((peak_val, peak_mag_response))
    return peaks

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

# decide if user wants to collect data or test against existing data
user_input = None
while user_input not in ["y","n"]:
    user_input = raw_input("Enter 'y' for collecting test data or 'n' for guessing using existing test data")

# collect data
if user_input == "y":
    numTimes = raw_input("How many trials do you want?")
    print "starting to test %s times..." % numTimes
    [opt_frequency, opt_response,handles] = testFrequencyRange(int(numTimes), freqs)
    print("Optimal Frequency = " + str(opt_frequency))
    print("Optimal Mag. Response = " + str(opt_response))
    if (opt_response < 0.75):
        print("Container is empty!")
    else:
        if (opt_frequency < 1000):
            print ("Container is full!")
        elif (opt_frequency == 1000):
            print ("Container is three-quarters full!")
        elif (opt_frequency == 1100):
            print("Container is half full!")
        elif (opt_frequency == 1200):
            print("Container is a quarter full!")
        else:
            print("Container is empty!")
    #print (allTrials)
    allTrialsStr = str(allTrials)
    #csvStr = ""
    firstIndex = 1
    csvStr = "\n".join([",".join([str(x) for x in trial]) for trial in allTrials])
    '''
    for i in range(len(allTrialsStr)-1):
        if (allTrialsStr[i] == ']') and (allTrialsStr[i+1] == ','):
            thisRow = allTrialsStr[firstIndex:i+1]
            csvStr += thisRow
            newChar = '\n'
            csvStr += newChar
            firstIndex = i+3
            print("First Index Char = " + allTrialsStr[firstIndex])
        elif (allTrialsStr[i] == ']') and (allTrialsStr[i+1] == ']'):
            thisRow = allTrialsStr[firstIndex:i+1]
            csvStr += thisRow'''
    print("CSV Str = " + csvStr)
    writeFile("empty.csv", csvStr)
    plt.xlabel('Freq (Hz)')
    plt.ylabel('|Y(freq)|')
    plt.title('Empty Bottle Sample')
    plt.legend(handles, ('600 Hz', '700 Hz', '800 Hz', '900 Hz', '1000 Hz', '1100 Hz', '1200 Hz', '1300 Hz', '1400 Hz'))
    plt.grid(True)
    plt.show()

# test against existing data
else:
    samplePeaks = getSamplePeaks(freqs)
    writeFile("samplePeaks.csv",",".join([str(x) for x in samplePeaks]))
    trainingDataMap = createTrainingDataMap.createTrainingDataMap()
    guess = classifySample.classify(samplePeaks, trainingDataMap)
    print(guess)

print("done")
