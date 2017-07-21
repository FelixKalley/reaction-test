#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import math
import numpy
import pyaudio
import sys
import wiimote
import time

# felix: bisherige Funktionalität - wii connecten, A-Knopf spielt kurzen Ton, oder lang bei gedrückt halten.
# felix: +/- Knöpfe erhöhen oder senken Tonhöhe, dauert manchmal kurz.

# felix: Beim starten kommt echt viel text. ich weiß nicht was das ist... scheint vom stream zu sein.


# ----------------------------------------
# felix: altes wimmerbeispiel wiimote demo zum connecten
input("Press the 'sync' button on the back of your Wiimote Plus " +
      "or buttons (1) and (2) on your classic Wiimote.\n" +
      "Press <return> once the Wiimote's LEDs start blinking.")

if len(sys.argv) == 1:
    addr, name = wiimote.find()[0]
elif len(sys.argv) == 2:
    addr = sys.argv[1]
    name = None
elif len(sys.argv) == 3:
    addr, name = sys.argv[1:3]
print(("Connecting to %s (%s)" % (name, addr)))
wm = wiimote.connect(addr, name)
# -----------------------------------------------



# ---------------------------------------------
# http://milkandtang.com/blog/2013/02/16/making-noise-in-python/
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                    channels=1, rate=44100, output=1)


# http://milkandtang.com/blog/2013/02/16/making-noise-in-python/
# felix: macht scheinbar ne kurve aus frequency, length und rate
def sine(frequency, length, rate):
    length = int(length * rate)
    factor = float(frequency) * (math.pi * 2) / rate
    return numpy.sin(numpy.arange(length) * factor)
# ----------------------------------------------


# ------------------------------------------------
# felix: das hier ist die frequenz variable, die hängt irgendwie dumm in der gegend rum.
# felix: ich weiß nicht, wie man das mit der Frequenzänderung anders realisieren könnte, daher erstmal so...
myfrequency = 261
# -------------------------------------------------






# -----------------------------------------------------------
# http://milkandtang.com/blog/2013/02/16/making-noise-in-python/
# felix: length in seconds
# felix: lower frequency = deeper tone
# felix: rate is standard for sound, probably better to not change
# felix: i dont know what chunks and streams are...
def play_tone(stream, frequency, length=0.5, rate=44100):
    chunks = []
    chunks.append(sine(frequency, length, rate))

    chunk = numpy.concatenate(chunks) * 0.25

    stream.write(chunk.astype(numpy.float32).tostring())
# --------------------------------------------------------------


# --------------------------------------------------------------
# erhöht die frequenz um magic number 100
def up_frequency():
    global myfrequency
    myfrequency += 100
    print(myfrequency)

# senkt die frequenz um magic number 100
def down_frequency():
    global myfrequency
    myfrequency -= 100
    print(myfrequency)
# --------------------------------------------------------------




# -------------------------------------------------
# felix: wimmer button zeugs
while True:
    if wm.buttons["A"]:
        play_tone(stream, myfrequency)
    if wm.buttons["Plus"]:
        up_frequency()
    if wm.buttons["Minus"]:
        down_frequency()
    time.sleep(0.1)
#-------------------------------------------------




# ---------------------------------------------
# felix: das killt scheinbar den stream und python audio.
# felix: stand so in dem beispiel, weiß nicht, ob wir das brauchen.
stream.close()
p.terminate()