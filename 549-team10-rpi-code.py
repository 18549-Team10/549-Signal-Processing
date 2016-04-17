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

freqs = []

# set up frequencies
for freq in range(600,1500,100):
    new_square = []
#                                  ON       OFF      MICROS
    new_square.append(pigpio.pulse(1<<GPIO, 0,       1000000/(2*freq)))
    new_square.append(pigpio.pulse(0,       1<<GPIO, 1000000/(2*freq)))
    freqs.append(new_square)
    # expectedFreq = 600 Hz | actualFreq = 600 Hz (signal generated from Pi)
    # expectedFreq = 700 Hz | actualFreq = 800 Hz (signal generated from Pi)
    # expectedFreq = 800 Hz | actualFreq = 1000 Hz (signal generated from Pi)
    # expectedFreq = 900 Hz | actualFreq = 1200 Hz (signal generated from Pi)

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



handles = []
for freq in freqs:
    # Call test frequency function
    sample_freq_results = testFrequency(freq)
    if (sample_freq_results == -2):
        continue
    else:
        # Use result to add a plot
        t = np.arange(0, len(sample_freq_results)/2, 0.5)
        handle, = plt.plot(t, sample_freq_results)
        handles.append(handle)
        time.sleep(0.5)


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

plt.xlabel('time (ms)')
plt.ylabel('voltage (% of 3.3V)')
plt.title('Full Bottle Sample - 20.0 kHz')
plt.legend(handles, ('600 Hz', '700 Hz', '800 Hz', '900 Hz', '1000 Hz', '1100 Hz', '1200 Hz', '1300 Hz', '1400 Hz'))
plt.grid(True)
plt.show()

