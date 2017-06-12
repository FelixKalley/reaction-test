#!/usr/bin/python3

# Contribution: Felix Kalley, Lena Manschewski

# imports
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QColor


class SpecialCursor(object):
    def __init__(self, window):
        self.givenWindow = window
        #self.givenWindow.setOverrideCursor(QCursor(Qt.CrossCursor));
        self.cursor = QtGui.QCursor()
        self.cursor.setPos(1700, 700)
        self.mycolor = QtGui.QColor("white")
        print(self.cursor.shape())
        self.cursor.setShape(2)
        print(self.cursor.shape())
        pm = QtGui.QPixmap('test.png')
        bm = pm.createMaskFromColor(self.mycolor, Qt.MaskOutColor)
        #pm.setAlphaChannel(bm)
        self.cursor = QtGui.QCursor(pm)
        self.givenWindow.setOverrideCursor(self.cursor)
        #self.setCursor(cursor)
        #self.cursor.shape = Qt.CrossCursor()
        #self.cursor.setShape(self, Qt.CrossCursor())