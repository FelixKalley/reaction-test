#!/usr/bin/python3

# Contribution: Felix Kalley, Lena Manschewski


""" setup file looks like this:
USER: 1
WIDTHS: 35, 60, 100, 170
DISTANCES: 170, 300, 450, 700
"""

import sys
import random
from PyQt5 import QtGui, QtWidgets, QtCore

# model that can be reused for task 5.2
# pure python - no camel case?
class PointingExperimentModel(object):
    def __init__(self):
        self.parse_input()
        
    def current_target(self):
        distance = random.randint(0, len(self.distances)-1)
        width = random.randint(0, len(self.widths)-1)
        return self.distances[distance], self.widths[width]
    
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

        
# concrete implementation of Fitts law pointing 
class PointingExperimentTest(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        # initialize model
        self.model = PointingExperimentModel()
        
        self.amountCircles = 5
        self.start_pos = (793 / 2, 603 / 2)
        self.initUI()

    def initUI(self):
        self.text = "Please click on the target"
        self.setGeometry(0, 0, 793, 603)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(self.start_pos[0], self.start_pos[1])))
        self.setMouseTracking(True)
        self.show()
        self.update()

    # needs to be two dimensional (wie soll die distance berechnet werden?
    # von wo soll die distance berechnet werden?
    # (current cursor position oder starting position?))
    # sicherstellen, das das Ziel innerhalb des Fensters liegt!
    def target_pos(self, distance):
        x = self.start_pos[0] + distance
        y = self.start_pos[1]
        return (x, y)

 
    # last drawn circle is the correct one, so its always on top
    def drawCircles(self, event, qp):
        for index in range(0, self.amountCircles):
            distance, width = self.model.current_target()
            print(distance)
            print(width)
            print(self.target_pos(distance))
            x, y = self.target_pos(distance)
            if index == self.amountCircles - 1:
                qp.setBrush(QtGui.QColor(255, 0, 0))
            else:
                qp.setBrush(QtGui.QColor(0, 255, 0))
            qp.drawEllipse(x-width/2, y-width/2, width, width)
    
    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        # self.drawBackground(event, qp)
        # self.drawText(event, qp)
        self.drawCircles(event, qp)
        qp.end()

            


def main():
    app = QtWidgets.QApplication(sys.argv)
    pet = PointingExperimentTest()
    pet.setWindowTitle("Pointing experiment")
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
