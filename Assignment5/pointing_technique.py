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
        # sets cursor radius
        self.cursor_radius = 17

    # gets target position, click position and list of circles
    def filter(self, target_position, click_position, circle_list):
        # calculates distance between target and click position (Pythagorean Theorem)
        dist = math.sqrt((target_position[0]-click_position[0]) * (target_position[0]-click_position[0]) +
                         (target_position[1]-click_position[1]) * (target_position[1]-click_position[1]))
        
        # if distance from (click position minus cursor radius) to target is bigger than target radius
        if (dist - self.cursor_radius) > circle_list[-1][2]:
            # saves bool as int!!!
            hit = 0
            # returns missclick
            return hit, target_position, click_position
        # otherwise
        else:
            no_distrator_hit = True
            for distractor in circle_list[:-1]:
                distractor_dist = math.sqrt((distractor[0]-click_position[0]) * (distractor[0]-click_position[0]) +
                         (distractor[1]-click_position[1]) * (distractor[1]-click_position[1]))
                if not (distractor_dist - self.cursor_radius) > distractor[2]:
                    no_distrator_hit = False
                    hit = 0
                    return hit, target_position, click_position

        	# saves bool as int!!!
            hit = 1
            # returns click
            return hit, target_position, click_position