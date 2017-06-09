#!/usr/bin/python3

# Contribution: Felix Kalley, Lena Manschewski


""" setup file looks like this:
USER: 1
WIDTHS: 35, 60, 100, 170
DISTANCES: 170, 300, 450, 700
"""

import sys
import random
import math
import itertools
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication

# model that can be reused for task 5.2
# pure python - no camel case?
class PointingExperimentModel(object):
    def __init__(self):
        self.parse_input()
        # amount of circles per round
        self.repetitions = 10
        # amount of circles per click
        self.amountCircles = 5
        self.clicked_targets = 0
        self.create_targets()

    # creates the targets that should be clicked
    def create_targets(self):
        # gives us a list of (distance, width) tuples:
        self.targets = self.repetitions * list(itertools.product(self.distances, self.widths))
        random.shuffle(self.targets)
        
    def current_target(self):
        if len(self.targets) > self.clicked_targets:
            return self.targets[self.clicked_targets]
        else:
            return None
    
    def parse_input(self):
        if len(sys.argv) < 2:
            sys.stderr.write("Usage: %s <setup file>\n" % sys.argv[0])
            sys.exit(1)

        lines = open(sys.argv[1], "r").readlines()
        if lines[0].startswith("USER:"):
            self.user_id = lines[0].split(":")[1].strip()
        else:
            sys.stderr.write("Error: wrong file format.")
            sys.exit(1)
        if lines[1].startswith("WIDTHS:"):
            width_string = lines[1].split(":")[1].strip()
            self.widths = [int(x) for x in width_string.split(",")]
        else:
            sys.stderr.write("Error: wrong file format.")
            sys.exit(1)
        if lines[2].startswith("DISTANCES:"):
            distance_string = lines[2].split(":")[1].strip()
            self.distances = [int(x) for x in distance_string.split(",")]
        else:
            sys.stderr.write("Error: wrong file format.")
            sys.exit(1)

    def register_click(self, target_pos, click_pos):
        print("I REGISTERED A CLICK!")
        print(target_pos)
        print(click_pos)
        dist = math.sqrt((target_pos[0]-click_pos[0]) * (target_pos[0]-click_pos[0]) +
                         (target_pos[1]-click_pos[1]) * (target_pos[1]-click_pos[1]))
        if dist > self.current_target()[1]:
            return False
        else:
            click_offset = (target_pos[0] - click_pos[0], target_pos[1] - click_pos[1])
            # self.log_time(self.stop_measurement(), click_offset)
            self.clicked_targets += 1
            return True

# concrete implementation of Fitts law pointing 
class PointingExperimentTest(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        # initialize model
        self.model = PointingExperimentModel()
        self.descriptionText = "main hand on touchpad \n" \
                               "weak hand on spacebar \n" \
                               "to start press space!"
        self.screenWidth = 793
        self.screenHeight = 603
        self.start_pos = (self.screenWidth / 2, self.screenHeight / 2)
        self.xpos = 0
        self.ypos = 0
        self.position = (0,0)
        self.testStarted = False
        self.initUI()
        self.initScreen()

    def initUI(self):
        self.text = "Please click on the target"
        self.setGeometry(0, 0, self.screenWidth, self.screenHeight)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(self.start_pos[0], self.start_pos[1])))
        self.setMouseTracking(True)
        self.center()
        self.show()
        self.update()

    def initScreen(self):
        secRange = max(self.model.widths) / 2
        self.screenXMin = secRange
        self.screenXMax = self.screenWidth - secRange
        self.screenYMin = secRange
        self.screenYMax = self.screenHeight - secRange

    def target_pos(self, distance):
        ready = False
        while(not ready):
            angle = random.randint(0, 360)
            if angle == 0:
                x = self.start_pos[0] + distance
                y = self.start_pos[1]
            elif angle == 180:
                x = self.start_pos[0] - distance
                y = self.start_pos[1]
            elif angle == 90:
                x = self.start_pos[0]
                y = self.start_pos[1] + distance            
            elif angle == 270:
                x = self.start_pos[0]
                y = self.start_pos[1] - distance        
            else:
                
                
                if angle > 270:
                    factorB = -1
                    beta = 360 - angle
                elif angle > 180:
                    factorB = -1
                    beta = angle - 180
                elif angle > 90:
                    factorB = 1
                    beta = 180 - angle
                else:
                    factorB = 1
                    beta = angle
                    
                alpha = 90
                gamma = 90 - angle
                
                a = distance
                b = factorB * distance * math.sin(math.radians(beta)) / math.sin(math.radians(90))
                c = distance * math.sin(math.radians(gamma)) / math.sin(math.radians(90))
                
                x = self.start_pos[0] + c
                y = self.start_pos[1] + b

            if x > self.screenXMax:
                x = self.start_pos[0] - c
            elif x < self.screenXMin:
                x = self.start_pos[0] + c
            if y > self.screenYMax:
                y = self.start_pos[1] - b
            elif y < self.screenYMin:
                y = self.start_pos[1] + b
            if((x < self.screenXMax and x > self.screenXMin) and (y < self.screenYMax and y > self.screenYMin)):
                ready = True
            else:
                # print("no way!")
    
        return (x, y)

    def drawCircles(self, event, qp):
        if self.model.current_target() is not None:
            distance, size = self.model.current_target()
        else:
            sys.stderr.write("no targets left...")
            sys.exit(1)
        self.position = self.target_pos(distance)
        # print(self.position)
        self.xpos = self.position[0]
        self.ypos = self.position[1]
        qp.setBrush(QtGui.QColor(200, 34, 20))
        qp.drawEllipse(self.xpos-size/2, self.ypos-size/2, size, size)

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        # self.drawBackground(event, qp)
        if self.testStarted:
            self.drawCircles(event, qp)
        else:
            self.drawDescriptionText(event, qp)
        qp.end()

    # centers window on screen
    # source: http://zetcode.com/gui/pyqt5/firstprograms/
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())   

    # handles drawing of description text
    def drawDescriptionText(self, event, qp):
        # sets color
        qp.setPen(QtGui.QColor(0, 204, 255))
        # sets font
        qp.setFont(QtGui.QFont('Decorative', 18))
        # draws text
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.descriptionText)

        # handles keyPress Events
    def keyPressEvent(self, event):
        # if space button is pressed
            if not self.testStarted and event.key() == QtCore.Qt.Key_Space:
                self.testStarted = True
                self.descriptionText = ""
                self.update()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            tar = (self.xpos, self.ypos)
            hit = self.model.register_click(tar, (event.x(), event.y()))
            if hit:
                #QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(self.start_pos[0], self.start_pos[1])))
                print("YO HIT!!")
                self.update()
            else:
                print("YO MISS!")                


def main():
    app = QtWidgets.QApplication(sys.argv)
    pet = PointingExperimentTest()
    pet.setWindowTitle("Pointing experiment")
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
