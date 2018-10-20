#!/usr/bin/env python
from websocket import create_connection

import time
import struct
import collections
import sys
from os import system, name


import numpy as np
import pyaudio

lastChange = time.time()
chan = 1
reset_count = 0
trigger = False
nFFT = 512
BUF_SIZE = 4 * nFFT
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
max_bar_length = 1

blub = list()
peak_buffer = collections.deque(16 * [0], 16)


def animate(stream, MAX_y):
    global trigger
    global chan
    global maxi
    global lastChange
    global max_bar_length
    global reset_count
    N = max(stream.get_read_available() / nFFT, 1) * nFFT
    data = stream.read(int(N))
    # Unpack data, LRLRLR...
    y = np.array(struct.unpack("%dh" % (N * CHANNELS), data)) / MAX_y
    y_L = y[::2]
    Y_L = np.fft.fft(y_L, nFFT)
    test = np.abs(Y_L)
    peak_buffer.appendleft(min(255, int((test[0]/128)*255)))
    peak_buffer.appendleft(min(255, int((test[1]/128)*255)))
    #print(str(sum(peak_buffer)) + ' : ' + str(len(peak_buffer)))
    # col1 = int(sum(peak_buffer) / len(peak_buffer)) # find average of
    bar_length = int(sum(peak_buffer)/2)
    col1 = bar_length
    g_percent = 0.0  # %
    y_percent = 0.5  # %
    r_percent = 0.9  # %
    # print(bar_length)
    # print(max_bar_length)
    g_start = round(g_percent * max_bar_length)
    y_start = round(y_percent * max_bar_length)
    r_start = round(r_percent * max_bar_length)
    #print(bar_length)
    #print(max_bar_length)
    #print(str(g_start) + ' : ' + str(y_start) + ' : ' + str(r_start))
    if bar_length > y_start:
        g_length = round(bar_length - (bar_length - y_start))
    else:
        g_length = bar_length
    g_value = 'G' * g_length
    if bar_length > r_start:
        r_length = round(bar_length - r_start)
        r_value = 'R' * r_length
    else:
        r_length = 0
        r_value = ""
    if bar_length > y_start:
        y_length = round(bar_length - y_start)
        y_value = "Y" * y_length
    else:
        y_length = 0
        y_value = ""
    g_ansi = "\033[1;32m" + g_value + "\x1b[0m"
    y_ansi = "\033[1;33m" + y_value + "\x1b[0m"
    r_ansi = "\033[1;31m" + r_value + "\x1b[0m"
    bar_ansi = g_ansi + y_ansi + r_ansi
    bar = g_value + y_value + r_value
    peak_length = max_bar_length - len(bar)
    print(len(bar))
    print(peak_length)
    peak_pad = ' ' * peak_length
    bar_print = bar_ansi + peak_pad + "\033[1;37m#\x1b[0m"
    if bar_length > max_bar_length:
        reset_count = 0
        max_bar_length = bar_length
    else:
        reset_count += 1
    if reset_count == 50:
        reset_count = 0
        max_bar_length = bar_length
    print(str(reset_count).zfill(2) + " : " + bar_print)

#    if (col1 > 90 and not trigger and (time.time() - lastChange) > 0.5 or (time.time() - lastChange > 5)):
#        lastChange = time.time()
#        trigger = True
#        chan = chan +1
#        if chan > 7:
#            chan = 1
#    if (col1 < 80 and trigger):
#        trigger = False

#   frame = bytearray()
#    chred = col1 if (chan & (1 << 0)) else 0x00
#    chgreen = col1 if (chan & (1 << 1)) else 0x00
#    chblue = col1 if (chan & (1 << 2)) else 0x00
#    r_value = chred
#    g_value = chgreen
#    b_value = chblue
#    mycmd = '{"color":['+str(r_value)+','+str(g_value)+','+str(b_value)+'],"command":"color","priority":100}'
    # print(mycmd)
    # result = send_to_hyperion(mycmd)
    #print(str([chred, chgreen, chblue]))



def main():
    p = pyaudio.PyAudio()
  # Used for normalizing signal. If use paFloat32, then it's already -1..1.
  # Because of saving wave, paInt16 will be easier.
    MAX_y = 2.0 ** (p.get_sample_size(FORMAT) * 8 - 1)
    print(MAX_y)
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output_device_index=2,
                    input=True,
                    output=True,
                    frames_per_buffer=BUF_SIZE)

    while True:
        animate(stream,MAX_y)
        time.sleep(0.01)
        #time.sleep(0.5)
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == '__main__':
    main()
