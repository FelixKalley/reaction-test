#!/usr/bin/python3

# Contribution: Felix Kalley, Lena Manschewski

# imports
import sys
import random
import math
import itertools
import datetime
import json
import csv
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication
from PyQt5.QtGui import QCursor
from configparser import ConfigParser

""" setup.ini file looks like this:
; ini file for experiment input
[user]
id = 1
pointer = default

[circles]
; min = 0, max = 200
widths = 35, 60, 100, 170
; min = 0, max = 400
distances = 170, 200, 300, 400

[colors]
; possible colors are red, green, blue and gray
order = red, green, blue, gray
"""

""" setup.json file looks like this:
{
    "user": {
        "id": "1",
        "pointer": "default"
    },
    "circles": {
        "widths": "35, 60, 100, 170",
        "distances": "170, 200, 300, 400"
    },
    "colors": {
        "order": "red, green, blue, gray"
    }
}
"""


# experiment model that can be reused for task 5.2
class PointingExperimentModel(object):

    # init everything needed for model
    def __init__(self):
        # timer for measuring time
        self.timer = QtCore.QTime()
        # parser for reading .ini files
        self.config = ConfigParser()
        # parses either .json or .ini file
        self.parse_file()
        # amount of repetitions per round
        self.repetitions = 10
        # amount of circles per repetition
        self.amountCircles = 5
        self.clicks_per_circle = 0
        # bool for movement detection
        self.mouse_moving = False
        # number of clicked targets
        self.clicked_targets = 0
        # creates targets
        self.create_targets()
        # array for distractor targets
        self.distractor_targets = []
        # starting time for .csv logging
        self.startedTimestamp = str(datetime.datetime.now()).split('.')[0]
        # console output for logging overview
        print("timestamp (ISO); user_id; trial; target_distance; target_size;",
              "movement_time (ms); click_offset_x; click_offset_y, click_per_circle")

    # creates the targets that should be clicked
    def create_targets(self):
        # creates list of targets consisting of tuples (distance, width)
        self.targets = self.repetitions * list(itertools.product(self.distances, self.widths))
        # randomizes targets
        random.shuffle(self.targets)
        # creates a list of distractors consisting of tuples (distance, width)
        self.distractors = self.repetitions * self.amountCircles * list(itertools.product(self.distances, self.widths))
        # randomizes targets
        random.shuffle(self.distractors)

    # returns a list of current distractor targets
    def current_distractors(self):
        # if more targets exist than have been clicked
        if len(self.targets) > self.clicked_targets:
            # clears distractor targets
            self.distractor_targets.clear()
            # for amount of circles
            for index in range(0, self.amountCircles-1):
                # appends distractors as distractor targets
                self.distractor_targets.append(self.distractors[self.clicked_targets + index])
            # returns distractor targets
            return self.distractor_targets
        # otherwise
        else:
            # returns nothing
            return None

    # returns the current target
    def current_target(self):
        # if more targets exist than have been clicked
        if len(self.targets) > self.clicked_targets:
            # returns the current target
            return self.targets[self.clicked_targets]
        # otherwise
        else:
            # returns nothing
            return None

    # parses .ini or .json file
    def parse_file(self):
        # if file is given
        if len(sys.argv[1:]):
            # tries storing content of .ini file as variables
            try:
                # reads the file
                self.config.read(sys.argv[1])
                # gets user id from file
                self.user_id = self.config.get("user", "id")
                # gets pointer setting from file
                self.pointer = self.config.get("user", "pointer")
                # temporarily stores the circle widths as string
                str_widths = self.config.get("circles", "widths")
                # splits the content of the string into width ints
                self.widths = [int(x) for x in str_widths.split(",")]
                # temporarily stores the circle distances as string
                str_distances = self.config.get("circles", "distances")
                # splits the content of the string into distance ints
                self.distances = [int(x) for x in str_distances.split(",")]
                # temporarily stores the order of colors as string
                str_colors = self.config.get("colors", "order")
                # splits the content of the string into single color strings
                self.colors = [str for str in str_colors.split(", ")]
                # prints notice of successful parsing
                print("Successfully parsed as .ini-file.")
            # if errors occur while parsing .ini file
            except:
                # prints error message
                print("No correct .ini file given! Trying to parse as JSON...")
                # tries storing content of .json file as variables
                try:
                    # opens .json file as data_file
                    with open(sys.argv[1]) as data_file:
                        # saves content in json_input
                        json_input = json.load(data_file)
                    # gets user id from input
                    self.user_id = int(json_input["user"]["id"])
                    # gets pointer setting from input
                    self.pointer = json_input["user"]["pointer"]
                    # temporarily stores the circle widths as string
                    str_widths = json_input["circles"]["widths"]
                    # splits the content of string into width ints
                    self.widths = [int(x) for x in str_widths.split(",")]
                    # temporarily stores the circle distances as string
                    str_distances = json_input["circles"]["distances"]
                    # splits the content of string into distance ints
                    self.distances = [int(x) for x in str_widths.split(",")]
                    # temporarily stores the order of colors as string
                    str_colors = json_input["colors"]["order"]
                    # splits the content of the string into single color strings
                    self.colors = str_colors.strip().split(", ")
                    # prints notice of successful parsing
                    print("Successfully parsed as .json-file")
                # if errors occur while parsing .json file
                except:
                    # prints error message
                    sys.stderr.write("Error: Could not parse as .ini or .json file! \
                                      Please check comments for file formatting.")
                    # exits program
                    sys.exit(1)
        # if no file is given or something went wrong with file input
        else:
            # prints error message
            sys.stderr.write("Error: Something went wrong with the file input. \
                              Please use .json or .ini files.")
            # exits program
            sys.exit(1)

    # registers if a target is clicked
    def register_click(self, target_pos, click_pos):
        # calculates distance between target and click position (Pythagorean Theorem)
        dist = math.sqrt((target_pos[0]-click_pos[0]) * (target_pos[0]-click_pos[0]) +
                         (target_pos[1]-click_pos[1]) * (target_pos[1]-click_pos[1]))
        # if distance from click position to target is bigger than target radius
        if dist > self.current_target()[1] / 2:
            # counting missclicks
            self.clicks_per_circle += 1
            # returns missclick
            return False
        # otherwise
        else:
            # counting correct click
            self.clicks_per_circle += 1
            # saves click offset (x,y) from target origin as tuple
            click_offset = (target_pos[0] - click_pos[0], target_pos[1] - click_pos[1])
            # logs data of click
            self.log_time(self.stop_measurement(), click_offset)
            # raises clicked targets by 1
            self.clicked_targets += 1
            # reset clicks per circle
            self.clicks_per_circle = 0
            # returns hit
            return True

    # logs data of clicks
    def log_time(self, time, click_offset):
        # temporarily saves distance and size of current target
        distance, size = self.current_target()
        # writes data into .csv file
        self.writeCSV(time, click_offset, distance, size)
        # prints data to console
        print("%s; %s; %d; %d; %d; %d; %d; %d; %d"
              % (self.timestamp(), self.user_id, self.clicked_targets,
                  distance, size, time, click_offset[0], click_offset[1], self.clicks_per_circle))

    # writes the current trail to the log file
    def writeCSV(self, time, click_offset, distance, size):
        # all data for current log row
        csvRow = [self.timestamp(), self.user_id, self.clicked_targets, distance,
                  size, time, click_offset[0], click_offset[1], self.clicks_per_circle]
        # name of current log file with timestamp to not override old ones
        logName = "pointing_experiment_log" + str(self.user_id) + "_" + self.startedTimestamp + ".csv"
        # opens csv as logfile
        with open(logName, 'a+') as logfile:
            # writer for logfile writing
            csvWriter = csv.writer(logfile)
            # if is first log row
            if(self.clicked_targets == 0):
                # csv header row
                csvHeader = ["timestamp (ISO)", "user_id", "trial", "target_distance",
                             "target_size", "movement_time (ms)", "click_offset_x",
                             "click_offset_y", "clicks_per_circle"]
                # writes header row
                csvWriter.writerow(csvHeader)
            # writes log row to file
            csvWriter.writerow(csvRow)

    # starts measument
    def start_measurement(self):
        # if no mouse movement
        if not self.mouse_moving:
            # starts timer
            self.timer.start()
            # sets movement indicator to true
            self.mouse_moving = True

    # stops measurement
    def stop_measurement(self):
        # if mouse is moving
        if self.mouse_moving:
            # temporarily saves elapsed time
            elapsed = self.timer.elapsed()
            # sets movement indicator to false
            self.mouse_moving = False
            # returns elapsed time
            return elapsed
        # otherwise
        else:
            # writes error
            self.debug("not running")
            # returns placeholder
            return -1

    # creates and returns new values for impossible target
    def impossible_target(self):
        # temporarily saves new distance
        newDistance = self.distances[random.randint(0, len(self.distances) - 1)]
        # temporarily saves new width
        newWidth = self.widths[random.randint(0, len(self.widths) - 1)]
        # returns new distance and width
        return newDistance, newWidth

    # creates and returns timestamp
    def timestamp(self):
        # returns timestamp
        return QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)

    # creates and writes error
    def debug(self, msg):
        # writes error with timestamp and message
        sys.stderr.write(self.timestamp() + ": " + str(msg) + "\n")


# experiment implementation
class PointingExperimentTest(QtWidgets.QWidget):
    def __init__(self, window):
        super().__init__()
        self.windowFrame = window
        print(self.windowFrame)
        # initialize model
        self.model = PointingExperimentModel()
        # initialize cursor
        self.cursor = QtGui.QCursor()
        # description text for title screen
        self.descriptionText = "This is an experiment to test your aiming speed. \n" \
                               " \n" \
                               "You will see several circles. \n" \
                               "Please click the one with the lightest color. \n" \
                               " \n" \
                               "Put your dominant hand on the touchpad. \n" \
                               "Put your weak hand on the space bar. \n" \
                               "Keep both hands in this position. \n" \
                               " \n" \
                               "To start press space!"
        # screen width
        self.screenWidth = 793
        # screen height
        self.screenHeight = 603
        # list of positions
        self.positionList = []
        # cursor start position
        self.start_pos = (self.screenWidth / 2, self.screenHeight / 2)
        # x position for circles
        self.xpos = 0
        # y position for circles
        self.ypos = 0
        # position for circles
        self.position = (0, 0)
        # indicator if test has started
        self.testStarted = False
        # number of actual round
        self.round = 0
        # indicator if round is finished
        self.finishedRound = False
        # number of hits
        self.numHits = 0
        # target color (initially dark gray / black)
        self.target_color = QtGui.QColor(50, 50, 50)
        # distractor color (initially black)
        self.distractor_color = QtGui.QColor(0, 0, 0)
        # saves colors from model as circle colors
        self.circle_colors = self.model.colors
        # inits ui
        self.initUI()
        # inits screen
        self.initScreen()
        # inits pointer
        self.initPointer()

    # inits all parts of ui
    def initUI(self):
        # sets screen position
        self.setGeometry(0, 0, self.screenWidth, self.screenHeight)
        # sets focus
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        # sets cursor to start position
        QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(self.start_pos[0], self.start_pos[1])))
        # enables mouse tracking
        self.setMouseTracking(True)
        # centers position of screen
        self.center()
        # shows screen
        self.show()
        # updates everything
        self.update()

    # inits the screen
    def initScreen(self):
        # defines range where circles can be placed without crossing the screen border
        secRange = max(self.model.widths) / 2
        # minimum x pos
        self.screenXMin = secRange
        # maximum x pos
        self.screenXMax = self.screenWidth - secRange
        # minimum y pos
        self.screenYMin = secRange
        # maximum y pos
        self.screenYMax = self.screenHeight - secRange

    # inits pointer depending on type
    def initPointer(self):
    	# if default
        if self.model.pointer == "default":
        	# do nothing
        	pass
        # if special
        elif self.model.pointer == "special":
        	# import special cursor class
        	from pointing_technique import SpecialCursor
        	self.special_cursor = SpecialCursor(self.windowFrame)
        # otherwise (optional other cursors)
        else:
        	# do nothing
        	pass

    # sets target position
    def target_pos(self, distance, radius):
        # bool to check if target position found
        ready = False
        # counter to limit iterations
        counter = 0
        # if target values changed this is no longer (0, 0)
        changed = (0, 0)
        # while no position found for target
        while(not ready):
            # get random angle for direction of target to previous
            angle = random.randint(0, 360)
            # when the angel is 0, 90, 180 or 270 the calculation is easier
            if angle == 0:
                x = self.current_pos()[0] + distance
                y = self.current_pos()[1]
            elif angle == 180:
                x = self.current_pos()[0] - distance
                y = self.current_pos()[1]
            elif angle == 90:
                x = self.current_pos()[0]
                y = self.current_pos()[1] + distance
            elif angle == 270:
                x = self.current_pos()[0]
                y = self.current_pos()[1] - distance
            else:
                if angle > 270:
                    # to get right values the value of the "b" side has to be inverted
                    factorB = -1
                    # to build a rectangle the beta angle has to be adjusted
                    beta = 360 - angle
                elif angle > 180:
                    # to get right values the value of the "b" side has to be inverted
                    factorB = -1
                    # to build a rectangle the beta angle has to be adjusted
                    beta = angle - 180
                elif angle > 90:
                    factorB = 1
                    # to build a rectangle the beta angle has to be adjusted
                    beta = 180 - angle
                else:
                    factorB = 1
                    beta = angle

                alpha = 90
                gamma = 90 - angle

                # calculating the sides of the rectangle to get the distance
                a = distance
                b = factorB * distance * math.sin(math.radians(beta)) / math.sin(math.radians(90))
                c = distance * math.sin(math.radians(gamma)) / math.sin(math.radians(90))

                # setting the position of the new circle
                x = self.current_pos()[0] + c
                y = self.current_pos()[1] + b

                # if the new circle is out of window bounds, invert the directions
                if x > self.screenXMax:
                    x = self.current_pos()[0] - c
                elif x < self.screenXMin:
                    x = self.current_pos()[0] + c
                if y > self.screenYMax:
                    y = self.current_pos()[1] - b
                elif y < self.screenYMin:
                    y = self.current_pos()[1] + b
            # if circle is full on screen
            if((x < self.screenXMax and x > self.screenXMin) and (y < self.screenYMax and y > self.screenYMin)):
                # if length of previous targets list is empty, its the first circle to draw
                # and it cannot overlap
                if not (len(self.positionList) == 0):
                    for posData in self.positionList:
                        # delta of x coordinates
                        xDelta = x - posData[0]
                        # delta of y coordinates
                        yDelta = y - posData[1]
                        # distance between center points
                        calculatedDist = math.sqrt(math.pow(xDelta, 2) + math.pow(yDelta, 2))
                        # should minimal distance between points + little space between circles
                        minDist = radius + posData[2] + 5
                        # if the minimal distance is greater than the acutal distance
                        # the circles are overlapping
                        if(minDist > calculatedDist):
                            # do another loop
                            ready = False
                            # increase counter for emergency break
                            counter += 1
                            # if it is the 20. loop change targets distance and size and try again
                            if counter > 20:
                                distance, size = self.model.impossible_target()
                                radius = size / 2
                                # set changed values
                                changed = (distance, size)
                                # reset counter
                                counter = 0
                            break
                        # circles not overlapping
                        else:
                            ready = True
                # its the first circle
                else:
                    ready = True
            # Circle is of screen
            else:
                # increase counter for emergency break
                counter += 1
                # if it is the 20. loop change targets distance and size and try again
                if counter > 20:
                    distance, size = self.model.impossible_target()
                    radius = size / 2
                    # set changed values
                    changed = (distance, size)
                    # reset counter
                    counter = 0
        # returns x and y coordinates of the new target and the new specification if changed
        return (x, y, changed)

    # returns current circle position
    def current_pos(self):
        # returns xpos and ypos
        return (self.xpos, self.ypos)

    # draws distractor circles
    def drawDistractorCircles(self, event, qp):
        if self.shouldRedraw:
            for circle in self.positionList[:-1]:
                x = circle[0]
                y = circle[1]
                size = circle[2] * 2

                self.redrawCircle(x, y, size, self.distractor_color, qp)
        elif self.model.current_distractors() is not None:
            self.positionList.clear()
            for circle in self.model.current_distractors():
                distance = circle[0]
                size = circle[1]

                self.drawCircle(distance, size, self.distractor_color, qp, True)
        else:
            sys.stderr.write("no targets left...")
            sys.exit(1)

    # draws all circles
    def drawAllCircles(self, event, qp):
        self.drawDistractorCircles(event, qp)
        if self.shouldRedraw:
            for circle in self.positionList[-1:]:
                x = circle[0]
                y = circle[1]
                size = circle[2] * 2

                self.redrawCircle(x, y, size, self.target_color, qp)
        elif self.model.current_target() is not None:
            distance, size = self.model.current_target()
            self.drawCircle(distance, size, self.target_color, qp, False)
        else:
            sys.stderr.write("no targets left...")
            sys.exit(1)
        self.shouldRedraw = True

    # redraws a circle
    def redrawCircle(self, x, y, size, color, qp):
        # sets color
        qp.setBrush(color)
        # draws a circle
        qp.drawEllipse(x-size/2, y-size/2, size, size)

    # draws a circle !only called from drawAllCircles and drawDistractorCircles!
    def drawCircle(self, distance, size, color, qp, isDistractor):
        self.position = self.target_pos(distance, size / 2)
        x = self.position[0]
        y = self.position[1]
        if(not self.position[2] == (0, 0)):
            distance = self.position[2][0]
            size = self.position[2][1]

        if not isDistractor:
            self.xpos = x
            self.ypos = y
        # x, y, radius
        self.positionList.append((x, y, size / 2))
        qp.setBrush(color)
        qp.drawEllipse(x-size/2, y-size/2, size, size)

    # handles paint events
    def paintEvent(self, event):
        # initializes QPainter
        qp = QtGui.QPainter()
        # starts painting
        qp.begin(self)
        # if the test started and the round is going on
        if self.testStarted and not self.finishedRound:
            # draws all circles
            self.drawAllCircles(event, qp)
        # if the round is finished
        elif self.finishedRound:
            # draws description text
            self.drawDescriptionText(event, qp)
        # otherwise
        else:
            # draws description text
            self.drawDescriptionText(event, qp)
        # ends painting
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
        # if test is not running and space button is pressed (first screen)
            if not self.testStarted and event.key() == QtCore.Qt.Key_Space:
                # sets redraw indicator to false
                self.shouldRedraw = False
                # sets test indicator to true
                self.testStarted = True
                # deletes description text
                self.descriptionText = ""
                # sets round number to 1
                self.round = 1
                # checks color order
                self.checkColor()
                # updates everything
                self.update()
            # otherwise if test is started and round is finished and round is not last round
            elif self.testStarted and self.finishedRound and not self.round == 4:
                # sets redraw indicator to false
                self.shouldRedraw = False
                # deletes description text
                self.descriptionText = ""
                # sets round finished indicator to false
                self.finishedRound = False
                # raises round number by 1
                self.round += 1
                self.numHits = 0

                # checks color order
                self.checkColor()
                # updates everything
                self.update()

    # starts measurement if mouse movement is detected
    def mouseMoveEvent(self, ev):
        # checks if test is running and mouse is moving
        if self.testStarted and ((abs(ev.x() - self.start_pos[0]) > 5) or (abs(ev.y() - self.start_pos[1]) > 5)):
            # starts measurement
            self.model.start_measurement()
            # updates everything
            self.update()

    # handles mouse clicks
    def mousePressEvent(self, event):
        # if left mouse button is pressed
        if event.button() == QtCore.Qt.LeftButton:
            # only check if hit when round is not finished
            if not self.finishedRound:
                # current cursor position is saved
                position_clicked = self.current_pos()
                # checks if a target got hit
                check_hit = self.model.register_click(position_clicked, (event.x(), event.y()))
                # if successful hit
            # if round finished the check is false
            else:
                check_hit = False

            if check_hit:
                # if number of hit targets is smaller then number of repetitions
                if self.numHits < self.model.repetitions - 1:
                    # redraw indicator is set to false
                    self.shouldRedraw = False
                    # number of hits is raised by 1
                    self.numHits += 1
                    # updates everything
                    self.update()
                # otherwise (all repetitions done)
                else:
                    # round is finished
                    self.finishedRound = True
                    # check number of round
                    self.checkRound()
                    # number of hits is resetted
                    self.numHits = 0
                    # updates everything
                    self.update()

    # checks number of round and sets text
    def checkRound(self):
        # if round 1
        if self.round == 1:
            # text for round 1
            self.descriptionText = "First round done! \n" \
                                   "To continue, press space."
        # if round 2
        if self.round == 2:
            # text for round 2
            self.descriptionText = "Second round done! \n" \
                                  "To continue, press space."
        # if round 3
        if self.round == 3:
            # text for round 3
            self.descriptionText = "Third round done! \n" \
                                   "To continue, press space."
        # if round 4
        if self.round == 4:
            # text for round 4
            self.descriptionText = "FINISHED! \n" \
                                   "You can now close the program."
        # otherwise (not intended)
        else:
            pass

    # checks color order for next color to be used
    def checkColor(self):
        # if red
        if self.circle_colors[self.round-1] == "red":
            # red target color
            self.target_color = QtGui.QColor(255, 0, 0)
            # red distractor color
            self.distractor_color = QtGui.QColor(130, 0, 0)
        # if green
        elif self.circle_colors[self.round-1] == "green":
            # green target color
            self.target_color = QtGui.QColor(0, 255, 0)
            # green distractor color
            self.distractor_color = QtGui.QColor(0, 130, 0)
        # if blue
        elif self.circle_colors[self.round-1] == "blue":
            # blue target color
            self.target_color = QtGui.QColor(0, 0, 255)
            # blue distractor color
            self.distractor_color = QtGui.QColor(0, 0, 130)
        # if gray
        elif self.circle_colors[self.round-1] == "gray":
            # gray target color
            self.target_color = QtGui.QColor(125, 125, 125)
            # gray distractor color
            self.distractor_color = QtGui.QColor(50, 50, 50)
        # otherwise (not intended)
        else:
            pass


# main
def main():
    # initializes app
    app = QtWidgets.QApplication(sys.argv)
    # initializes experiment
    pet = PointingExperimentTest(app)
    # sets window title
    pet.setWindowTitle("Pointing experiment")
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
