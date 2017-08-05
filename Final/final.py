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
import csv
import tkinter
import tkinter.filedialog
from PyQt5 import uic, QtWidgets, QtCore, QtGui


class MeloWii(QtWidgets.QWidget):
    """MeloWii is an application to generate and play simple melodies and save them for later use as wave.
    Lena Felix hier muss noch text rein inklusive anleitung etc.
    """
    def __init__(self):
        super().__init__()

        # counter variable for note position
        # initial value is actually not that relevant
        # 6 is only chosen to place the note image in the middle of the line before the wiimote connects.
        self.counter = 6

        # counter variable for note type (=length)
        self.type_counter = 0

        # list of frequencies of specific notes
        # from source: http://www.sengpielaudio.com/Rechner-notennamen.htm
        # self.notelist = [261.626, 277.183, 293.665, 311.127, 329.628, 349.228, 369.994, 391.995, 415.305, 440.000,
        #                  466.164, 493.883, 523.251, 554.365, 587.330, 622.254, 659.255, 698.456, 739.989, 783.991,
        #                  830.609, 880.000, 932.328, 987.767, 1046.500]
        # self.notelist below is the same list as above but this time without half-tones (= # or b)
        self.notelist = [261.626, 293.665, 329.628, 349.228, 391.995, 440.000,
                         493.883, 523.251, 587.330, 659.255, 698.456, 783.991,
                         880.000, 987.767, 1046.500]

        # list of note types (= length)
        self.typelist = [0.25, 0.5, 1.0]

        # list of geometrical heights of notes (in application)
        self.noteLineConnection = [263, 253, 243, 233, 223, 213,
                                   203, 193, 183, 173, 163, 153,
                                   143, 133, 123]

        # current frequency
        self.myfrequency = self.notelist[self.counter]

        # list of already played notes
        self.played_notes = []

        # list with redoable notes, cleared if new note is entered
        self.redoable_notes = []

        # defines where to start drawing the notes
        self.offset = 95

        # adresses of used wiimotes
        self.standard_wiimotes = ["00:1F:C5:3F:AA:F1", "18:2a:7b:f3:f1:68"]

        # starting volume
        self.volume = 1

        # maximum volume
        self.max_volume = 2

        # size of volume increment/decrement
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

        # inits ui elements
        self.initUI()

    # inits the user interface elements
    # loads ui file
    # adds listeners to buttons and connects associated functions
    # adds items from standard_wiimotes to combobox
    def initUI(self):
        # load ui file "final.ui"
        self.ui = uic.loadUi("final.ui", self)
        self.show()
        # combobox for wiimote address
        self.ui.wiiMoteAddresses.addItems(self.standard_wiimotes)
        # listener to connect button
        self.ui.connectWiiMoteButton.clicked.connect(self.connect_wiimote)
        # listener to recalibrate button
        self.ui.recalibrateWiiMoteButton.clicked.connect(self.recalibrate_wiimote)

    # connects to WiiMote with given MAC-address
    def connect_wiimote(self):
        # name of wiimote
        name = None
        # address of wiimote
        addr = self.ui.wiiMoteAddresses.currentText()
        # prints connection message
        print(("Connecting to %s (%s)" % (name, addr)))
        # trys to connect to specified wiimote
        try:
            # connects
            self.wm = wiimote.connect(addr, name)
            # sets warning label to empty
            self.ui.label_cannot_connect.setText("")
            # calls prepareSound function to setup stream
            self.prepareSound()
            # registers all wiimote buttons via callbacks
            self.registerButtons()
            # starts tracking changes in wiimote axis movement
            self.trackAxes()
            # disables connect button
            self.connectWiiMoteButton.setEnabled(False)
        # otherwise shows warning
        except:
            # prints warning message to console
            print("Cannot connect to WiiMote!")
            # shows warning message in application
            self.ui.label_cannot_connect.setText("Cannot connect to WiiMote!")

    # registers callbacks for button clicks
    def registerButtons(self):
        self.wm.buttons.register_callback(self.button_changed)

    # recalibrates wiimote
    def recalibrate_wiimote(self):
        # resets to initial state of set start values from axes
        self.start_axpos_set = False

    # tracks changes in axes via callbacks
    def trackAxes(self):
        self.wm.accelerometer.register_callback(self.axis_changed)

    # changes position or type of notes depending of changes in wiimote axes
    def axis_changed(self, state):
        # at the start of the programm after connecting the wiimote
        if not self.start_axpos_set:
            # sets starting values
            self.start_xyz = [state]
            # generates ranges of axis values for different frequencies
            self.generate_range_values(self.start_xyz)
            # sets state of axis positions to set
            self.start_axpos_set = True
        # any time else
        else:
            # runs through notelist
            for x in range(0, len(self.notelist)):
                # checks if current y-axis value is in range of a note
                if self.note_ranges[x][0] <= state[1] <= self.note_ranges[x][1]:
                    # sets frequency to value of corresponding note
                    self.myfrequency = self.notelist[len(self.notelist)-1-x]
                    # sets counter to corresponding value
                    self.counter = len(self.notelist)-1-x
                    # updates ui
                    self.update()
            # runs through typelist
            for x in range(0, len(self.typelist)):
                # checks if current x-axis value is in range of a type
                if self.type_ranges[x][0] <= state[0] <= self.type_ranges[x][1]:
                    # sets type to value of corresponding note type
                    mytype = self.typelist[x]
                    # sets type_counter to corresponding value
                    self.type_counter = x
                    # updates ui
                    self.update()

    # generates range values for notes
    # the idea is to check current axis value and see if it is in a range of a note(type)
    # range values are generated automatically depending on size of initial notelist
    # the method can easily be adapted to different sizes
    def generate_range_values(self, start_xyz):
        # first range values for note frequencies are generated
        # checks if number of notes in list is even or uneven
        # even
        if len(self.notelist) % 2 == 0:
            # this could be adapted if an even number of notes or other notes would be used
            print("Please rework the method \"generate_range_values\", if you wanna work with more notes.")
        # uneven
        else:
            # distance value between the highest and the lowest value of two different adjacent tuples
            # 4 is chosen depending on wiimote values, UI size and number of notes.
            tuple_distance = 4
            # range value between the low and high end value of one single tuple
            # 8 is chosen depending on wiimote values, UI size and number of notes.
            tuple_range = 8
            # sets middle value according to wiimote starting values
            middle_value = start_xyz[0][1]
            # calculates first tuple from middle value and tuple range
            middle_tuple = (middle_value-tuple_range/2, middle_value+tuple_range/2)
            # starting from middle tuple, calculates ranges values for notes with ranges below
            # therefore iterates over lower ("left") half of notelist
            for x in range(0, int((len(self.notelist)-1)/2)):
                # calculates next tuple
                next_tuple = (middle_tuple[0]-x*(tuple_range+tuple_distance),
                              middle_tuple[1]-x*(tuple_range+tuple_distance))
                # adds next_tuple in note_ranges
                self.note_ranges.insert(0, next_tuple)
            # starting from middle tuple, calculates ranges values for notes with ranges higher
            # therefore iterates over higher ("right") half of notelist
            for x in range(int((len(self.notelist)-1)/2), len(self.notelist)):
                # calculates next_tuple
                next_tuple = (middle_tuple[0]+(x+1-int((len(self.notelist)-1)/2))*(tuple_range+tuple_distance),
                              middle_tuple[1]+(x+1-int((len(self.notelist)-1)/2))*(tuple_range+tuple_distance))
                # adds next_tuple in note ranges
                self.note_ranges.insert(x, next_tuple)

        # second range values for note types are generated
        # checks if number of note types in type list is even or uneven
        # even
        if len(self.typelist) % 2 == 0:
            # this could be adapted if an even number of notes or other notes would be used
            print("Please rework the method \"generate_range_values\", if you wanna work with more types of notes.")
        # uneven
        else:
            # distance value between the highest and the lowest value of two different adjacent tuples
            # 10 is chosen depending on wiimote values and number of types
            tuple_distance = 10
            # range value between the low and high end value of one single tuple
            # 60 is chosen depending on wiimote values and number of types
            tuple_range = 60
            # sets middle value according to wiimote starting values
            middle_value = start_xyz[0][0]
            # calculates first tuple from middle value and tuple range
            middle_tuple = (middle_value-tuple_range/2, middle_value+tuple_range/2)
        # starting from middle tuple, calculates ranges values for note types with ranges below
        # therefore iterates over lower ("left") half of typelist
        for x in range(0, int((len(self.typelist)-1))):
            # calculates next_tuple
            next_tuple = (middle_tuple[0]-x*(tuple_range+tuple_distance),
                          middle_tuple[1]-x*(tuple_range+tuple_distance))
            # adds next_tuple in note_ranges
            self.type_ranges.insert(0, next_tuple)
        # starting from middle tuple, calculates ranges values for note types with ranges higher
            # therefore iterates over higher ("right") half of typelist
        for x in range(int((len(self.typelist)-1)), len(self.typelist)):
            # calculates next_tuple
            next_tuple = (middle_tuple[0]+(x/2)*(tuple_range+tuple_distance),
                          middle_tuple[1]+(x/2)*(tuple_range+tuple_distance))
            # adds next_tuple in note_ranges
            self.type_ranges.insert(x, next_tuple)

    # listens to the wiimote buttons and performs an action if buttons are clicked
    def button_changed(self, changed):
        # does nothing without input
        if not changed:
            pass
        # with input
        else:
            # A-button to choose a note
            if(("A", True) in changed):
                # LENA was tut das hier?
                self.redoable_notes = []
                # plays selected note
                self.play_note(self.myfrequency, self.typelist[self.type_counter] * 4)
                # adds note to melody
                self.add_note_to_melody()
                # shifts notes record
                self.shift_notes_record()
            # D-Pad (all directions) to play melody
            elif (("Down", True) in changed):
                # plays melody
                self.play_melody()
            elif (("Up", True) in changed):
                self.play_melody()
            elif (("Left", True) in changed):
                self.play_melody()
            elif (("Right", True) in changed):
                self.play_melody()
            # B-button to undo last note
            elif(("B", True) in changed):
                # deletes last note
                self.undo()
                # shifts notes record
                self.shift_notes_record()
            # 1-Button to redo last undone note
            elif(("One", True) in changed):
                # restores last note
                self.redo()
                # shifts notes record
                self.shift_notes_record()
            # 2-Button to save melody as wave file
            elif(("Two", True) in changed):
                # saves file
                self.save_file()
            # "+"-button to increase volume
            elif(("Plus", True) in changed):
                # increases volume
                self.up_volume()
            # "-"-button to decrease volume
            elif(("Minus", True) in changed):
                # decreases volume
                self.down_volume()
            # Home-button to close application
            elif (("Home", True) in changed):
                # closes stream
                self.stream.close()
                # kills stream
                self.p.terminate()
                # closes application
                self.close()

    # Lena einmal drüberlesen über die kommentare in der funktion bitte
    # saves file to location of choice in wave format
    def save_file(self):
        # inits tkinter for gui elements
        root = tkinter.Tk()
        # creates window for file saving
        name = tkinter.filedialog.asksaveasfilename(defaultextension=".wav")
        # destroys the extra window opened by tkinter
        root.destroy()

        # creates/opens wave file
        f = wave.open(name, 'w')
        # Lena was tut das hier?
        melody_length = 0
        # sets parameters for wave file
        f.setparams((1, 4, 44100, 0, 'NONE', 'not compressed'))
        # iterates over played notes
        for index, note in enumerate(self.played_notes):
            # appends notes to chunks
            chunks = []
            chunks.append(self.sine(self.notelist[note[0]], self.typelist[note[1]] * 2, 30000))
            # concatenates chunks
            chunk = numpy.concatenate(chunks) * self.volume
            # writes chunk in wave file
            f.writeframesraw(chunk.astype(numpy.float32))
        # closes wave file
        f.close()

    # handles paint events
    def paintEvent(self, event):
        # initializes QPainter
        qp = QtGui.QPainter()
        # starts painting
        qp.begin(self)
        # fill following notes black
        # sets width of lines to 2
        pen = QtGui.QPen()
        pen.setWidth(2)
        qp.setPen(pen)
        # loops through played notes and paint them (with additional lines if needed)
        for index, note in enumerate(self.played_notes):
            # Lena was passiert hier genau?
            if(note[1] == 0):
                qp.setBrush(QtGui.QColor(0, 0, 0))
            else:
                qp.setBrush(QtGui.QColor(0, 0, 0, 0))
            old_notes_height = self.noteLineConnection[note[0]]
            # draws the note
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
        # draws the note
        qp.drawEllipse(self.offset + len(self.played_notes) * 40, height, 20, 15)
        # ends painting
        qp.end()

    # adds stem (= vertical line) to note
    def add_stem_to_note(self, heightOfnote, qp, index):
        # checks height of note
        # if high
        if heightOfnote >= 213:
            # positions stem on the lower left side of note
            x = self.offset + 20 + index * 40
            y1 = heightOfnote + 7
            y2 = heightOfnote - 60
        # if low
        else:
            # positions stem on the upper right side of note
            x = self.offset + index * 40
            y1 = heightOfnote + 7
            y2 = heightOfnote + 60
        # draws line
        line = QtCore.QLine(x, y1, x, y2)
        qp.drawLine(line)

    # adds the horizontal line to a note
    def add_line_to_note(self, heightOfnote, qp, index):
        # x positions of line
        x1 = self.offset - 5 + index * 40
        x2 = self.offset + 25 + index * 40
        # checks height of note
        # if below
        if(heightOfnote == 123):
            # draws line
            line1 = QtCore.QLine(x1, heightOfnote + 27, x2, heightOfnote + 27)
            qp.drawLine(line1)
        # if above
        elif(heightOfnote == 133):
            heightOfnote = 143
        # draws line
        line2 = QtCore.QLine(x1, heightOfnote + 7, x2, heightOfnote + 7)
        qp.drawLine(line2)

    # shifts the notes, so the last note can be seen
    def shift_notes_record(self):
        # checks for number of played notes
        # if over 12
        if(len(self.played_notes) > 12):
            # shifts the notes
            self.offset = 95 - (len(self.played_notes) - 12) * 40
        # otherwise
        else:
            self.offset = 95

    # shifts the notes while playing, so the current note can be seen
    def shift_notes_play(self, index):
        # checks for index
        # if above 11
        if(index > 11):
            # shifts
            self.offset = 95 - (index - 11) * 40
        # otherwise
        else:
            self.offset = 95

    # undo last note if there is one
    def undo(self):
        # checks if at least one note has been placed
        if not len(self.played_notes) == 0:
            # Lena der kommentar in der nächsten Zeile ist noch von dir, ich nehme an das ist hinfällig?
            # funktioniert das schon so?
            # adds note to redoable_notes
            self.redoable_notes.append(self.played_notes[-1])
            # removes note from played_notes
            self.played_notes = self.played_notes[:-1]
            # updates ui
            self.update()

    # redo last undone note if there was one
    def redo(self):
        # checks if at least one note can be undone
        if(not len(self.redoable_notes) == 0):
            # Lena nochmal :D
            # funktioniert das schon so?
            # adds note to played_notes
            self.played_notes.append(self.redoable_notes[-1])
            # deletes note from redoable_notes
            self.redoable_notes = self.redoable_notes[:-1]
            # updates ui
            self.update()

    # plays the full melody and shifts, so current note is seen
    def play_melody(self):
        # iterates over all notes in played_notes
        for index, note in enumerate(self.played_notes):
            # shifts if needed
            self.shift_notes_play(index)
            # plays note
            self.play_note(self.notelist[note[0]], self.typelist[note[1]] * 4)
            # updates ui
            self.update()
            time.sleep(0.2)

    # add a note to the melody and redraw
    def add_note_to_melody(self):
        # adds note to played_notes
        self.played_notes.append((self.counter, self.type_counter))
        # updates ui
        self.update()

    # prepares pyaudio stream for making sounds
    # source from http://milkandtang.com/blog/2013/02/16/making-noise-in-python/
    def prepareSound(self):
        # inits pyaudio
        self.p = pyaudio.PyAudio()
        # opens stream
        # a rate of 30000 is chosen because underrun is more or less eliminated here
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1, rate=30000, output=1)

    # creates sine curve from frequency, length and rate
    # source fromhttp://milkandtang.com/blog/2013/02/16/making-noise-in-python/
    def sine(self, frequency, length, rate):
        # calculates new length depending on given length and rate
        length = int(length * rate)
        # calculates factor from frequency, rate and pi
        factor = float(frequency) * (math.pi * 2) / rate
        # creates sine
        sine = numpy.sin(numpy.arange(length) * factor)
        # checks if sin curve ends below or above x-axis
        # if below
        if sine[len(sine) - 1] < 0:
            lastval = -1
        # if above
        else:
            lastval = 1
        # sets index for cutting sine curve
        cutindex = 0
        # reverse iterates over all vals in sin curve and cuts when curve is below x axis and near zero
        for index, val in enumerate(reversed(sine)):
            # Lena evtl hier nochmal drüber kommentieren
            if val < 0 and lastval > 0:
                print(val, lastval, index)
                cutindex = index
                break
            lastval = val

        sine = sine[:-cutindex]
        return sine

    # plays a note from a sine
    # source from: http://milkandtang.com/blog/2013/02/16/making-noise-in-python/
    # length in seconds
    # lower frequency = deeper note
    # standard rate is 44.1kHz
    def play_note(self, frequency, length=0.5, rate=44100):
        # creates chunks array
        chunks = []
        # appends sine curve to chunks
        chunks.append(self.sine(frequency, length, rate))
        # concatenates chunks and factors in volume
        chunk = numpy.concatenate(chunks) * self.volume
        # writes data to stream
        self.stream.write(chunk.astype(numpy.float32))

    # increases volume
    def up_volume(self):
        # checks if not maximum volume
        if self.volume < self.max_volume - self.volume_step:
            # increases by one step
            self.volume += self.volume_step
            # updates volume text label
            self.ui.label_volume_value.setText(str(round(self.volume * 100 / 2, 2)))

    # decreases volume
    def down_volume(self):
        # checks if not minimum
        if self.volume > 0 + self.volume_step:
            # decreases volume by one step
            self.volume -= self.volume_step
            # updates volume text label
            self.ui.label_volume_value.setText(str(round(self.volume * 100 / 2, 2)))


# main
def main():
    # initializes Qapplication
    app = QtWidgets.QApplication(sys.argv)
    # initializes MeloWii
    meloWii = MeloWii()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
