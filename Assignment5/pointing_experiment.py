#!/usr/bin/python3

# Contribution: Felix Kalley, Lena Manschewski


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

import sys
import random
import math
import itertools
import datetime
import json
import csv
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication
from configparser import ConfigParser

# model that can be reused for task 5.2
# pure python - no camel case?
class PointingExperimentModel(object):
    def __init__(self):
        #self.parse_input()
        self.timer = QtCore.QTime()
        self.config = ConfigParser()
        self.parse_file()
        # amount of repetitions per round
        self.repetitions = 10
        # amount of circles per repetition
        self.amountCircles = 5
        self.mouse_moving = False
        self.clicked_targets = 0
        self.create_targets()
        self.distractor_targets = []
        self.startedTimestamp = str(datetime.datetime.now()).split('.')[0]

        print("timestamp (ISO); user_id; trial; target_distance; target_size; movement_time (ms); click_offset_x; click_offset_y")

    # creates the targets that should be clicked
    def create_targets(self):
        # gives us a list of (distance, width) tuples:
        self.targets = self.repetitions * list(itertools.product(self.distances, self.widths))
        random.shuffle(self.targets)
        self.distractors = self.repetitions * self.amountCircles * list(itertools.product(self.distances, self.widths))
        random.shuffle(self.distractors)


    def current_distractors(self):
        if len(self.targets) > self.clicked_targets:
            self.distractor_targets.clear()
            for index in range(0, self.amountCircles-1):
                self.distractor_targets.append(self.distractors[self.clicked_targets + index])
            return self.distractor_targets
        else:
            return None


    def current_target(self):
        if len(self.targets) > self.clicked_targets:
            return self.targets[self.clicked_targets]
        else:
            return None
    
    def parse_file(self):
        # if file is given
        if len(sys.argv[1:]):
            try:
                self.config.read(sys.argv[1])
                self.user_id = self.config.get("user", "id")
                self.pointer = self.config.get("user", "pointer")
                str_widths = self.config.get("circles", "widths")
                self.widths = [int(x) for x in str_widths.split(",")]
                str_distances = self.config.get("circles", "distances")
                self.distances = [int(x) for x in str_distances.split(",")]
                str_colors = self.config.get("colors", "order")
                self.colors = [str for str in str_colors.split(", ")]
                print("Successfully parsed as .ini-file.")
            except:
                # prints error message
                print("No correct .ini file given! Trying to parse as JSON...")
                try:
                    with open(sys.argv[1]) as data_file:    
                        json_input = json.load(data_file)
                    self.user_id = int(json_input["user"]["id"])
                    self.pointer = json_input["user"]["pointer"]
                    str_widths = json_input["circles"]["widths"]
                    self.widths = [int(x) for x in str_widths.split(",")]
                    str_distances = json_input["circles"]["distances"]
                    self.distances = [int(x) for x in str_widths.split(",")]
                    str_colors = json_input["colors"]["order"]
                    self.colors = str_colors.strip().split(", ")
                    print("Successfully parsed as .json-file")
                except:
                    sys.stderr.write("Error: Could not parse as .ini or .json file! Please check comments for file formatting.")
                    sys.exit(1)
        else:
            sys.stderr.write("Error: Something went wrong with the file formatting.")
            sys.exit(1)
    
    def register_click(self, target_pos, click_pos):
        #print("I REGISTERED A CLICK!")
        #print(target_pos)
        #print(click_pos)
        dist = math.sqrt((target_pos[0]-click_pos[0]) * (target_pos[0]-click_pos[0]) +
                         (target_pos[1]-click_pos[1]) * (target_pos[1]-click_pos[1]))
        if dist > self.current_target()[1]:
            return False
        else:
            click_offset = (target_pos[0] - click_pos[0], target_pos[1] - click_pos[1])
            self.log_time(self.stop_measurement(), click_offset)
            self.clicked_targets += 1
            return True

    def log_time(self, time, click_offset):
        distance, size = self.current_target()
        self.writeCSV(time, click_offset, distance, size)
        print("%s; %s; %d; %d; %d; %d; %d; %d" % (self.timestamp(), self.user_id, self.clicked_targets, distance, size, time, click_offset[0], click_offset[1]))


    # writes the current trail to the log file
    def writeCSV(self, time, click_offset, distance, size):
        # all data for current log row
        csvRow = [self.timestamp(), self.user_id, self.clicked_targets, distance,
                  size, time, click_offset[0], click_offset[1]]
        # name of current log file with timestamp to not override old ones
        logName = "pointing_experiment_log" + str(self.user_id) + "_" + self.startedTimestamp + ".csv"
        # write log row to file
        with open(logName, 'a+') as logfile:
            csvWriter = csv.writer(logfile)
            # if is first log row, first write header row
            if(self.clicked_targets == 0):
                # csv header row
                csvHeader = ["timestamp (ISO)", "user_id", "trial", "target_distance",
                             "target_size", "movement_time (ms)", "click_offset_x",
                             "click_offset_y"]
                csvWriter.writerow(csvHeader)
            csvWriter.writerow(csvRow)



    def start_measurement(self):
        if not self.mouse_moving:
            self.timer.start()
            self.mouse_moving = True

    def stop_measurement(self):
        if self.mouse_moving:
            elapsed = self.timer.elapsed()
            self.mouse_moving = False
            return elapsed
        else:
            self.debug("not running")
            return -1

    def impossible_target(self):
        newDistance = self.distances[random.randint(0, len(self.distances) - 1)]
        newWidth = self.widths[random.randint(0, len(self.widths) - 1)]
        # new distance and width 
        return newDistance, newWidth

    def timestamp(self):
        return QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)

    def debug(self, msg):
        sys.stderr.write(self.timestamp() + ": " + str(msg) + "\n")

    
# concrete implementation of Fitts law pointing 
class PointingExperimentTest(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        # initialize model
        self.model = PointingExperimentModel()
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
        self.screenWidth = 793
        self.screenHeight = 603
        
        self.positionList = []
        self.start_pos = (self.screenWidth / 2, self.screenHeight / 2)
        self.xpos = 0
        self.ypos = 0
        self.position = (0,0)
        self.testStarted = False
        self.round = 0
        self.finishedRound = False
        self.numHits = 0
        self.target_color = QtGui.QColor(20,20,20)
        self.distractor_color = QtGui.QColor(10, 10, 10)
        self.circle_colors = self.model.colors
        print(self.circle_colors)
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

    def target_pos(self, distance, radius):
        ready = False
        counter = 0
        changed = (0,0)
        while(not ready):
            angle = random.randint(0, 360)
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
                
                x = self.current_pos()[0] + c
                y = self.current_pos()[1] + b

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
                if not (len(self.positionList) == 0):
                    for posData in self.positionList:
                        # delta of x coordinates
                        xDelta = x - posData[0]
                        # delta of y coordinates
                        yDelta = y - posData[1]
                        # distance between points
                        calculatedDist = math.sqrt(math.pow(xDelta, 2) + math.pow(yDelta, 2))
                        # should minimal distance between points + little space between circles
                        minDist = radius + posData[2] + 5
                        if(minDist > calculatedDist):
                            ready = False
                            counter += 1
                            # print("redraw!!!", radius * 2, calculatedDist, minDist, posData[2])
                            if counter > 20:
                                # print("before:", distance, radius)
                                distance, size = self.model.impossible_target()
                                radius = size / 2
                                # print("after:", distance, radius)
                                changed = (distance, size)
                                counter = 0
                            break
                        else:
                            ready = True
                            # print("ok")
                else:
                    ready = True
            else:
                counter += 1
                if counter > 20:
                    print("not on screen, new values")
                    distance, size = self.model.impossible_target()
                    radius = size / 2
                    # print("after:", distance, radius)
                    changed = (distance, size)
                    counter = 0
                
        return (x, y, changed)
        
    def current_pos(self):
        return (self.xpos, self.ypos)

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
                
                self.drawCircle(distance, size, self.distractor_color, qp)
        else:
            sys.stderr.write("no targets left...")
            sys.exit(1)

        
        
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
            self.drawCircle(distance, size, self.target_color, qp)
        else:
            sys.stderr.write("no targets left...")
            sys.exit(1)
        self.shouldRedraw = True

    def redrawCircle(self, x, y, size, color, qp):
        qp.setBrush(color)
        qp.drawEllipse(x-size/2, y-size/2, size, size)

    # only called from drawAllCircles and drawDistractorCircles
    def drawCircle(self, distance, size, color, qp):
        self.position = self.target_pos(distance, size / 2)
        self.xpos = self.position[0]
        self.ypos = self.position[1]
        if(not self.position[2] == (0,0)):
            distance = self.position[2][0]
            size = self.position[2][1]

        # x, y, radius
        self.positionList.append((self.xpos, self.ypos, size / 2))  
        qp.setBrush(color)
        qp.drawEllipse(self.xpos-size/2, self.ypos-size/2, size, size)
    
    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        # self.drawBackground(event, qp)
        if self.testStarted and not self.finishedRound:
            self.drawAllCircles(event, qp)
        elif self.finishedRound:
            self.drawDescriptionText(event, qp)
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
                self.shouldRedraw = False
                self.testStarted = True
                self.descriptionText = ""
                self.round = 1
                self.checkColor()
                self.update()
            elif self.testStarted and self.finishedRound and not self.round == 4:
                self.shouldRedraw = False
                self.descriptionText = ""
                self.finishedRound = False
                self.round += 1
                self.checkColor()
                self.update()
                
    
    def mouseMoveEvent(self, ev):
        if self.testStarted and ((abs(ev.x() - self.start_pos[0]) > 5) or (abs(ev.y() - self.start_pos[1]) > 5)):
            self.model.start_measurement()
            self.update()

    def mousePressEvent(self, event):
        if self.numHits < self.model.repetitions -1:
            if event.button() == QtCore.Qt.LeftButton:
                position_clicked = self.current_pos()
                check_hit = self.model.register_click(position_clicked, (event.x(), event.y()))
            if check_hit:
                #QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(self.start_pos[0], self.start_pos[1])))
                #print("YO HIT!!")
                self.shouldRedraw = False
                self.numHits += 1
                print(self.numHits)

                self.update()
            #else:
                #print("YO MISS!") 
        else: 
            self.finishedRound = True
            self.checkRound()
            self.numHits = 0
            self.update()               

    def checkRound(self):
        if self.round == 1:
            self.descriptionText = "First round done! \n" \
                                   "To continue, press space."
        if self.round == 2:
            self.descriptionText = "Second round done! \n" \
                                   "To continue, press space."
        if self.round == 3:
            self.descriptionText = "Third round done! \n" \
                                   "To continue, press space."
        if self.round == 4:
            self.descriptionText = "FINISHED! \n" \
                                   "You can now close the program."
        else:
            pass

    def checkColor(self):
        if self.circle_colors[self.round-1] == "red":
            self.target_color = QtGui.QColor(255, 0 , 0)
            self.distractor_color = QtGui.QColor(150, 0, 0)
        elif self.circle_colors[self.round-1] == "green":
            self.target_color = QtGui.QColor(0, 255, 0)
            self.distractor_color = QtGui.QColor(0, 150, 0)
        elif self.circle_colors[self.round-1] == "blue":
            self.target_color = QtGui.QColor(0, 0, 255)
            self.distractor_color = QtGui.QColor (0, 0, 120)
        elif self.circle_colors[self.round-1] == "gray":
            self.target_color = QtGui.QColor (125, 125, 125)
            self.distractor_color = QtGui.QColor (70, 70, 70)
        else:
            pass



def main():
    app = QtWidgets.QApplication(sys.argv)
    pet = PointingExperimentTest()
    pet.setWindowTitle("Pointing experiment")
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
