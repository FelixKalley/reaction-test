#!/usr/bin/env python3

import wiimote
import time
import sys
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication

class WiimoteGame(object):

    ''' map of the game:

                7             
                |
             6--1--2
             |     |
             5  4--3
    
    Lines (| or --) indicate where you can go to 
    1 = starting room
    2 = old man (sword)
    3 = flute
    4 = shield
    5 = armor
    6 = potion
    7 = dragon
    '''
    def __init__(self):            
        # order of doors in rooms: north, east, south, west. 0 = no door, 1 = door
        self.doors_in_rooms = [[1, 1, 0, 1],
                               [0, 0, 1, 1],
                               [1, 0, 0, 1],
                               [0, 1, 0, 0],
                               [1, 0, 0, 0],
                               [0, 1, 1, 0],
                               [0, 0, 0, 0]]
        self.current_room = 1
        self.armor = False
        self.weapon = False
        self.shield = False
        self.flute = False
        self.potion = False
        self.game_start = True
        self.met_old_man = False
        self.played_song = False

        input("Press the 'sync' button on the back of your Wiimote Plus " +
              "or buttons (1) and (2) on your classic Wiimote.\n" +
              "Press <return> once the Wiimote's LEDs start blinking.")

        if len(sys.argv) == 1:
            addr, name = wiimote.find()[0]
        elif len(sys.argv) == 2:
            addr = sys.argv[1]
            name = None
        elif len(sys.argv) == 3:
            addr, name = sys.argv[1:3]
            print(("Connecting to %s (%s)" % (name, addr)))
        self.wm = wiimote.connect(addr, name)
        self.wm.speaker.beep()
        time.sleep(0.05)
        self.wm.speaker.beep()
        time.sleep(0.05)
        self.wm.speaker.beep()
        time.sleep(0.05)

        # logo created with http://www.network-science.de/ascii/
        print("///////////////////////////////////////////////////////\n"
              "______                                                 \n"
              "|  __ \                                                \n"
              "| |  | |  _ __    __ _    __ _    ___    _ __          \n"
              "| |  | | | '__|  / _` |  / _` |  / _ \  | '_ \         \n"
              "| |__| | | |    | (_| | | (_| | | (_) | | | | |        \n"
              "|_____/  |_|     \__,_|  \__, |  \___/  |_| |_|        \n"
              "______                    __/ |                        \n"
              "|  __ \                  |___/                         \n"
              "| |  | |  _   _   _ __     __ _    ___    ___    _ __  \n"
              "| |  | | | | | | | '_ \   / _` |  / _ \  / _ \  | '_ \ \n"
              "| |__| | | |_| | | | | | | (_| | |  __/ | (_) | | | | |\n"
              "|_____/   \__,_| |_| |_|  \__, |  \___|  \___/  |_| |_|\n"
              "                           __/ |                       \n"
              "                          |___/                        \n"
              "                                                       \n"
              "///////////////////////////////////////////////////////\n")
        print("A stdout text adventure for wiimote! \n"
              "Press \"Home\" to explore. Move around with the D-Pad. Press \"1\" for help.\n")

        while True:
            if self.wm.buttons["Up"]:
                self.go_north()
                time.sleep(0.5)
            if self.wm.buttons["Down"]:
                self.go_south()
                time.sleep(0.5)
            if self.wm.buttons["Right"]:
                self.go_east()
                time.sleep(0.5)
            if self.wm.buttons["Left"]:
                self.go_west()
                time.sleep(0.5)
            if self.wm.buttons["A"]:
                self.attack()
                time.sleep(0.5)
            if self.wm.buttons["B"]:
                self.block()
                time.sleep(0.5)
            if self.wm.buttons["Minus"]:
                self.use_potion()
                time.sleep(0.5)
            if self.wm.buttons["Home"]:
                self.inspect()
                time.sleep(0.5)
            if self.wm.buttons["Plus"]:
                self.use_flute()
                time.sleep(0.5)
            if self.wm.buttons["One"]:
                self.help_menu()
                time.sleep(0.5)
            if self.wm.buttons["Two"]:
                print("You quit your dragon slaying hobby for today. \n" \
                      "Now back to work!")
                sys.exit()


    def go_north(self):
        print("\n")
        if self.current_room == 1:
            print("You go north!\n" \
                  "The huge door closes behind you!")
            self.current_room = 7
        elif self.current_room == 3:
            print("You go north!")
            self.current_room = 2
        elif self.current_room == 5:
            print("You go north!")
            self.current_room = 6
        else:
            print("You bang your head against a wall!\n" \
                  "Your head is hard, but so is that wall...")

    def go_south(self):
        print("\n")        
        if self.current_room == 2:
            print("You go south!")
            self.current_room = 3
        elif self.current_room == 6:
            print("You go south!")
            self.current_room = 5
        elif self.current_room == 7:
            print("You are trapped!")
        else:
            print("You cannot go there!\n" \
                  "Seriously... You can't.")

    def go_east(self):
        print("\n")
        if self.current_room == 1:
            print("You go east!")
            self.current_room = 2
        elif self.current_room == 4:
            print("You go east!")
            self.current_room = 3
        elif self.current_room == 6:
            print("You go east!")
            self.current_room = 1
        else:
            print("There is no door!\n" \
                  "And there will never be a door!")

    def go_west(self):
        print("\n")
        if self.current_room == 1:
            print("You go west!")
            self.current_room = 6
        elif self.current_room == 2:
            print("You go west!")
            self.current_room = 1
        elif self.current_room == 3:
            print("You go west!")
            self.current_room = 4
        else:
            print("This is a wall, not a door.\n"
                  "If you want to walk through walls try other games!")


    def attack(self):
        if self.current_room == 7:
            print("You hit the dragon!")
        elif self.current_room == 2:
            print("You hit the old man!")
        elif self.current_room == 4:
        	if not self.sword:
        		"You hit the skeleton.\n"
        		"The shield wiggles in his hands, but you cannot get it loose."
        	if self.sword:
        		"You crush the skeleton's bones with your mythical sword.\n"
        		"With a loud metallic rattle, the shield drops on the ground.\n"
        		"You pick it up and feel safely guarded!"
        		"Press \"B\" to block incoming attacks."
        else:
            print("You attack fiercely, but...\n" \
                  "You look pretty weird hitting nothing")
        #print("\n")

    def block(self):
        if self.current_room == 7:
            print("You block the attack!")
        else:
            print("You focus all your last energy on blocking an attack...\n" \
                  "But there is no one who attacks you.")
        #print("\n")

    def use_potion(self):
        if self.potion:
            print("That magical potion increases your strength!")
        else:
            print("It would be nice to have something to drink.")
        #print("\n")

    def use_flute(self):
        if self.flute:
            print("You play a beautiful song...")
            self.wm.speaker.beep()
            time.sleep(0.05)
            self.wm.speaker.beep()
            time.sleep(0.05)
            self.wm.speaker.beep()
            time.sleep(0.05)
            if self.current_room == 2:
                print("The old man smiles joyfully.\n"
                  "\"Use this wisely, hero!\", are his very last words, as he leaves his mystic sword to you.")
                self.played_song = True;
            self.sword = True;
        else:
            print("You make a weird sound...")
            self.wm.speaker.beep()
            time.sleep(0.05)
            if self.current_room == 2:
                print("\"That's not a song I like.\", the old man grumbles.")
        #print("\n")

    def inspect(self):
        if self.current_room == 1:
            if self.game_start:
                print("\"How did I get here?,\" you think to yourself.\n"
                  "You seem to have lost your memories.\n"
                  "And your only belongings are the cloth you wear.\n"
                  "It's pretty dark around you, but you seem to be in a big room.\n"
                  "Let's just call this room \"Room 1\".\n"
                  "You can see three doors, one in the north, one in the east and one in the west.\n"
                  "But the one in the north is huge compared to the two doors.")
                self.game_start = False
            else:
                print("Room 1: \n"
                      "This is where you started.")
        elif self.current_room == 2:
            if not self.met_old_man:
                print("Room 2:"
                      "\"Who's there?\", a weak voice whispers.\n"
                      "You can spot an old man in the shadows.\n"
                      "\"Are you the hero of this game?\", he mutters.\n"
                      "\"I don't know\", you answer.\n"
                      "\"Nevermind...\", the old man says. \"I don't have much life in me."
                      "If you fulfill my last wish, you will become a hero. So please, play a song for me!\"\n"
                      "Press the \"+\"-Button to try to play a song.")
                self.met_old_man = True
            else:
                if not self.played_song:
                    print("Room 2: \n"
                          "The old man is still waiting for a song.")
                else:
                    print("Room 2: \n"
                          "The dead old man smiles peacefully.\n"
                          "Nothing else is of note here.")

        elif self.current_room == 3:
            if not self.flute:
                print("Room 3:\n"
                      "There is nothing special in this room.\n"
                      "Only a table with a... a flute!\n"
                      "Now you can surely play a nice song!\n"
                      "Press the \"+\"-Button to try to play a song.")
                self.flute = True
            else:
            	print("Room 3: \n"
            		  "There is nothing special in this room anymore.")
        elif self.current_room == 4:
            if not self.shield:
            print("Room 4:\n"
            	  "A skeleton is chained to the ceiling. \n"
            	  "Its bony fingers are clinging to a huge shield.\n"
            	  "This could be of prime importance for your further adventures.")
            if self.shield:
            	print("A skeleton is chained to the ceiling... \n"
            		  "With only one hand.")
        elif self.current_room == 5:
            print("Room 5:")
        elif self.current_room == 6:
            print("Room 6:")
        elif self.current_room == 7:
            print("Room 7:")
        else:
            pass
        self.report_doors(self.current_room)
        #print("\n")

    def report_doors(self, room_number):
        possible_doors = self.doors_in_rooms[room_number-1]
        if possible_doors[0]:
            print("You see a door in the north!")
        if possible_doors[1]:
            print("You see a door in the east!")
        if possible_doors[2]:
            print("You see a door in the south!")
        if possible_doors[3]:
            print("You see a door in the west!")

    def help_menu(self):
    	print("\n"
    		  "#######\n"
    		  "# How to play:\n"
    		  "# D-Pad:          Move through doors\n"
    		  "# A-Button:       Attack\n"
    		  "# B-Button:       Block\n"
    		  "# Minus-Button:   Use Potion\n"
    		  "# Home-Button:    Explore your surroundings\n"
    		  "# Plus-Button:    Play a Song\n"
    		  "# One-Button:     Show Controls\n"
    		  "# Two-Button:     Quit Game\n"
    		  "#######\n")

# main
def main():
    # initializes app
    # initializes app
    app = QtWidgets.QApplication(sys.argv)
    # initializes experiment
    game = WiimoteGame()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

