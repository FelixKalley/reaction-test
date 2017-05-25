#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
import time
import datetime
import random
import csv
import urllib.request
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication


class ReactionTest(QtWidgets.QWidget):
    # experiment with some tests ...

    def __init__(self):
        super().__init__()
        # counts the screen number
        self.counter = 0
        # contains data given from file
        self.dataArray = []
        # the number of the actual subject
        self.subjectNum = 0
        # order of screens in form of final strings
        self.testOrder = []
        # time between signals change:
        self.timeBetween = 0
        # bool if test has started
        self.testStarted = False
        # icon for arrow up
        self.upIcon = '\u25b2'
        self.downIcon = '\u25bc'
        # numbers for screen order
        self.screenAD = 0
        self.screenAN = 0
        self.screenPD = 0
        self.screenPN = 0
        # time for countdown in seconds
        self.countdownTime = 5
        # number of repetitions
        self.repetitionsNum = 10
        # list of words for attentive tasks
        self.attentiveList = {"bird": "1", "airplane": "1", "fly": "1",
                              "helicopter": "1", "spaceship": "1", "bee": "1",
                              "superman": "1", "U.F.O.": "1", "dragon": "1",
                              "butterfly": "1", "boat": "0", "car": "0",
                              "pizza": "0", "fish": "0", "dog": "0",
                              "cat": "0", "you": "0", "guitar": "0",
                              "table": "0", "bus": "0"}
        # list of words for pre attentive tasks
        self.preattentiveList = {"\u25b2": "1", "\u25bc": "0"}
        # count for repetitions per task
        self.repetitionCount = 0

        self.stimulus = ""
        self.isAttentive = ""
        self.isDistraction = False
        self.rTimeStart = 0
        self.pressedKey = ""
        self.correctKey = ""
        self.stimulusCompleted = True
        self.testTimestamp = str(datetime.datetime.now()).split('.')[0]

        # variable for attentive or preattentive text
        self.text = ""
        # description text
        self.descriptionText = "This is a test of reaction speed. \n" \
                               "\n" \
                               "You will only use two buttons in this test: \n" \
                               "Arrow Key Up and Arrow Key Down. \n" \
                               "\n" \
                               "You will see green arrows on the screen. \n" \
                               "If a shown arrow points upward, press Arrow Key Up. \n" \
                               "Otherwise press Arrow Key Down. \n" \
                               "\n" \
                               "You will see green words on the screen. \n" \
                               "The words describe things that do usually fly, or don't. \n" \
                               "If a thing usually flies, press Arrow Key Up. \n" \
                               "Otherwise press Arrow Key Down. \n" \
                               "\n" \
                               "You will see distractions. Try to ignore them. \n" \
                               "\n" \
                               "Hover your right middle finger over the arrow keys. \n" \
                               "To begin press the space bar with your left hand. \n" \
                               "After that the test starts immediately. Be quick!"
        # variable for distraction arrows
        self.distractionArrows = ""
        # list of different arrow patterns
        self.distractionArrowsList = {"▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲",

                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼",

                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n"
                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n"
                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n"
                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n"
                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n"
                                      "▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ \n"
                                      "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲",

                                      "▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲ \n"
                                      "▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼ \n"
                                      "▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲ \n"
                                      "▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼ \n"
                                      "▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲ \n"
                                      "▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼ \n"
                                      "▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲ \n"
                                      "▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼ \n"
                                      "▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲ \n"
                                      "▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼ \n"
                                      "▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲ \n"
                                      "▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼",

                                      "▲▼▲▼▲▲▼▼▼▲▼▼▲▼▲▼▼▼▼▲▲▼▼▲ \n"
                                      "▲▲▲▼▲▼▲▼▼▲▼▼▼▼▼▼▲▲▲▼▼▼▼▲ \n"
                                      "▼▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▼▼▼▼▼▲▲▼ \n"
                                      "▼▼▼▼▼▼▲▼▼▼▼▲▼▼▼▲▼▲▼▲▼▲▼▼ \n"
                                      "▼▼▼▲▼▼▲▼▼▼▲▼▼▲▼▼▼▲▼▼▲▼▼▼ \n"
                                      "▼▲▼▼▲▼▲▲▼▲▼▲▼▼▲▼▼▲▼▲▼▲▼▲ \n"
                                      "▼▲▼▲▼▼▼▲▼▼▲▲▼▲▼▼▼▲▼▼▲▼▲▼ \n"
                                      "▲▲▲▼▲▼▼▼▲▼▼▼▲▲▼▼▲▼▼▼▼▼▲▼ \n"
                                      "▼▲▲▼▼▼▼▼▲▲▲▲▲▲▲▲▲▼▼▼▼▲▼▼ \n"
                                      "▼▼▼▲▲▲▼▼▼▲▲▼▼▲▼▼▲▼▼▼▲▼▼▲ \n"
                                      "▼▼▲▼▲▼▼▼▼▼▲▼▼▼▲▲▲▼▲▼▼▲▼▲ \n"
                                      "▼▲▼▼▲▼▲▼▲▼▼▲▼▼▲▼▲▼▼▼▲▼▲▲"}
        # function to initialize the ui
        self.initUI()
        # function to check if data input is given
        self.checkInput()
        # function to convert the given data input
        self.convertInput()
        # function to convert the string containing the order of screens as needed
        self.convertOrder()

    # inits ui
    def initUI(self):
        # sets size of window
        self.setGeometry(0, 0, 793, 603)
        # sets window title
        self.setWindowTitle('Reaction Test')
        # widget should accept focus by click and tab key
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        #
        self.center()
        # shows window
        self.show()

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

    # converts the data input
    def convertInput(self):
        # tries splitting strings
        try:
            # splits strings and keeps relevant data
            self.subjectNum = self.dataArray[0].split(":")[1].strip()
            temporaryOrder = self.dataArray[1].split(":")[1]
            self.testOrder = temporaryOrder.strip().split(", ")
            self.timeBetween = int(self.dataArray[2].split(": ")[1].strip())
        # if errors happen while splitting
        except:
            # prints data format as message
            print("The given data does not conform to the standard. \n"
                  "Please format data like this: \n"
                  "PARTICIPANT: 1 \n"
                  "TRIALS: AD, AN, PD, PN, AD, AN, PD, PN, ... \n"
                  "TIME_BETWEEN_SIGNALS_MS: 1000")
            # exits
            sys.exit()

    # converts the given order of screens into numbers
    def convertOrder(self):
        # gets number from index of testOrder arry
        self.screenAD = self.testOrder.index("AD")
        self.screenAN = self.testOrder.index("AN")
        self.screenPD = self.testOrder.index("PD")
        self.screenPN = self.testOrder.index("PN")

    # handles keyPress Events
    def keyPressEvent(self, ev):
        # if space button is pressed
            if not self.testStarted and ev.key() == QtCore.Qt.Key_Space:
                self.stimulusCompleted = False
                self.testStarted = True
                self.text = ""
                self.distractionArrows = ""
                self.descriptionText = ""
                self.update()
                # function nextScreen is called
                QtCore.QTimer.singleShot((self.timeBetween), lambda: self.nextScreen())
            if self.testStarted and self.stimulusCompleted and ev.key() == QtCore.Qt.Key_Up:
                self.stimulusCompleted = False
                self.writeCSV("up")
                self.text = ""
                self.distractionArrows = ""
                self.update()
                # function nextScreen is called
                QtCore.QTimer.singleShot((self.timeBetween), lambda: self.nextScreen())
            if self.testStarted and self.stimulusCompleted and ev.key() == QtCore.Qt.Key_Down:
                self.stimulusCompleted = False
                self.writeCSV("down")
                self.text = ""
                self.distractionArrows = ""
                self.descriptionText = ""
                self.update()
                # function nextScreen is called
                QtCore.QTimer.singleShot((self.timeBetween), lambda: self.nextScreen())

    # shows the following screen depending on order
    def nextScreen(self):
        if self.testStarted:
            # checks if screen is next in order respectively has same number as counter
            if self.screenAD == self.counter:
                # shows attentive stimulus with distractions
                self.attentive()
                self.addDistractionArrows()
                self.isDistraction = True
                self.rTimeStart = datetime.datetime.now()
            elif self.screenAN == self.counter:
                # shows attentive stimulus without distractions
                self.attentive()
                self.removeDistractionArrows()
                self.isDistraction = False
                self.rTimeStart = datetime.datetime.now()
            elif self.screenPD == self.counter:
                # shows preattentive stimulus with distractions
                self.preAttentive()
                self.addDistractionArrows()
                self.isDistraction = True
                self.rTimeStart = datetime.datetime.now()
            elif self.screenPN == self.counter:
                # shows preattentive stimulus without distractions
                self.preAttentive()
                self.removeDistractionArrows()
                self.isDistraction = False
                self.rTimeStart = datetime.datetime.now()
            else:
                self.lastScreen()

            if self.repetitionCount < self.repetitionsNum:
                self.repetitionCount += 1
            else:
                self.repetitionCount = 0
                # counts up for next screen
                self.counter += 1
        self.stimulusCompleted = True

    # handles preattentive stimulus
    def preAttentive(self):
        self.isAttentive = "pre-attentive"
        # picks random word from pre-attentive words list
        self.text = list(self.preattentiveList)[random.randint(0, len(self.preattentiveList)-1)]
        # save stimulus text for log
        self.stimulus = self.text
        # save correct key for log
        if self.preattentiveList[self.text] == "0":
            self.correctKey = "down"
        elif self.preattentiveList[self.text] == "1":
            self.correctKey = "up"
        self.update()

    # handles attentive stimulus
    def attentive(self):
        self.isAttentive = "attentive"
        # picks random word from attentive words list
        self.text = list(self.attentiveList)[random.randint(0, len(self.attentiveList)-1)]
        # save stimulus text for log
        self.stimulus = self.text
        # save correct key for log
        if self.attentiveList[self.text] == "0":
            self.correctKey = "down"
        elif self.attentiveList[self.text] == "1":
            self.correctKey = "up"
        self.update()

    # handles painting of screens
    def paintEvent(self, event):
        # sets up painter
        qp = QtGui.QPainter()
        qp.begin(self)
        # draws text
        self.drawDescriptionText(event, qp)
        self.drawDistractionArrows(event, qp)
        self.drawText(event, qp)
        qp.end()

    # handles drawing of text
    def drawText(self, event, qp):
        # sets color
        qp.setPen(QtGui.QColor(0, 204, 0))
        # sets font
        qp.setFont(QtGui.QFont('Decorative', 60))
        # draws text
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)

    # handles drawing of distraction text
    def drawDistractionArrows(self, event, qp):
        # sets color
        qp.setPen(QtGui.QColor(100, 100, 100))
        # sets font
        qp.setFont(QtGui.QFont('Decorative', 32))
        # draws text
        qp.drawText(event.rect(), QtCore.Qt.AlignLeft, self.distractionArrows)

    # handles drawing of description text
    def drawDescriptionText(self, event, qp):
        # sets color
        qp.setPen(QtGui.QColor(0, 204, 255))
        # sets font
        qp.setFont(QtGui.QFont('Decorative', 18))
        # draws text
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.descriptionText)

    # adds distractions
    def addDistractionArrows(self):
        self.distractionArrows = list(self.distractionArrowsList)[random.randint(0, 4)]

    # removes distractions
    def removeDistractionArrows(self):
        self.distractionArrows = ""

    # centers window on screen
    # source: http://zetcode.com/gui/pyqt5/firstprograms/
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # screen when experiment finished
    def lastScreen(self):
        self.descriptionText = "Finished!"
        self.update()

    # writes the current trail to the log file
    def writeCSV(self, pressedKey):
        id = self.subjectNum
        if pressedKey == self.correctKey:
            correctKeyPressed = True
        else:
            correctKeyPressed = False
        # calculate the reaction time based on time when stimuli is shown til now
        reactionTime = int((datetime.datetime.now() - self.rTimeStart).total_seconds() * 1000)
        logTimestamp = str(datetime.datetime.now()).split('.')[0]
        # all data for current log row
        csvRow = [id, self.stimulus, self.isAttentive,
                  self.isDistraction, pressedKey, self.correctKey,
                  correctKeyPressed, reactionTime, logTimestamp]
        # name of current log file with timestamp to not override old ones
        logName = "reaction_time_results_" + str(self.subjectNum) + "_" + self.testTimestamp + ".csv"
        # write log row to file
        with open(logName, 'a+') as logfile:
            csvWriter = csv.writer(logfile)
            # if is first log row, first write header row
            if(self.repetitionCount == 1 and self.counter == 0):
                # csv header row
                csvHeader = ["participant ID", "stimulus", "mental complexity",
                             "distraction", "pressed key", "correct key",
                             "correct key pressed", "reaction time in ms",
                             "timestamp"]
                csvWriter.writerow(csvHeader)
            csvWriter.writerow(csvRow)


# function
def main():
    app = QtWidgets.QApplication(sys.argv)
    # variable is never used, class automatically registers itself for Qt main loop:
    space = ReactionTest()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
