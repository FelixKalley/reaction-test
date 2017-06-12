#!/usr/bin/python3

# Contribution: Felix Kalley, Lena Manschewski

# imports
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QColor


class SpecialCursor(object):
    def __init__(self, window):
        # saves window from given parameter
        self.givenWindow = window
        # creates pixmap from image
        self.pixmap = QtGui.QPixmap('circle.png')
        # initializes cursor from pixmap
        self.cursor = QtGui.QCursor(self.pixmap)
        # overrides cursor in window
        self.givenWindow.setOverrideCursor(self.cursor)


        #self.setCursor(cursor)
        #self.cursor.shape = Qt.CrossCursor()
        #self.cursor.setShape(self, Qt.CrossCursor())