#!/usr/bin/python3

# Contribution: Felix Kalley, Lena Manschewski


""" setup file looks like this:
USER: 1
WIDTHS: 35, 60, 100, 170
DISTANCES: 170, 300, 450, 700
"""

import sys
from PyQt5 import QtGui, QtWidgets, QtCore


class PointingExperimentModel(object):
    def __init__(self):
        self.parseInput()
    
    def parseInput(self):
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

        

class PointingExperimentTest(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.model = PointingExperimentModel()
        print(self.model.user_id)
        print(self.model.distances)
        print(self.model.widths)

        self.start_pos = (793 / 2, 603 / 2)
        self.initUI()

    def initUI(self):
        self.text = "Please click on the target"
        self.setGeometry(0, 0, 793, 603)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(self.start_pos[0], self.start_pos[1])))
        self.setMouseTracking(True)
        self.show()

            


def main():
    app = QtWidgets.QApplication(sys.argv)
    pet = PointingExperimentTest()
    pet.setWindowTitle("Pointing experiment")
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
