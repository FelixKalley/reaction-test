#!/usr/bin/python3

# Contribution: Felix Kalley, Lena Manschewski

# imports
import math
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
        self.cursor_radius = 20

    def filter(self, target_position, click_position, circle_list):
    	# registers if a target is clicked
    	
        # calculates distance between target and click position (Pythagorean Theorem)
        dist = math.sqrt((target_position[0]-click_position[0]) * (target_position[0]-click_position[0]) +
                         (target_position[1]-click_position[1]) * (target_position[1]-click_position[1]))
        # if distance from click position to target is bigger than target radius
        print(circle_list[-1][2])
        if (dist - self.cursor_radius) > circle_list[-1][2]:
            print("NO HIT THIS TIME DUDE")
            # counting missclicks
            #self.clicks_per_circle += 1
            # returns missclick
            return False
        # otherwise
        else:
            print("YOU HIT MAN!")
            # counting correct click
            #self.clicks_per_circle += 1
            # saves click offset (x,y) from target origin as tuple
            #click_offset = (target_pos[0] - click_pos[0], target_pos[1] - click_pos[1])
            # logs data of click
            #self.log_time(self.stop_measurement(), click_offset)
            # raises clicked targets by 1
            #self.clicked_targets += 1
            # reset clicks per circle
            #self.clicks_per_circle = 0
            # returns hit
            return True

        #self.setCursor(cursor)
        #self.cursor.shape = Qt.CrossCursor()
        #self.cursor.setShape(self, Qt.CrossCursor())