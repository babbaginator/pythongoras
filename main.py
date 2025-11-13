# ===============================================================
#    The Temple of Pythongoras
#    A Retro Text Adventure Game & Prototype Game Engine
#    Version 0.2
#    By Neil Aitken
# ===============================================================
#   This engine and game are based on an earlier prototype 
#   developed at UBC by Neil Aitken, Coco Chen, and Daniel Unruh
# ===============================================================
#   CHANGE LOG:
#   v0.2 - Console/output implemented with curses library (not pygame)
#   v0.1 - Console/output implemented using pygame

import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle
import time
from dice import *
from utility import *
import pyadventure as pyadv

def unused(stdscr):
    game = pyadv.game
    output = game.title
    output_log = pyadv.MessageBuffer()

    try:
        key = stdscr.getkey()
    except:
        key = None
    x,y = 0,0
    if key == curses.KEY_BACKSPACE:            
        stdscr.clear()
        x-=1            
        stdscr.addstr(x,y,'')
        stdscr.refresh()
        text = text[:-1]

    # Handle return/enter (send command)
    elif key == "\n":
        match text:
            case 'e': text = 'east'
            case 'w': text = 'west'
            case 's': text = 'south'
            case 'n': text = 'north'
            case 'u': text = 'up'
            case 'd': text = 'down'
            case 'inv': text = 'inventory'

        output = game.handle(text)                             
                                        
        if output == 'quit' or '[END]' in output:
            game_state = 'game_over'                                       
        
        if output.startswith('[DIED]'):
            output = output.replace('[DIED]','')
            game_state = 'player_death'                            

        output_log.read('\n>> '+text+"\n"+output)
        text = ''
    
    if not key == None:
        text += key 
        stdscr.clear()
        stdscr.addstr(text)
        stdscr.refresh()

def main(stdscr):
    
    stdscr.nodelay(True)
    x,y = 0,0 
    game_state = 'start_menu'
    game = pyadv.game

    output = game.title
    output_log = pyadv.MessageBuffer()

    cmdwindow = curses.newwin(4,20,10,10)

    x,y = 0,0
    text = ''
    while True:
        
        try:
            key = stdscr.getkey()
            if key == curses.KEY_BACKSPACE:            
                cmdwindow.clear()
                x-=1            
                cmdwindow.delch()
                cmdwindow.refresh()
            else:
                x +=1
                cmdwindow.addch(key)
                cmdwindow.refresh()
        except:
            key = None
        

wrapper(main)