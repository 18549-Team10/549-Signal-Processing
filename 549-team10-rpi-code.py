# Simple example of reading the MCP3008 analog input channels and printing
# them all out.
# Author: Tony DiCola
# License: Public Domain
import time

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
        top_x_l.append(copy_l.pop(l.index(max(l))))
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

print('Reading MCP3008 values, press Ctrl-C to quit...')
# Print nice channel column headers.
print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*range(8)))
print('-' * 57)
counter = 0

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
    for i in range(5000):
        val = mcp.read_adc(0)
        next_values.append(val)
        time.sleep(VOLT_3v3)
    pi.wave_tx_stop()
    pi.wave_delete(wid)
    pi.stop()
    allSamplesValues.append(next_values)
    return next_values




def testFrequencyRange(numTimes, pulse):
    handles = []
    opt_frequency = None
    opt_response = None
    frequencies = {}
    responses = []
    
    for j in range(len(freqs)):
        runningSum = 0
        trials = 0
        frequencies[sampleFreqs[j]] = []

        for i in range(numTimes):

            freq = freqs[j]
            # Call test frequency function
            sample_freq_results = testFrequency(freq)
            if (sample_freq_results == -2):
                continue
            else:
                trials += 1
                # Use result to add a plot
                Fs = 0.0000013
                Ts = 1/Fs
                #t = np.arange(0, 1500, 100)
                n = len(sample_freq_results)
                k = np.arange(n)
                T = n/Fs
                frq = k/T
                frq = range(500, 2500, 1) #frq[range(n/2)]
        #        t = np.arange(0, len(sample_freq_results)/2, 0.5)
                print(avg(sample_freq_results))
                freq_response = np.fft.fft(sample_freq_results)/n
                freq_response = freq_response[range(n/2)]
                freq_response = freq_response[500:]
                #freq_response = butter_bandpass_filter(freq_response, 500, 1500, 75000)
                handle, = plt.plot(frq, abs(freq_response))
                handles.append(handle)
                time.sleep(0.5)

                avgVal = top_x_avg(abs(freq_response).tolist(),10)
                runningSum += avgVal
                frequencies[sampleFreqs[j]].append(avgVal)
        #check average against max of previous frequencies
        average = runningSum/trials       
        if (average > opt_response):
            opt_frequency = sampleFreqs[j]
            opt_response = average 
    print(sorted(frequencies.items()))
    return [opt_frequency, opt_response, handles]


'''
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

contentsToWrite = str(allSamplesValues)
writeFile("empty.txt", contentsToWrite)

t = np.arange(0, len(allSamplesValues[0])/2, 0.5)
handles = []
for i in range(len(allSamplesValues)): # TODO: edit this to support freq sweep
    handle = plt.plot(t, allSamplesValues[i], label=("Sample " + str(i)))
    handles.append(handle)'''

numTimes = raw_input("How many trials do you want?")
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
plt.xlabel('Freq (Hz)')
plt.ylabel('|Y(freq)|')
plt.title('Full Bottle Sample')
plt.legend(handles, ('600 Hz', '700 Hz', '800 Hz', '900 Hz', '1000 Hz', '1100 Hz', '1200 Hz', '1300 Hz', '1400 Hz'))
plt.grid(True)
plt.show()

