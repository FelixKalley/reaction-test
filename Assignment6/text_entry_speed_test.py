#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import uic, QtWidgets, QtCore, QtGui


class TextInput(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        
        # contains data given from file
        self.dataArray = []
        self.checkInput()
        
        self.sentences = ("Satz Nummer eins.",
                          "Satz Nummer zwei.",
                          "Satz Nummer drei.",
                          "Satz Nummer vier.")
        
        self.initUI()
        self.round = 0
        self.nextRound()

    # checks for given input
    def checkInput(self):
        # if file is given
        if len(sys.argv[1:]):
            # tries if file can be opened
            try:
                with open(sys.argv[1], 'Ur') as input_data:
                    # iterates over every line in given file
                    for line in input_data:
                        # puts content from line into input_data
                        self.dataArray.append(line)
            # if file cannot be opened
            except EnvironmentError as err_open:
                # prints error message
                print('Error accessing file %s: %s' % (sys.argv[1], err_open), file=sys.stderr)
                # exits programm
                sys.exit(err_open.errno)
        # if no file is given
        else:
            print("Please provide one .txt-file as argument")
            sys.exit()
            
        self.convertInput()

    # converts the data input
    def convertInput(self):
        # tries splitting strings
        try:
            # splits strings and keeps relevant data
            self.subjectNum = self.dataArray[0].split(":")[1].strip()
            temporaryOrder = self.dataArray[1].split(":")[1]
            self.testOrder = temporaryOrder.strip().split(", ")
        # if errors happen while splitting
        except:
            # prints data format as message
            print("The given data does not conform to the standard. \n"
                  "Please format data like this: \n"
                  "PARTICIPANT: 1 \n"
                  "SENTENCE-NR: 3, 2, 1, 4 \n")
            # exits
            sys.exit()

    # receives key presses from keyboard
    def keyPressEvent(self, event):
        print("event")
        if type(event) == QtGui.QKeyEvent:
            key = event.key()
            if  key == QtCore.Qt.Key_Return:
                self.nextRound()
    
    def initUI(self):
        self.ui = uic.loadUi("text_entry_speed_test.ui", self)
        self.show()
        self.ui.EnterTextEdit.textChanged.connect(self.editedText)

    def editedText(self):
        print("test")

    def nextRound(self):
        # clear field
        # show next text
        self.ui.GivenTextLabel.setText(self.sentences[self.round])
        self.ui.EnterTextEdit.setText("")
        self.round += 1
        print("next round")

def main():
    app = QtWidgets.QApplication(sys.argv)
    txtInput = TextInput()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
