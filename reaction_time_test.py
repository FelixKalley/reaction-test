#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
import time
import random
import urllib.request
from PyQt5 import QtGui, QtWidgets, QtCore


class ReactionTest(QtWidgets.QWidget):
    # experiment with some tests ...

    def __init__(self):
        super().__init__()
        # counts the screen number
        self.counter=0
        # contains data given from file
        self.dataArray=[]
        # the number of the actual subject
        self.subjectNum=0
        # order of screens in form of unedited strings
        self.temporaryOrder=[]
        # order of screens in form of final strings
        self.testOrder=[]
        # time between signals change:
        self.timeBetween=0
        # bool if test has started
        self.testStarted = False
        # icon for arrow up
        self.upIcon = '\u25b2'
        # numbers for screen order
        self.screenAD = 0
        self.screenAN = 0
        self.screenPD = 0
        self.screenPN = 0
        # time for countdown in seconds
        self.countdownTime = 5
        # list of words for attentive tasks
        self.attentiveList = {"bird": "1", "airplane": "1", "fly": "1", "cloud": "1", "bee": "1", "boat": "0", "car": "0","pizza": "0", "fish": "0", "bus": "0"}
        # list of words for pre attentive tasks
        self.preattentiveList = {"\u25b2": "1", "\u25bc": "0"}
        # count for repetitions per task
        self.repetitionCount = 0
        
        # function to remove distractions at start
        self.removeDistraction()
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
        # description of the experiment 
        self.distractionText = "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n" \
                               "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n" \
                               "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n" \
                               "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n" \
                               "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n" \
                               "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n" \
                               "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n" \
                               "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n" \
                               "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n" \
                               "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n" \
                               "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ \n" \
        					   "▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲"
        self.text = "▲"
        # sets size of window
        self.setGeometry(0, 0, 793, 603)
        # sets window title
        self.setWindowTitle('Reaction Test')
        # widget should accept focus by click and tab key
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        # shows window
        self.show()
        
        

    '''def countdown(self, n):
        prevT = 0
        while n>0:
            u = time.time()
            if(prevT < u - 1):
                prevT = time.time()
                print(prevT)
                self.text = str(n)
                self.update()
                print(n)
                n = n-1
        if n == 0:
            print("neuer Screen")
'''

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
                #prints error message
                print('Error accessing file %s: %s' % (sys.argv[1], err_open), file=sys.stderr)
                #exits programm
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
            self.temporaryOrder = self.dataArray[1].split(":")[1]
            self.testOrder = self.temporaryOrder.strip().split(", ")
            self.timeBetween = int(self.dataArray[2].split(": ")[1].strip()) / 1000
        # if errors happen while splitting
        except:
            # prints data format as message
            print("The given data does not conform to the standard. \n" \
                   "Please format data like this: \n" \
                   "PARTICIPANT: 1 \n" \
                   "TRIALS: AD, AN, PD, PN, AD, AN, PD, PN, ... \n" \
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
        if ev.key() == QtCore.Qt.Key_Space:
            # function nextScreen is called
            self.testStarted = True
            self.nextScreen()
            time.sleep(int(self.timeBetween))
        if ev.key() == QtCore.Qt.Key_Up or ev.key() == QtCore.Qt.Key_Down:
            # function nextScreen is called
            self.nextScreen()
            time.sleep(int(self.timeBetween))

    # shows the following screen depending on order
    def nextScreen(self):
        if self.testStarted:
            # checks if screen is next in order respectively has same number as counter
            if self.screenAD == self.counter:
                # shows attentive stimulus with distractions
                self.attentive()
                #self.addDistraction()
                self.addDistractionArrows()
            elif self.screenAN == self.counter:
                # shows attentive stimulus without distractions
                self.attentive()
                #self.removeDistraction()
            elif  self.screenPD == self.counter:
                # shows preattentive stimulus with distractions
                self.preAttentive()
                #self.addDistraction()
            elif  self.screenPN == self.counter:
                # shows preattentive stimulus without distractions
                self.preAttentive()
                #self.removeDistraction()
                
            if self.repetitionCount < 10:
                self.repetitionCount += 1
            else:
                self.repetitionCount = 0
                # counts up for next screen
                self.counter += 1
        

    # handles preattentive stimulus
    def preAttentive(self):
        self.text = list(self.preattentiveList)[random.randint(0, len(self.preattentiveList)-1)]
        print("PREATTENTIVE")
        print(self.repetitionCount)
        self.update()

    # handles attentive stimulus
    def attentive(self):        
        self.text = list(self.attentiveList)[random.randint(0, len(self.attentiveList)-1)]
        print("ATTENTIVE")
        print(self.text)
        print(self.repetitionCount)
        self.update()

    # removes distractions
    def removeDistraction(self):
        # sets bool
        self.withDistraction = False
        # reads data for white image from url
        url = 'https://www.ledr.com/colours/white.jpg'
        data = urllib.request.urlopen(url).read()
        # sets up image element
        image = QtGui.QImage()
        image.loadFromData(data)
        # sets white image as background
        self.backgroundImage = QtGui.QPixmap(image)

    # adds distractions
    def addDistraction(self):
        #sets bool
        self.withDistraction = True
        # reads data for distraction image from url
        url = 'https://image.flaticon.com/sprites/new_packs/275104-arrows.png'
        data = urllib.request.urlopen(url).read()
        # sets up image element
        image = QtGui.QImage()
        image.loadFromData(data)
        # sets distractions as background
        self.backgroundImage = QtGui.QPixmap(image)
        
    # handles painting of screens    
    def paintEvent(self, event):
        # sets up painter
        qp = QtGui.QPainter()
        qp.begin(self)
        # draws background with image
        #qp.drawPixmap(0, 0, 1440, 850, self.backgroundImage)
        # draws text
        self.drawDistractionText(event,qp)
        self.drawText(event, qp)
        qp.end()

    # handles drawing of text
    def drawText(self, event, qp):
        # sets color
        qp.setPen(QtGui.QColor(168, 34, 3))
        # sets font
        qp.setFont(QtGui.QFont('Decorative', 40))
        # draws text
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)

    # handles drawing of distraction text
    def drawDistractionText(self, event, qp):
    	#sets color
    	qp.setPen(QtGui.QColor(0, 0, 0))
    	# sets font
    	qp.setFont(QtGui.QFont('Decorative', 32))
    	# draws text
    	qp.drawText(event.rect(), QtCore.Qt.AlignLeft, self.distractionText)


    '''def drawRect(self, event, qp):
        if (self.counter % 2) == 0:
            rect = QtCore.QRect(10, 10, 80, 80)
            qp.setBrush(QtGui.QColor(34, 34, 200))
        else:
            rect = QtCore.QRect(100, 10, 80, 80)
            qp.setBrush(QtGui.QColor(200, 34, 34))
        qp.drawRoundedRect(rect, 10.0, 10.0)
'''


    def addDistractionArrows(self):
        print(self.upIcon)


# main function
def main():
    app = QtWidgets.QApplication(sys.argv)
    # variable is never used, class automatically registers itself for Qt main loop:
    space = ReactionTest()
    sys.exit(app.exec_())



if __name__ == '__main__':
    main()
