#!/usr/bin/python3

# Contribution: Felix Kalley, Lena Manschewski
'''
Our novel cursor is a circle that expands the area where the subject can click.
So instead of clicking a simple point or pixel, you can now click a broader area,
in our case everything covered under a circle of around 20 px. The circle in the
image in has 22px diameter but in the code it's radius is 17 because this value
covered the image circle perfect.

If the special cursor is clicked while above more than one target it is counted
as missclick because it is not clear which circle the subject wanted to click.

Circle shaped cursors are often used for presenting, to highlight were a
presenter is pointing to with his cursor. In contrast to our technique these
highlighting cursors are only graphical overlays without extending the range
of a click. The main difference between fitts' law pointing technique (default)
and our novel technique (special) is that a user doesn't have to aim as precise,
so this pointing technique may be faster than the default technique.
'''
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
