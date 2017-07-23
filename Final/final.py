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
        self.counter = 5
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
        # current frequency
        self.myfrequency = self.notelist[self.counter]
        # already played notes
        self.played_notes = []
        # current mode
        self.mode = 0
        # mode to record tones
        self.mode_record = 0
        # mode to play melody
        self.mode_play = 1
        # mode to change volume
        self.mode_volume = 2
        # list with redoable tones, cleared if new tone entered
        self.redoable_notes = []
        # defines where to start to draw the notes
        self.offset = 95

        self.initUI()

    # init the ui
    def initUI(self):
        # load ui file
        self.ui = uic.loadUi("final.ui", self)
        self.show()

        # listener to comboBox index change
        self.ui.modeComboBox.currentIndexChanged.connect(self.set_new_mode)
        # listener to connect button
        self.ui.connectWiiMoteButton.clicked.connect(self.connect_wiimote)

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

    # register callback for button clicks
    def registerButtons(self):
        self.wm.buttons.register_callback(self.button_changed)

    # listen to the buttons and do action if button's clicked
    def button_changed(self, changed):
        if not changed:
            pass
        else:
            # button to select tone or start play melody
            if(("A", True) in changed):
                if(self.mode is self.mode_record):
                    self.redoable_notes = []
                    self.play_tone(self.myfrequency)
                    self.add_tone_to_melody()
                    self.shift_notes_record()
                elif(self.mode is self.mode_play):
                    self.play_melody()
                # wird noch ersetzt durch drehen
                elif(self.mode is self.mode_volume):
                    print("change volume")
            # if mode is record, undo last note
            elif(("One", True) in changed):
                if(self.mode is self.mode_record):
                    self.undo()
                    self.shift_notes_record()
            # if mode is record, redo last undone note
            elif(("Two", True) in changed):
                if(self.mode is self.mode_record):
                    self.redo()
                    self.shift_notes_record()
            # ändern auf hoch und runter
            elif(("Plus", True) in changed):
                self.up_frequency()
            # ändern auf hoch und runter
            elif(("Minus", True) in changed):
                self.down_frequency()
            # change mode to next
            elif(("B", True) in changed):
                self.change_mode()

    # handles paint events
    def paintEvent(self, event):
        # initializes QPainter
        qp = QtGui.QPainter()
        # starts painting
        qp.begin(self)
        # fill following notes black
        qp.setBrush(QtGui.QColor(0, 0, 0))
        # loop through played notes and paint them (with additional lines if needed)
        for index, note in enumerate(self.played_notes):
            old_notes_height = self.noteLineConnection[note]
            # draws the tone
            qp.drawEllipse(self.offset + index * 40, old_notes_height, 20, 15)
            # notes 263, 123 and 143 are the ones with additional line
            if(old_notes_height == 263 or old_notes_height == 123 or old_notes_height == 143):
                self.add_line_to_note(old_notes_height, qp, index)

        # draw current note (only in record mode)
        if(self.mode is self.mode_record):
            height = self.noteLineConnection[self.counter]
            # notes 263, 123 and 143 are the ones with additional line
            if(height == 263 or height == 123 or height == 143):
                self.add_line_to_note(height, qp, len(self.played_notes))
            # fill current note grey
            qp.setBrush(QtGui.QColor(70, 70, 70))
            # draws the tone
            qp.drawEllipse(self.offset + len(self.played_notes) * 40, height, 20, 15)
        # ends painting
        qp.end()

    # adds the line to a note
    def add_line_to_note(self, heightOfTone, qp, index):
        x1 = self.offset - 5 + index * 40
        x2 = self.offset + 30 + index * 40
        
        line = QtCore.QLine(x1, heightOfTone + 7, x2, heightOfTone + 7)
        qp.drawLine(line)
    
    # sets the new mode if change per mouse on combobox
    def set_new_mode(self, mode):
        self.mode = mode
        self.update()

    # change mode between record, play and change volume
    def change_mode(self):
        if(self.mode is self.mode_record):
            # shift notes so first note is shown
            self.shift_notes_play(0)
            self.mode = self.mode_play
        elif(self.mode is self.mode_play):
            self.mode = self.mode_volume
        else:
            # shift notes so if the line is more than full, the last one is shown
            self.shift_notes_record()
            self.mode = self.mode_record

        # set index of combobox to new mode
        self.ui.modeComboBox.setCurrentIndex(self.mode)
        # paint new
        self.update()

    # shifts the notes, so the last note can be seen
    def shift_notes_record(self):
        # momentan passen 12 Noten ins Fenster
        if(len(self.played_notes) > 12):
            self.offset = 95 - (len(self.played_notes) - 12) * 40
        else:
            self.offset = 95
    
    # shifts the notes, so the current note can be seen
    def shift_notes_play(self, index):
        # momentan passen 12 Noten ins Fenster
        if(index > 12):
            self.offset = 95 - (index - 12) * 40
        else:
            self.offset = 95

    # undo last note if there is one
    def undo(self):
        if( not len(self.played_notes) == 0):            
            self.redoable_notes.append(self.played_notes[-1])
            self.played_notes = self.played_notes[:-1]
            self.update()

    # redo last undone note if there was one
    def redo(self):
        if(not len(self.redoable_notes) == 0):
            self.played_notes.append(self.redoable_notes[-1])
            self.redoable_notes = self.redoable_notes[:-1]
            self.update()

    # play the full melody and shift, so current note is seen
    def play_melody(self):
        for index, note in enumerate(self.played_notes):
            self.shift_notes_play(index)
            self.play_tone(self.notelist[note])
            self.update()
            time.sleep(0.1)

    # add a tone to the melody and redraw
    def add_tone_to_melody(self):
        self.played_notes.append(self.counter)
        self.update()

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
    def play_tone(self, frequency, length=0.5, rate=44100):
        chunks = []
        chunks.append(self.sine(frequency, length, rate))
        chunk = numpy.concatenate(chunks)

        self.stream.write(chunk.astype(numpy.float32).tostring())

    # wird noch angepasst mit wiimote bewegung
    def up_frequency(self):
        if self.counter < len(self.notelist)-1:
            self.counter +=1
            self.myfrequency = self.notelist[self.counter]
            self.update()

    # wird noch angepasst mit wiimote bewegung
    def down_frequency(self):
        if self.counter > 0:
            self.counter -=1
            self.myfrequency = self.notelist[self.counter]
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
