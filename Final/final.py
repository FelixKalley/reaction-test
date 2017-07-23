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
        self.counter = 5
        self.initUI()
        #h ttp://www.sengpielaudio.com/Rechner-notennamen.htm
        # self.notelist = [261.626, 277.183, 293.665, 311.127, 329.628, 349.228, 369.994, 391.995, 415.305, 440.000, 
        #                  466.164, 493.883, 523.251, 554.365, 587.330, 622.254, 659.255, 698.456, 739.989, 783.991, 
        #                  830.609, 880.000, 932.328, 987.767, 1046.500]
        # Nur töne ohne # und b 
        self.notelist = [261.626, 293.665, 329.628, 349.228, 391.995, 440.000,
                         493.883, 523.251, 587.330, 659.255, 698.456, 783.991, 
                         880.000, 987.767, 1046.500]
        # height of tone (in application)
        self.noteLineConnection = [263, 253, 243, 233, 223, 213,
                                   203, 193, 183, 173, 163, 153,
                                   143, 133, 123]
        self.myfrequency = self.notelist[self.counter]
        self.played_notes = []
        self.mode = 0
        self.mode_record = 0
        self.mode_play = 1
        self.mode_volume = 2
        self.note_line_heights =  [(80, -70, 30, 200), (80, -50, 30, 200), (80, 70, 30, 200)]
        self.redoable_notes = []        

    # init the ui
    def initUI(self):
        # load ui file
        self.ui = uic.loadUi("final.ui", self)
        self.show()

        self.ui.connectWiiMoteButton.clicked.connect(self.connect_wiimote)
    
    # handles paint events
    def paintEvent(self, event):
        # initializes QPainter
        qp = QtGui.QPainter()
        # starts painting
        qp.begin(self)
        qp.setBrush(QtGui.QColor(0, 0, 0))
        for index, note in enumerate(self.played_notes):
            old_notes_height = self.noteLineConnection[note]
            qp.drawEllipse(95 + index * 40, old_notes_height, 20, 15)
            if(old_notes_height == 263 or old_notes_height == 123 or old_notes_height == 143):
                self.add_line_to_note(old_notes_height, qp, index)
            
        height = self.noteLineConnection[self.counter]
        
        
        if(height == 263 or height == 123 or height == 143):
            self.add_line_to_note(height, qp, len(self.played_notes))
        
        if(self.mode is self.mode_record):
            qp.setBrush(QtGui.QColor(70, 70, 70))
            # sets color
            # draws a circle
            qp.drawEllipse(95 + len(self.played_notes) * 40, height, 20, 15)
        # ends painting
        qp.end()


    def add_line_to_note(self, heightOfTone, qp, index):
        x1 = 90 + index * 40
        x2 = 120 + index * 40
        
        line = QtCore.QLine(x1, heightOfTone + 7, x2, heightOfTone + 7)
        print(x1, heightOfTone + 7, x2, heightOfTone + 7)
        qp.drawLine(line)
    
    # connect to WiiMote with given MAC-address
    # Lena: kann man das irgendwie automatisch machen?
    def connect_wiimote(self):        
        if len(sys.argv) == 1:
            addr, name = wiimote.find()[0]
        elif len(sys.argv) == 2:
            addr = sys.argv[1]
            name = None
        elif len(sys.argv) == 3:
            addr, name = sys.argv[1:3]
        print(("Connecting to %s (%s)" % (name, addr)))
        self.wm = wiimote.connect(addr, name)
        
        self.prepareSound()

        self.registerButtons()

    def undo(self):
        if( not len(self.played_notes) == 0):            
            self.redoable_notes.append(self.played_notes[-1])
            self.played_notes = self.played_notes[:-1]
            self.update()
    
    def redo(self):
        if(not len(self.redoable_notes) == 0):
            self.played_notes.append(self.redoable_notes[-1])
            self.redoable_notes = self.redoable_notes[:-1]
            print(self.played_notes)
            print(self.redoable_notes)
            self.update()


    # While-Schleife um auf Button presses zu hören (muss umgebaut werden)
    # das muss irgendwie mit signal und slot funktionieren... aber wie???
    def registerButtons(self):
        self.wm.buttons.register_callback(self.button_changed)
            
     
    def button_changed(self, changed):
        if not changed:
            pass
        else:
            if(("A", True) in changed):
                if(self.mode is self.mode_record):
                    self.redoable_notes = []
                    self.play_tone(self.myfrequency)
                    self.add_tone_to_melody()
                elif(self.mode is self.mode_play):
                    self.play_melody()
                elif(self.mode is self.mode_volume):
                    print("change volume")
            elif(("One", True) in changed):
                if(self.mode is self.mode_record):
                    self.undo()
            elif(("Two", True) in changed):
                if(self.mode is self.mode_record):
                    self.redo()
            elif(("Plus", True) in changed):
                self.up_frequency()
            elif(("Minus", True) in changed):
                self.down_frequency()
            elif(("B", True) in changed):
                self.change_mode()
                self.update()
                
    def change_mode(self):
        if(self.mode is 0):
            self.mode = self.mode_play
        elif(self.mode is 1):
            self.mode = self.mode_volume
        else:
            self.mode = self.mode_record
          
    def play_melody(self):
        for note in self.played_notes:
            time.sleep(0.1)
            self.play_tone(self.notelist[note])
    
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
    def play_tone(self, frequency, length=0.5, rate=44100):
        chunks = []
        chunks.append(self.sine(frequency, length, rate))
        chunk = numpy.concatenate(chunks)

        self.stream.write(chunk.astype(numpy.float32).tostring())

    def add_tone_to_melody(self):
        self.played_notes.append(self.counter)
        self.update()


    def up_frequency(self):
        if self.counter < len(self.notelist)-1:
            self.counter +=1
            self.myfrequency = self.notelist[self.counter]
            print("up")
            self.update()
    

    def down_frequency(self):
        if self.counter > 0:
            self.counter -=1
            self.myfrequency = self.notelist[self.counter]
            print("down")
            self.update()

    
    
        # felix: das killt scheinbar den stream und python audio.
        # felix: stand so in dem beispiel, weiß nicht, ob wir das brauchen.
        # self.stream.close()
        # p.terminate()

def main():
    app = QtWidgets.QApplication(sys.argv)
    musicMaker = MusicMaker()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


