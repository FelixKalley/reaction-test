#!/usr/bin/python3

# Contribution: Felix Kalley, Lena Manschewski

# imports
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtGui import QCursor


class SpecialCursor(object):
    def __init__(self):
        self.cursor = QtGui.QCursor()
        #self.cursor.setPos(1000, 1000)
        print(self.cursor.shape())
        self.cursor.setShape(2)
        print(self.cursor.shape())

        #self.cursor.shape = Qt.CrossCursor()
        #self.cursor.setShape(self, Qt.CrossCursor())