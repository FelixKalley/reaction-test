import sys
 
from PyQt5 import Qt, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QLineEdit, QCompleter
from PyQt5.QtCore import QStringListModel, pyqtSignal, QObject
 
TAGS = ['Nature', 'buildings', 'home', 'City', 'country', 'Berlin']
 
class CompleterLineEdit(QLineEdit):
    mylist = ['Nature', 'buildings', 'home', 'City', 'country', 'Berlin']
    myprefix = ""
    inputtext = ""
    mytags = ""

    def __init__(self, *args):
        QLineEdit.__init__(self, *args)
        
        self.textChanged.connect(self.text_changed)

    def text_changed(self, text):
        all_text = text
        text = all_text[:self.cursorPosition()]
        prefix = text.split(',')[-1].strip()
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
        prefix_len = len(before_text.split(',')[-1].strip())
        # sets text 
        self.setText('%s%s, %s' % (before_text[:cursor_pos - prefix_len], text,
            after_text))
        # sets cursor postion 
        self.setCursorPosition(cursor_pos - prefix_len + len(text) + 1)
        text = ""

    # returns wordlist
    def givelist(self):
        return self.mylist

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
        tags = list(self.all_tags.difference(text_tags))
        #creates list from all_tags
        #tags = self.all_tags
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

# main
def main():
    # application
    app = QApplication(sys.argv)
    # special QLineEdit
    editor = CompleterLineEdit()
    # special Completer
    completer = TagsCompleter(editor, TAGS)
    # disables case sensitivity
    completer.setCaseSensitivity(False)
    # connects activation of completer with editor function complete_text
    completer.activated.connect(lambda: editor.complete_text(completer))
    # connects change of text in editor with completer function update
    editor.textChanged.connect(lambda: completer.update(editor))
    # sets widget for completer
    completer.setWidget(editor)
    # shows editor
    editor.show()
    # executes app
    return app.exec_()
 
if __name__ == '__main__':
    main()