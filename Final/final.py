#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import math
import numpy
import pyaudio
import sys
import wiimote
import time
import wave
from PyQt5 import uic, QtWidgets, QtCore, QtGui

# felix: bisherige Funktionalität - wii connecten, A-Knopf spielt kurzen Ton, oder lang bei gedrückt halten.
# felix: +/- Knöpfe erhöhen oder senken Tonhöhe, dauert manchmal kurz.

# felix: Beim starten kommt echt viel text. ich weiß nicht was das ist... scheint vom stream zu sein.


class MusicMaker(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()
        self.counter = 6
        self.type_counter = 0
        #h ttp://www.sengpielaudio.com/Rechner-notennamen.htm
        # self.notelist = [261.626, 277.183, 293.665, 311.127, 329.628, 349.228, 369.994, 391.995, 415.305, 440.000, 
        #                  466.164, 493.883, 523.251, 554.365, 587.330, 622.254, 659.255, 698.456, 739.989, 783.991, 
        #                  830.609, 880.000, 932.328, 987.767, 1046.500]
        # Nur töne ohne # und b 
        self.notelist = [261.626, 293.665, 329.628, 349.228, 391.995, 440.000,
                         493.883, 523.251, 587.330, 659.255, 698.456, 783.991,
                         880.000, 987.767, 1046.500]
        self.typelist = [0.25, 0.5, 1.0]
        # height of tone (in application)
        self.noteLineConnection = [263, 253, 243, 233, 223, 213,
                                   203, 193, 183, 173, 163, 153,
                                   143, 133, 123]
        # current frequency
        self.myfrequency = self.notelist[self.counter]
        self.mytype = self.typelist[self.type_counter]
        # already played notes
        self.played_notes = []
        # list with redoable tones, cleared if new tone entered
        self.redoable_notes = []
        # defines where to start to draw the notes
        self.offset = 95
        # adress of used wiimotes
        self.standard_wiimotes = ["00:1F:C5:3F:AA:F1", "18:2a:7b:f3:f1:68"]
        # starting volume
        self.volume = 1
        # maximal volume
        self.max_volume = 2
        self.volume_step = 0.2
        # initial state of set start values from axes
        self.start_axpos_set = False
        # start values for axes
        self.start_xyz = []
        # range for axes
        self.max_range_value = 200
        # range arrays for notes and types
        self.note_ranges = []
        self.type_ranges = []
        self.initUI()

    # init the ui
    def initUI(self):
        # load ui file
        self.ui = uic.loadUi("final.ui", self)
        self.show()
        
        # combobox for wiimote address
        self.ui.wiiMoteAddresses.addItems(self.standard_wiimotes)
        # listener to connect button
        self.ui.connectWiiMoteButton.clicked.connect(self.connect_wiimote)
        self.ui.recalibrateWiiMoteButton.clicked.connect(self.recalibrate_wiimote)

    # connect to WiiMote with given MAC-address
    def connect_wiimote(self):
        name = None
        addr = self.ui.wiiMoteAddresses.currentText()
        print(("Connecting to %s (%s)" % (name, addr)))
        #try:
        self.wm = wiimote.connect(addr, name)
        self.ui.label_cannot_connect.setText("")
        self.prepareSound()
        self.registerButtons()
        self.trackAxes()
        self.connectWiiMoteButton.setEnabled(False)
        #except:
        #    print("Cannot connect to WiiMote!")
        #    self.ui.label_cannot_connect.setText("Cannot connect to WiiMote!")
    # register callback for button clicks
    def registerButtons(self):
        self.wm.buttons.register_callback(self.button_changed)

    def recalibrate_wiimote(self):
    	self.start_axpos_set = False


    def trackAxes(self):
        self.wm.accelerometer.register_callback(self.axis_changed)

    def axis_changed(self, state):
        if not self.start_axpos_set:
               self.start_xyz = [state]
               self.generate_range_values(self.start_xyz)
               self.start_axpos_set = True
        else:
            for x in range(0, len(self.notelist)):
                if self.note_ranges[x][0] <= state[1] <= self.note_ranges[x][1]:
                    self.myfrequency = self.notelist[len(self.notelist)-1-x]
                    if(not self.counter == len(self.notelist)-1-x):
                        #self.play_tone(self.myfrequency, 0.3)
                        self.counter = len(self.notelist)-1-x
                        self.update()
            for x in range(0, len(self.typelist)):
                if self.type_ranges[x][0] <= state[0] <= self.type_ranges[x][1]:
                    self.mytype = self.typelist[x]
                    self.type_counter = x
                    self.update()

    def generate_range_values(self, start_xyz):
        #range values for note frequencies
        if len(self.notelist)%2 == 0:
            # for other notes, implement stuff here
            print("Please rework the method \"generate_range_values\", if you wanna work with more notes.")
        else:
            tuple_distance = 4
            tuple_range = 8
            middle_value = start_xyz[0][1]
            middle_tuple = (middle_value-tuple_range/2, middle_value+tuple_range/2)
            for x in range (0, int((len(self.notelist)-1)/2)):
                next_tuple = (middle_tuple[0]-x*(tuple_range+tuple_distance), middle_tuple[1]-x*(tuple_range+tuple_distance))
                self.note_ranges.insert(0, next_tuple)
            for x in range (int((len(self.notelist)-1)/2), len(self.notelist)):
                next_tuple = (middle_tuple[0]+(x+1-int((len(self.notelist)-1)/2))*(tuple_range+tuple_distance), middle_tuple[1]+(x+1-int((len(self.notelist)-1)/2))*(tuple_range+tuple_distance))
                self.note_ranges.insert(x, next_tuple)

        # range values for note type
        if len(self.typelist)%2 == 0:
            # for other notes, implement stuff here
            print("Please rework the method \"generate_range_values\", if you wanna work with more types of notes.")
        else:
            tuple_distance = 10
            tuple_range = 60
            middle_value = start_xyz[0][0]
            middle_tuple = (middle_value-tuple_range/2, middle_value+tuple_range/2)
        for x in range (0, int((len(self.typelist)-1))):
            next_tuple = (middle_tuple[0]-x*(tuple_range+tuple_distance), middle_tuple[1]-x*(tuple_range+tuple_distance))
            self.type_ranges.insert(0, next_tuple)
        for x in range (int((len(self.typelist)-1)), len(self.typelist)):
            next_tuple = (middle_tuple[0]+(x/2)*(tuple_range+tuple_distance), middle_tuple[1]+(x/2)*(tuple_range+tuple_distance))
            self.type_ranges.insert(x, next_tuple)

    # listen to the buttons and do action if button's clicked
    def button_changed(self, changed):
        if not changed:
            pass
        else:
            # button to select tone
            if(("A", True) in changed):
                self.redoable_notes = []
                #self.play_tone(self.myfrequency, self.typelist[self.type_counter] * 2)
                self.add_tone_to_melody()
                self.shift_notes_record()
            # play melody
            elif (("Down", True) in changed):
                self.play_melody()
            # undo last note
            elif(("B", True) in changed):
                self.undo()
                self.shift_notes_record()
            # redo last undone note
            elif(("One", True) in changed):
                self.redo()
                self.shift_notes_record()
            # save melody as wav file
            elif(("Two", True) in changed):
                self.save_file()
            # higher volume
            elif(("Plus", True) in changed):
                self.up_volume()
            # lower volume
            elif(("Minus", True) in changed):
                self.down_volume()
            # close application
            elif (("Home", True) in changed):
                self.stream.close()
                self.p.terminate()
                # Das wirft eine Exception!
                self.close()

    def save_file(self):
        f = wave.open("melody.wav", 'w')
        f.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
        chunks = []
        for index, note in enumerate(self.played_notes):
            chunks.append(self.sine(note[0], note[1], 44100))
            chunk = numpy.concatenate(chunks)

        f.writeframesraw(chunk)

        # f.writeframesraw(chunk.astype(numpy.float32).tostring())
    
    # handles paint events
    def paintEvent(self, event):
        # initializes QPainter
        qp = QtGui.QPainter()
        # starts painting
        qp.begin(self)
        # fill following notes black

        # set width of lines to 2
        pen = QtGui.QPen()
        pen.setWidth(2)
        qp.setPen(pen)

        # loop through played notes and paint them (with additional lines if needed)
        for index, note in enumerate(self.played_notes):
            if(note[1] == 0):
                qp.setBrush(QtGui.QColor(0, 0, 0))
            else:
                qp.setBrush(QtGui.QColor(0, 0, 0, 0))                
            old_notes_height = self.noteLineConnection[note[0]]
            # draws the tone
            qp.drawEllipse(self.offset + index * 40, old_notes_height, 20, 15)
            # notes 263, 123 and 143 are the ones with additional line
            if(old_notes_height == 263 or old_notes_height <= 143):
                self.add_line_to_note(old_notes_height, qp, index)
            
            if(not note[1] == 2):
                self.add_stem_to_note(old_notes_height, qp, index)

        # draw current note
        height = self.noteLineConnection[self.counter]
        # notes 263, 123 and 143 are the ones with additional line
        if(height == 263 or height <= 143):
            self.add_line_to_note(height, qp, len(self.played_notes))
        if(not self.type_counter == 2):
            self.add_stem_to_note(height, qp, len(self.played_notes))

        # fill current note grey if quarter
        if(self.type_counter == 0):
            qp.setBrush(QtGui.QColor(70, 70, 70))
        else:
            qp.setBrush(QtGui.QColor(70, 70, 70, 30))
        # draws the tone
        qp.drawEllipse(self.offset + len(self.played_notes) * 40, height, 20, 15)
        # ends painting
        qp.end()

    def add_stem_to_note(self, heightOfTone, qp, index):
        if heightOfTone >= 213:
            x = self.offset + 20 + index * 40
            y1 = heightOfTone + 7
            y2 = heightOfTone - 60
        else:
            x = self.offset + index * 40
            y1 = heightOfTone + 7
            y2 = heightOfTone + 60
            
        line = QtCore.QLine(x, y1, x, y2)
        qp.drawLine(line)
    
        
    # adds the line to a note
    def add_line_to_note(self, heightOfTone, qp, index):
        x1 = self.offset - 5 + index * 40
        x2 = self.offset + 25 + index * 40
        
        if(heightOfTone == 123):
            line1 = QtCore.QLine(x1, heightOfTone + 27, x2, heightOfTone + 27)
            qp.drawLine(line1)
        elif(heightOfTone == 133):
            heightOfTone = 143
            
        line2 = QtCore.QLine(x1, heightOfTone + 7, x2, heightOfTone + 7)
        qp.drawLine(line2)
    

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
        if(index > 11):
            self.offset = 95 - (index - 11) * 40
        else:
            self.offset = 95

    # undo last note if there is one
    def undo(self):
        if( not len(self.played_notes) == 0):
            # funktioniert das schon so?
            self.redoable_notes.append(self.played_notes[-1])
            self.played_notes = self.played_notes[:-1]
            self.update()

    # redo last undone note if there was one
    def redo(self):
        if(not len(self.redoable_notes) == 0):
            # funktioniert das schon so?
            self.played_notes.append(self.redoable_notes[-1])
            self.redoable_notes = self.redoable_notes[:-1]
            self.update()

    # play the full melody and shift, so current note is seen
    def play_melody(self):
        for index, note in enumerate(self.played_notes):
            self.shift_notes_play(index)
            # self.play_tone(self.notelist[note[0]], self.typelist[note[1]] * 2)
            self.update()
            time.sleep(0.1)

    # add a tone to the melody and redraw
    def add_tone_to_melody(self):
        self.played_notes.append((self.counter, self.type_counter))
        self.update()

    # http://milkandtang.com/blog/2013/02/16/making-noise-in-python/
    def prepareSound(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32,
                        channels=1, rate=44100, output=1, stream_callback=self.play_tone_callback)
        self.stream.start_stream()
        while(self.stream.is_active()):
            time.sleep(10.0)            
            self.stream.stop_stream()
        print("stopped")
        self.stream.close()
    
    def play_tone_callback(self, in_data, frame_count, time_info, status):
        chunk = self.play_tone2()
        data = chunk.astype(numpy.float32).tostring()
        return (data, pyaudio.paContinue)
        
    def play_tone2(self):
        return self.sine(self.myfrequency, self.mytype * 2, 44100) * self.volume

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
        chunk = numpy.concatenate(chunks) * self.volume
        self.stream.start_stream()
        self.stream.write(chunk.astype(numpy.float32).tostring())
        self.stream.stop_stream()

    def up_volume(self):
        if self.volume < self.max_volume - self.volume_step:
            self.volume += self.volume_step
            self.ui.label_volume_value.setText(str(round(self.volume * 100 / 2, 2)))
        
    def down_volume(self):
        if self.volume > 0 + self.volume_step:
            self.volume -= self.volume_step
            self.ui.label_volume_value.setText(str(round(self.volume * 100 / 2, 2)))

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
