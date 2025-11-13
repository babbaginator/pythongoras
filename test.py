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

def main2(stdscr):
    counter_win = curses.newwin(1,20,10,10)
    stdscr.addstr("hello world!")
    stdscr.refresh() 

    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_YELLOW)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_WHITE)
    BLUE_AND_YELLOW = curses.color_pair(1)
    GREEN_AND_BLACK = curses.color_pair(2)
    RED_AND_WHITE = curses.color_pair(3)
  
    for i in range(100):
        counter_win.clear()
        color = BLUE_AND_YELLOW
        if i%2 == 0:
            color = GREEN_AND_BLACK
        counter_win.addstr(f"Count: {i}",color)
        counter_win.refresh()
        time.sleep(0.1)
    
    stdscr.getch()

def main3(stdscr):
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_YELLOW)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_WHITE)
    BLUE_AND_YELLOW = curses.color_pair(1)
    GREEN_AND_BLACK = curses.color_pair(2)
    RED_AND_WHITE = curses.color_pair(3)
    SCR_LINES = curses.LINES-1
    SCR_COLS = curses.COLS-1

    pad = curses.newpad(100,100)
    stdscr.refresh()

    for i in range(100):
        for j in range(26):
            char = chr(65+j)
            pad.addstr(char, GREEN_AND_BLACK)

    for i in range(100):
        stdscr.clear()
        stdscr.refresh()
        pad.refresh(i, 0, 0, 0, 20, 20)
        time.sleep(0.2)
    stdscr.getch()

def main4(stdscr):
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_YELLOW)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_WHITE)
    BLUE_AND_YELLOW = curses.color_pair(1)
    GREEN_AND_BLACK = curses.color_pair(2)
    RED_AND_WHITE = curses.color_pair(3)
    SCR_LINES = curses.LINES-1
    SCR_COLS = curses.COLS-1

    stdscr.nodelay(True)
    string_x = 0
    x,  y = 0, 0 
    while True:
        

        try:
            key = stdscr.getkey()
        except:
            key = None
        
        if key == "KEY_LEFT":
            x -= 1
        elif key == "KEY_RIGHT":
            x += 1
        elif key == "KEY_UP":
            y -= 1
        elif key == "KEY_DOWN":
            y += 1
        stdscr.clear()

        
        string_x += 1
        stdscr.addstr(0, string_x//50, "hello world")

        stdscr.addstr(y,x,"0")
        stdscr.refresh()
        

def main(stdscr):
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_YELLOW)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_WHITE)
    BLUE_AND_YELLOW = curses.color_pair(1)
    GREEN_AND_BLACK = curses.color_pair(2)
    RED_AND_WHITE = curses.color_pair(3)
    SCR_LINES = curses.LINES-1
    SCR_COLS = curses.COLS-1
    curses.echo()

    stdscr.attron(RED_AND_WHITE)
    stdscr.border()
    stdscr.attroff(RED_AND_WHITE)

    stdscr.attron(GREEN_AND_BLACK)     
    rectangle(stdscr,1,1,5,20)
    stdscr.attroff(GREEN_AND_BLACK)     
    stdscr.addstr(5,30,"Hello world")

    stdscr.move(10,20) # move the cursor

    stdscr.refresh()    
    while True:
        key = stdscr.getkey()
        if key == "q":
            break


wrapper(main)