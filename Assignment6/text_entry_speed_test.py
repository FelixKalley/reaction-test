#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
This gives a measure in characters per second (cps). To convert this to words
per minute (wpm) the standard typists' definition of a word as five characters
(regardless of whether the characters are letters, punctuation, or spaces)
is employed (Gentner, Grudin, Larochelle, Norman, & Rumelhart, 1983).
Therefore, words per minute is obtained by multiplying characters per second by
60 (seconds per minute) and dividing by 5 (characters per word). (MacKenzie I.,
Soukoreff R., 2002)
char = 1 char (cps)
word = 5 chars (wpm)
sentence = click return (cps, wpm)
'''

import sys
import datetime
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
        
        self.sentenceStarted = False
        self.charStartTime = 0
        self.wordStartTime = 0
        self.sentenceStartTime = 0
        self.experimentStartTime = 0
        
        self.inputCount = 0
        self.round = 0
        self.initUI()
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
            
            print(self.testOrder)
        # if errors happen while splitting
        except:
            # prints data format as message
            print("The given data does not conform to the standard. \n"
                  "Please format data like this: \n"
                  "PARTICIPANT: 1 \n"
                  "SENTENCE-NR: 3, 2, 1, 4 \n")
            # exits
            sys.exit()
    
    def initUI(self):
        self.ui = uic.loadUi("text_entry_speed_test.ui", self)
        self.show()
        self.ui.EnterTextEdit.textEdited.connect(self.editedText)
        self.ui.EnterTextEdit.returnPressed.connect(self.nextRound)

    def editedText(self):
        if(not self.sentenceStarted and self.inputCount == 0):
            self.sentenceStarted = True
            self.startExperimentTimer()

        self.inputCount += 1
        self.charLog()
        self.stopCharTimer()
        if(self.inputCount % 5 == 0):
            self.wordLog()
            self.stopWordTimer()


    def nextRound(self):
        self.wordLog()
        if(self.sentenceStarted):    
            self.stopSentenceTimer()
        if(self.round < 4):
            # clear field
            # show next text
            self.ui.GivenTextLabel.setText(self.sentences[int(self.testOrder[self.round]) - 1])
            self.ui.EnterTextEdit.setText("")
            self.round += 1
            #print("next round")
        else:
            self.ui.GivenTextLabel.setText("")
            self.ui.EnterTextEdit.setText("")
            self.stopExperimentTimer()
            #print("end")
    
    def startExperimentTimer(self):
        self.experimentStartTime = datetime.datetime.now()
        self.startCharTimer()
        self.startWordTimer()
        self.startSentenceTimer()
    
    def startCharTimer(self):
        self.charStartTime = datetime.datetime.now()

    def startWordTimer(self):
        self.wordStartTime = datetime.datetime.now()

    def startSentenceTimer(self):
        self.sentenceStartTime = datetime.datetime.now()
    
    
    def stopExperimentTimer(self):
        stopTime = datetime.datetime.now()
        diff = stopTime - self.experimentStartTime
        print("experiment", diff.total_seconds())
    
    def stopCharTimer(self):
        stopTime = datetime.datetime.now()
        diff = stopTime - self.charStartTime
        print("char", diff.total_seconds())
        self.startCharTimer()

    def stopWordTimer(self):
        stopTime = datetime.datetime.now()
        diff = stopTime - self.wordStartTime
        print("word", diff.total_seconds())
        self.startWordTimer()

    def stopSentenceTimer(self):
        stopTime = datetime.datetime.now()
        diff = stopTime - self.sentenceStartTime
        print("sentence", diff.total_seconds())
        self.startSentenceTimer()

    def charLog(self):
        #print(self.inputCount)
        pass
    
    def wordLog(self):
        #print("word")
        pass
    
    def sentenceLog(self):
        #print("sentence")
        pass

def main():
    app = QtWidgets.QApplication(sys.argv)
    txtInput = TextInput()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
