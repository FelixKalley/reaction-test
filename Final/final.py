#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import math
import numpy
import pyaudio
import sys
import wiimote
import time
from PyQt5 import uic, QtWidgets, QtCore, QtGui

# felix: bisherige Funktionalität - wii connecten, A-Knopf spielt kurzen Ton, oder lang bei gedrückt halten.
# felix: +/- Knöpfe erhöhen oder senken Tonhöhe, dauert manchmal kurz.

# felix: Beim starten kommt echt viel text. ich weiß nicht was das ist... scheint vom stream zu sein.


class MusicMaker(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()
        # felix: das hier ist die frequenz variable, die hängt irgendwie dumm in der gegend rum.
        # felix: ich weiß nicht, wie man das mit der Frequenzänderung anders realisieren könnte, daher erstmal so...
        # lena: die frequenzen ändern sich pro ton nicht gleichmäßig ändert,
        #       würde ich eine Liste an möglichen Tönen vorgeben?
        self.myfrequency = 261
        self.connect_wiimote()
        self.prepareSound()
        self.registerButtons()

    # connect to WiiMote with given MAC-address
    # Lena: muss noch umgebaut werden für Oberfläche!
    def connect_wiimote(self):
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
        self.wm = wiimote.connect(addr, name)

    # While-Schleife um auf Button presses zu hören (muss umgebaut werden)
    def registerButtons(self):
        while True:
            if self.wm.buttons["A"]:
                self.play_tone(self.myfrequency)
            if self.wm.buttons["Plus"]:
                self.up_frequency()
            if self.wm.buttons["Minus"]:
                self.down_frequency()
            time.sleep(0.1)

        # felix: das killt scheinbar den stream und python audio.
        # felix: stand so in dem beispiel, weiß nicht, ob wir das brauchen.
        self.stream.close()
        p.terminate()
    
    # http://milkandtang.com/blog/2013/02/16/making-noise-in-python/
    def prepareSound(self):
        p = pyaudio.PyAudio()
        self.stream = p.open(format=pyaudio.paFloat32,
                        channels=1, rate=44100, output=1)
        
        
    # http://milkandtang.com/blog/2013/02/16/making-noise-in-python/
    def sine(self, frequency, length, rate):
        length = int(length * rate)
        factor = float(frequency) * (math.pi * 2) / rate
        return numpy.sin(numpy.arange(length) * factor)

    # http://milkandtang.com/blog/2013/02/16/making-noise-in-python/
    # length in seconds
    # lower frequency = deeper tone
    # standard rate is 44.1kHz
    # felix: i dont know what chunks and streams are...
    def play_tone(self, frequency, length=1, rate=44100):
        chunks = []
        chunks.append(self.sine(frequency, length, rate) / 2)
    
        chunk = numpy.concatenate(chunks) * 0.25
    
        self.stream.write(chunk.astype(numpy.float32).tostring())


    # erhöht die frequenz um magic number 100
    def up_frequency(self):
        self.myfrequency += 100
        print(self.myfrequency)
    
    # senkt die frequenz um magic number 100
    def down_frequency(self):
        self.myfrequency -= 100
        print(self.myfrequency)
    

def main():
    app = QtWidgets.QApplication(sys.argv)
    musicMaker = MusicMaker()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


