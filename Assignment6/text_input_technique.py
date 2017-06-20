#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
This gives a measure in characters per second (cps). To convert this to words
per minute (wpm) the standard typists' definition of a word as five characters
(regardless of whether the characters are letters, punctuation, or spaces)
is employed (Gentner, Grudin, Larochelle, Norman, & Rumelhart, 1983).
Therefore, words per minute is obtained by multiplying characters per second by
60 (seconds per minute) and dividing by 5 (characters per word). (MacKenzie I.,
Soukoreff R., 2002)
char = 1 char
word = 5 chars
sentence = click return
'''

import sys
import datetime
from PyQt5 import uic, QtWidgets, QtCore, QtGui, Qt
from PyQt5.QtWidgets import QApplication, QLineEdit, QCompleter
from PyQt5.QtCore import QStringListModel, pyqtSignal, QObject
#from PyQt5.QtCore.Qt import Alignment

TAGS = (["The", "five", "boxing", "wizards", "jump", "quickly."],
        ["The", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog."],
        ["Jackdaws", "love", "my", "big", "sphinx", "of", "quartz."],
        ["The", "quick", "onyx", "goblin", "jumps", "over", "the", "lazy", "dwarf."],
        ["My", "girl", "wove", "six", "dozen", "plaid", "jackets", "before", "she", "quit."],
        ["Crazy", "Frederick", "bought", "many", "very", "exquisite", "opal", "jewels."],
        ["Jim", "quickly", "realized", "that", "beautiful", "gowns", "are", "expensive."])

sentence_index = 0

class TextInput(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        # contains data given from file
        self.dataArray = []

        # sentences to type
        self.sentences = ("The five boxing wizards jump quickly.",
                          "The quick brown fox jumps over the lazy dog.",
                          "Jackdaws love my big sphinx of quartz.",
                          "The quick onyx goblin jumps over the lazy dwarf.",
                          "My girl wove six dozen plaid jackets before she quit.",
                          "Crazy Frederick bought many very exquisite opal jewels.",
                          "Jim quickly realized that the beautiful gowns are expensive.")
        # function to check the input file
        self.checkInput()


        self.editor = CompleterLineEdit(self)
        self.editor.setFixedSize(681, 161)
        self.editor.setGeometry(10, 211, 681, 161)
        f = self.editor.font()
        f.setPointSize(14)
        self.editor.setFont(f)
        self.editor.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        # special Completer
        completer = TagsCompleter(self.editor, TAGS[sentence_index])
        # disables case sensitivity
        completer.setCaseSensitivity(False)
        # connects activation of completer with editor function complete_text
        completer.activated.connect(lambda: self.editor.complete_text(completer))
        # connects change of text in editor with completer function update
        self.editor.textChanged.connect(lambda: completer.update(self.editor))
        # sets widget for completer
        completer.setWidget(self.editor)
        #
        self.editor.show()

        # indicates whether a sentences was started or not
        self.sentenceStarted = False
        # start time for character
        self.charStartTime = 0
        # start time for a word (5 chars)
        self.wordStartTime = 0
        # start time for a sentence
        self.sentenceStartTime = 0
        # start time of the experiment
        self.experimentStartTime = 0

        # counting inputs per sentence
        self.inputCount = 0
        # the number of rounds depends on the number of sentences
        self.round = 0
        # function to init the ui
        self.initUI()
        # function to init the experiment
        self.sentenceTyped()

    # checks for given input
    def checkInput(self):
        # if file is given
        if len(sys.argv[1:]):
            # tries if file can be opened
            try:
                with open(sys.argv[1], 'Ur') as input_data:
                    # iterates over every line in given file
                    for line in input_data:
                        # puts content from line into input_data
                        self.dataArray.append(line)
            # if file cannot be opened
            except EnvironmentError as err_open:
                # prints error message
                print('Error accessing file %s: %s' % (sys.argv[1], err_open),
                      file=sys.stderr)
                # exits programm
                sys.exit(err_open.errno)
        # if no file is given
        else:
            print("Please provide one .txt-file as argument")
            sys.exit()

        # function to convert the input into useful data
        self.convertInput()

    # converts the data input
    def convertInput(self):
        # tries splitting strings
        try:
            # splits strings and keeps relevant data
            self.subjectNum = self.dataArray[0].split(":")[1].strip()
            temporaryOrder = self.dataArray[1].split(":")[1]
            # order of the sentences
            self.testOrder = temporaryOrder.strip().split(", ")
            if len(self.testOrder) > len(self.sentences):
                print("to many sentence indexes given, there are only", str(len(self.sentences)), "given.")
                sys.exit()
        # if errors happen while splitting
        except:
            # prints data format as message
            print("The given data does not conform to the standard. \n"
                  "Please format data like this: \n"
                  "PARTICIPANT: 1 \n"
                  "SENTENCE-NR: 3, 2, 1, 4, 7, 5, 6 \n")
            # exits
            sys.exit()

    # init the ui
    def initUI(self):
        # load ui file
        self.ui = uic.loadUi("text_input_technique.ui", self)
        self.show()
        # connect edit text text edited
        self.editor.textEdited.connect(self.editedText)
        # connect edit text return click
        if len(self.editor.text()) >= len(self.ui.GivenTextLabel.text()):
            self.editor.returnPressed.connect(self.sentenceTyped)

    # if text was edited
    def editedText(self):
        # if no sentence was startet and the input count is 0, start experiment
        if(not self.sentenceStarted and self.inputCount == 0):
            self.sentenceStarted = True
            self.startExperimentTimer()

        # increase input count
        self.inputCount += 1
        # a char was typed
        self.charTyped()
        # if 5 chars were typed it is a word
        # print(self.editor.text()[-1:])
        if(self.inputCount % 5 == 0):
            self.wordTyped()

    # if a char was typed stop char time and log
    def charTyped(self):
        time = self.stopCharTimer()
        self.charLog(time)

    # if a word was typed stop word time and log
    def wordTyped(self):
        time = self.stopWordTimer()
        self.wordLog(time)

    # if a sentence was typed it is the next round
    def sentenceTyped(self):
        # if it is not the first round
        if(self.sentenceStarted):
            time = self.stopSentenceTimer()
            self.sentenceLog(time)
        else:
            self.logExperimentStart()
        # if it is not the last round
        if(self.round < len(self.sentences)):
            sentenceIndex = int(self.testOrder[self.round]) - 1
            # show next text
            self.ui.GivenTextLabel.setText(self.sentences[sentenceIndex])
            # clear field
            self.editor.setText("")
            # increase round count
            self.round += 1
            sentence_index = sentenceIndex
            print(sentence_index)
        # if it is the last round
        else:
            # clear given and typed sentence
            self.ui.GivenTextLabel.setText("")
            self.editor.setText("")
            # stop experiment time
            time = self.stopExperimentTimer()
            # log experiment end
            self.logExperimentEnd(time)
            # close window
            sys.exit()
        # reset input count in each round
        self.inputCount = 0

    # start all timers
    def startExperimentTimer(self):
        self.experimentStartTime = datetime.datetime.now()
        self.startCharTimer()
        self.startWordTimer()
        self.startSentenceTimer()

    # save current time as char start time
    def startCharTimer(self):
        self.charStartTime = datetime.datetime.now()

    # save current time as word start time
    def startWordTimer(self):
        self.wordStartTime = datetime.datetime.now()

    # save current time as sentence start time
    def startSentenceTimer(self):
        self.sentenceStartTime = datetime.datetime.now()

    # stop experiment timer
    def stopExperimentTimer(self):
        stopTime = datetime.datetime.now()
        diff = stopTime - self.experimentStartTime
        # return difference in seconds
        return diff.total_seconds()

    # stop experiment timer
    def stopCharTimer(self):
        stopTime = datetime.datetime.now()
        diff = stopTime - self.charStartTime
        self.startCharTimer()
        # return difference in seconds
        return diff.total_seconds()

    # stop word timer
    def stopWordTimer(self):
        stopTime = datetime.datetime.now()
        diff = stopTime - self.wordStartTime
        self.startWordTimer()
        # return difference in seconds
        return diff.total_seconds()

    # stop sentence timer
    def stopSentenceTimer(self):
        stopTime = datetime.datetime.now()
        diff = stopTime - self.sentenceStartTime
        self.startSentenceTimer()
        # return difference in seconds
        return diff.total_seconds()

    # log if char was entered
    def charLog(self, time):
        # eventtype, wann, Welcher, wie lange gebraucht, ...
        char = self.editor.text()[-1:]
        print("key pressed;%s;%f;\"%s\"" % (datetime.datetime.now(), time, char))

    # log if word was finished
    def wordLog(self, time):
        # eventtype, wann, Welches, wie lange gebraucht, ...
        word = self.editor.text()[-5:]
        print("word typed;%s;%f;\"%s\"" % (datetime.datetime.now(), time, word))

    # log if sentence was finished
    def sentenceLog(self, time):
        # eventtype, wann, welcher, wie lange gebraucht, ...
        sentence = self.editor.text()
        print("sentence typed;%s;%f;\"%s\"" % (datetime.datetime.now(), time, sentence))

    # log if experiment was started
    def logExperimentStart(self):
        print("type;timestamp;time needed in ms;input")

    # log if experiment was finished
    def logExperimentEnd(self, time):
        # eventtype, wann, wie lange gebraucht, ...
        print("test finished;%s;%f;" % (datetime.datetime.now(), time))


class CompleterLineEdit(QLineEdit):

    myprefix = ""
    inputtext = ""
    mytags = ""


    def __init__(self, *args):
        QLineEdit.__init__(self, *args)
        
        self.textChanged.connect(self.text_changed)

    def text_changed(self, text):
        all_text = text
        text = all_text[:self.cursorPosition()]
        prefix = text.split(' ')[-1].strip()
        text_tags = []
        for t in all_text.split(' '):
            t1 = t.strip()
            if t1 != '':
                text_tags.append(t)
        text_tags = list(set(text_tags))
        self.mytags = text_tags
        self.myprefix = prefix
        self.inputtext = text
    
    # completes the text
    def complete_text(self, completer):
        # HIER IST DAS PROBLEM IRGENDWO...
        # resets text?
        text = ""
        # sets text to current completion
        text = completer.givecompletion()
        # gets cursor position
        cursor_pos = self.cursorPosition()
        # gets text in front of cursor
        before_text = self.text()[:cursor_pos]
        # gets text behind cursor
        after_text = self.text()[cursor_pos:]
        # gets length of prefix
        prefix_len = len(before_text.split(' ')[-1])
        print(before_text)
        print(before_text.split(","))
        print(before_text.split(" "))
        print(before_text.split(" ")[-1].strip())
        print(prefix_len)
        # sets text 
        self.setText('%s%s %s' % (before_text[:cursor_pos - prefix_len], text,
            after_text))
        # sets cursor postion 
        self.setCursorPosition(cursor_pos - prefix_len + len(text) + 1)
        text = ""


    # returns prefix
    def giveprefix(self):
        return self.myprefix

    # returns input text
    def givetext(self):
        return self.inputtext

    # returns tags
    def givetags(self):
        return self.mytags


class TagsCompleter(QCompleter):
    current_completion= ""

    # inits completer
    def __init__(self, parent, all_tags):
        # inits QCompleter
        QCompleter.__init__(self, all_tags, parent)
        # generates list from all_tags without duplicates
        self.all_tags = set(all_tags)
        # sets prefix
        self.completion_prefix = self.completionPrefix()
    
    # updates completer
    def update(self, editor):
        # gets tags (words) from editor
        text_tags = editor.givetags()
        # gets prefix (first letters) from editor
        completion_prefix = editor.giveprefix()
        # creates list of differences between all_tags and text_tags
        #tags = list(self.all_tags.difference(text_tags))
        #creates list from all_tags
        tags = self.all_tags
        # creates model as QStringList from tags
        model = QStringListModel(tags, self)
        # sets model
        self.setModel(model)
        # sets prefix
        self.setCompletionPrefix(completion_prefix)
        # sets current completion
        self.current_completion = self.currentCompletion()
        # checks if prefix is not empty
        if completion_prefix.strip() != '' and len(completion_prefix) >1:
            # completes text
            self.complete()
    
    # returns text of current completion
    def givecompletion(self):
        return self.current_completion




def main():
    app = QtWidgets.QApplication(sys.argv)
    txtInput = TextInput()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
