# ===============================================================
#    The Temple of Pythongoras
#    A Retro Text Adventure Game & Prototype Game Engine
#    Version 0.1
#    By Neil Aitken
# ===============================================================
#   This engine and game are based on an earlier prototype 
#   developed at UBC by Neil Aitken, Coco Chen, and Daniel Unruh
# ===============================================================

import os
import sys

colors = {}
colors['white'] = (255,255,255)
colors['black'] = (0,0,0)
colors['output'] = (222,211,190)
colors['bgout'] = (77,77,77)
colors['gold'] = (255,215,0)
colors['blue'] = (30,144,255)
colors['red'] = (181,9,38)
colors['purple'] = (161,23,177)

WINDOW_WIDTH = 800  
WINDOW_HEIGHT = 600

FONT_SIZE_1 = int(WINDOW_HEIGHT/37)     #16
FONT_SIZE_2 = int(WINDOW_HEIGHT/33)     #18
FONT_SIZE_3 = int(WINDOW_HEIGHT/15)     #40

TXT_COLOR = colors['white']
BG_COLOR = colors['black']

bg_output = colors['bgout']

lines_out = []

# Main Game Code
from utility import *   #Include a set of general purpose ease-of-life functions
import pygame 
import pyadventure as pyadv


def add_line(text,x,y,font,color=colors['output']):        
    text_surface = font.render(text,True,color)
    rect = text_surface.get_rect()
    rect.topleft = (x,y)
    lines_out.append((text_surface,rect))


def blit_surfaces(screen,color,surfacelist,code):
    for surface in surfacelist:
        pygame.draw.rect(screen,color,surface,code)  

def display_start_screen(screen,text,desc,font,subfont):
    screen.fill(colors['black'])        
    titlefont = pygame.font.Font(pyadv.resource_path(font),FONT_SIZE_3)
    title = titlefont.render(text,True,colors['gold'])
    descfont = pygame.font.Font(pyadv.resource_path(font),FONT_SIZE_1)
    gamedesc = descfont.render(desc,True,colors['white'])
    subtitlefont = pygame.font.Font(pyadv.resource_path(subfont),FONT_SIZE_2)
    start_button = subtitlefont.render('Press spacebar to start',True,colors['white'])
    screen.blit(title, (WINDOW_WIDTH/2 - title.get_width()/2, WINDOW_HEIGHT/2 - title.get_height()/2))
    screen.blit(start_button, (WINDOW_WIDTH/2 - start_button.get_width()/2, WINDOW_HEIGHT/2  + title.get_height()))
    screen.blit(gamedesc,(WINDOW_WIDTH/2 - gamedesc.get_width()/2,WINDOW_HEIGHT/2 -start_button.get_height()+ 3*title.get_height()))
    
    pygame.display.update()

def display_end_screen(screen,font,subfont):
    screen.fill(colors['black'])    
    titlefont = pygame.font.Font(pyadv.resource_path(font),FONT_SIZE_3)
    subtitlefont = pygame.font.Font(pyadv.resource_path(subfont),FONT_SIZE_2)
    title = titlefont.render('Game Over',True,colors['white'])
    start_button = subtitlefont.render('Restart? (Y/N)',True,colors['white'])
    screen.blit(title, (WINDOW_WIDTH/2 - title.get_width()/2, WINDOW_HEIGHT/2 - title.get_height()/2))
    screen.blit(start_button, (WINDOW_WIDTH/2 - start_button.get_width()/2, WINDOW_HEIGHT/2 + start_button.get_height()*2))
    pygame.display.update()

def display_win_screen(screen,font,subfont):
    screen.fill(colors['black'])    
    titlefont = pygame.font.Font(pyadv.resource_path(font),FONT_SIZE_3)
    subtitlefont = pygame.font.Font(pyadv.resource_path(subfont),FONT_SIZE_2)
    title = titlefont.render('You escaped the Temple of Pythongoras!',True,colors['white'])
    start_button = subtitlefont.render('Play again? (Y/N)',True,colors['white'])
    screen.blit(title, (WINDOW_WIDTH/2 - title.get_width()/2, WINDOW_HEIGHT/2 - title.get_height()/2))
    screen.blit(start_button, (WINDOW_WIDTH/2 - start_button.get_width()/2, WINDOW_HEIGHT/2 + start_button.get_height()*2))
    pygame.display.update()

# ======================================================
# MAIN GAME LOOP
# ======================================================

def main():    
    import time
    pygame.init()
    game_state = 'start_menu'
    game = pyadv.game
         
    #screen = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT),pygame.FULLSCREEN)
    #screen = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
    screen = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT),pygame.SCALED|pygame.FULLSCREEN)
    caption =  game.title
    pygame.display.set_caption(caption)
    
    # Set up command line prompt
    prompt = '>> '      # marker for command line
    text = ''           # initial text in the command line
    #fontsize = game.fontsize
    #outfontsize = game.displayfontsize    
    
    fontsize = FONT_SIZE_1
    outfontsize = FONT_SIZE_2
    
    font = pygame.font.Font(pyadv.resource_path(game.font),fontsize)   # set font to system font, font-size 25
    outfont = pygame.font.Font(pyadv.resource_path(game.displayfont),outfontsize)    
    critfont = pygame.font.Font(pyadv.resource_path(game.criticalfont),outfontsize+2)

    output = game.title
    output_log = pyadv.MessageBuffer()

    charheight = font.size('gH')[1]    
    charwidth = font.size('z')[0]
    lineheight = charheight

    outcharheight = outfont.size('gH')[1]
    outcharwidth = outfont.size('z')[0]
    outlineheight = outcharheight

    CMD_HEIGHT = lineheight*3
    CMD_WIDTH = WINDOW_WIDTH

    COMMAND_X = 0
    COMMAND_Y = WINDOW_HEIGHT - CMD_HEIGHT - 2*lineheight -3
    
    NUM_DISPLAY_LINES = int((WINDOW_HEIGHT-CMD_HEIGHT)/outlineheight)

    SCROLL_DIRECTION =  -1           # Use 1 for scroll from the top, -1 for scroll from the bottom

    OUTPUT_X = COMMAND_X
    OUTPUT_Y = outlineheight*3
    OUTPUT_HEIGHT = NUM_DISPLAY_LINES*outlineheight-CMD_HEIGHT - 2*charheight
    OUTPUT_WIDTH = WINDOW_WIDTH
    OUTPUT_BOTTOM_Y = OUTPUT_Y        

    HISTORY_X = OUTPUT_X+OUTPUT_WIDTH
    HISTORY_Y = 3*outlineheight          
    HISTORY_WIDTH = CMD_WIDTH - OUTPUT_WIDTH 
    HISTORY_HEIGHT = OUTPUT_HEIGHT
    HISTORY_BOTTOM_Y = OUTPUT_HEIGHT+outlineheight

    NUM_CHAR = int(OUTPUT_WIDTH/outcharwidth)-1
      
    # Set up text as img to use RGB white (255,255,255) and render (display) it
    cmd_text = font.render(text,True, TXT_COLOR) 
    
    # Create a rectangle with top left coordinates (x,y) and put the cursor (a rectangle) at coordinates at the end of the line.
    rect = cmd_text.get_rect()
    rect.topleft = (COMMAND_X+charwidth*2,COMMAND_Y+charheight)
    cursor = pygame.Rect(rect.topright, (3,rect.height))

    # Display the command line marker 
    cmd_text = font.render(prompt,True,colors['white'])
    rect.size = cmd_text.get_size()
    
    # Draw output background

    screenoutrect = pygame.Rect(OUTPUT_X,OUTPUT_Y,OUTPUT_WIDTH,OUTPUT_HEIGHT)
    cmdline_rect = pygame.Rect(COMMAND_X,COMMAND_Y,CMD_WIDTH,CMD_HEIGHT)
    #last_command_rect = pygame.Rect(HISTORY_X,HISTORY_Y,HISTORY_WIDTH,HISTORY_HEIGHT)
    game_label_rect = pygame.Rect(OUTPUT_X,OUTPUT_Y-outfontsize+5,50*charwidth,outfontsize+10)

    #surfaces = [screenoutrect,cmdline_rect,last_command_rect]    
    surfaces = [screenoutrect,cmdline_rect]    

    cursor.topleft = rect.topright    # update cursor location to be at the end of the line
    pygame.display.flip()             # display.flip() is the command to show the screen to the user
    
    # Screen update loop 
    running = True
    start_room_shown = False
    while running:
        for event in pygame.event.get():

            # The display window is closed (exited)
            if event.type == pygame.QUIT:
                running = False

            # Start screen
            if game_state == 'start_menu':
                display_start_screen(screen,game.title,game.desc,game.titlefont,game.font)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:                    
                    game_state = 'game'                                        
            
            # Game End screen
            if game_state == 'game_over' or game_state == 'player_death':
                if game.game_won == False:
                    display_end_screen(screen,game.titlefont,game.font)
                else:
                    display_win_screen(screen,game.titlefont,game.font)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        game.reset_game_environment()
                        game_state = 'start_menu'
                    elif event.key == pygame.K_n:
                        pygame.quit()
                        sys.exit()
                        return
                        
            # Game mode
            if game_state == 'game':
                if not start_room_shown:
                    output = game.player.current_room.describe()
                    output_log.read(output)
                    start_room_shown = True
                    
                    # Print game name at the top of the screen
                    label_font = pygame.font.Font(pyadv.resource_path(game.displayfont),outfontsize+4)   
                    game_name = label_font.render(game.title,True,colors['gold'])
                    game_label_rect = game_name.get_rect()
                    game_label_rect.topleft = (OUTPUT_X,outfontsize+4)

                    # Create a list from the string and render it to surfaces
                    lines_out.clear()                
                    paragraphs = output_log.log
                    i = 0
                    
                    # Convert output into a paragraph format that fits the output width
                    lines = get_multiline_from_list(paragraphs,NUM_CHAR)
                    
                    for line in lines:                        
                        if line.startswith('>> '):
                            line = line.replace('>> ','')
                            add_line(line,COMMAND_X+charwidth*3,OUTPUT_BOTTOM_Y+i*lineheight+charheight,outfont,colors['blue'])
                        #elif line.startswith('[['):
                        #    line = line.replace('[[','')
                        #    add_line(line,COMMAND_X+charwidth*3,OUTPUT_BOTTOM_Y+i*lineheight+charheight,outfont,colors['red'])
                        elif line.startswith('<<'):
                            line = line.replace('<<','')
                            line = line.replace('>>','')
                            add_line(line,COMMAND_X+charwidth*3,OUTPUT_BOTTOM_Y+i*lineheight+charheight,outfont,colors['gold'])
                        #elif line.startswith('**'):
                        #    line = line.replace('**','')
                        #    add_line(line,COMMAND_X+charwidth*3,OUTPUT_BOTTOM_Y+i*lineheight+charheight,outfont,colors['purple'])
                        #elif line.startswith('[CRIT]'):
                        #    line = line.replace('[CRIT]','')
                        #    add_line(line,COMMAND_X+charwidth*3,OUTPUT_BOTTOM_Y+i*lineheight+charheight,critfont,colors['purple'])
                        else:
                            add_line(line,COMMAND_X+charwidth*3,OUTPUT_BOTTOM_Y+i*lineheight+charheight,outfont)
                        i+=1

                    # Fill background and refresh screen
                    screen.fill(BG_COLOR)
                    screen.blit(cmd_text,rect)
                    screen.blit(game_name,game_label_rect)
                    
                    blit_surfaces(screen,colors['white'],surfaces,3)
                    
                    # Draw text
                    if len(lines_out)>0:
                        for txt_surf, txt_rect in lines_out:
                            screen.blit(txt_surf, txt_rect) 

                    
                    # Draw blinking cursor
                    if time.time() %1 > 0.5:
                        pygame.draw.rect(screen,colors['white'], cursor)
                    
                    pygame.display.update()
                    continue

            # A key is pressed down, check to see how to handle it                
                if event.type == pygame.KEYDOWN:
                    # Handle backspace
                    if event.key == pygame.K_BACKSPACE:
                        if len(text) > 0:
                            text = text[:-1]

                    # Handle return/enter (send command)
                    elif event.key == pygame.K_RETURN:
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
                    else:
                        text += event.unicode
        
                    # Print command in the command line
                    cmd_text = font.render(prompt+text,True,colors['white'])
                    rect.size = cmd_text.get_size()
                    cursor.topleft = rect.topright

                    # Print game name at the top of the screen
                    label_font = pygame.font.Font(pyadv.resource_path(game.displayfont),outfontsize+4)   
                    game_name = label_font.render(game.title,True,colors['gold'])
                    game_label_rect = game_name.get_rect()
                    game_label_rect.topleft = (OUTPUT_X,outfontsize+4)

                    # Create a list from the string and render it to surfaces
                    lines_out.clear()                     
                    paragraphs = output_log.log
                    i = 0
                    
                    # Convert output into a paragraph format that fits the output width
                    lines = get_multiline_from_list(paragraphs,NUM_CHAR)

                    lines = game.get_output(lines,15)
                    
                    for line in lines:                        
                        if line.startswith('>> '):
                            line = line.replace('>> ','')
                            add_line(line,COMMAND_X+charwidth*3,OUTPUT_BOTTOM_Y+i*lineheight+charheight,outfont,colors['blue'])
                        elif line.startswith('<<'):
                            line = line.replace('<<','')
                            line = line.replace('>>','')
                            add_line(line,COMMAND_X+charwidth*3,OUTPUT_BOTTOM_Y+i*lineheight+charheight,outfont,colors['gold'])
                        elif line.startswith('[['):
                            line = line.replace('[[','')
                            add_line(line,COMMAND_X+charwidth*3,OUTPUT_BOTTOM_Y+i*lineheight+charheight,outfont,colors['red'])
                        elif line.startswith('**'):
                            line = line.replace('**','')
                            add_line(line,COMMAND_X+charwidth*3,OUTPUT_BOTTOM_Y+i*lineheight+charheight,outfont,colors['purple'])
                        elif line.startswith('[CRIT]'):
                            line = line.replace('[CRIT]','')
                            add_line(line,COMMAND_X+charwidth*3,OUTPUT_BOTTOM_Y+i*lineheight+charheight,critfont,colors['purple'])
                        elif line.startswith('[READ]'):
                            line = line.replace('[READ]','')
                            add_line(line,COMMAND_X+charwidth*3,OUTPUT_BOTTOM_Y+i*lineheight+charheight,outfont,colors['gold'])
                        else:
                            add_line(line,COMMAND_X+charwidth*3,OUTPUT_BOTTOM_Y+i*lineheight+charheight,outfont)
                        i+=1
                    
                    # Convert command history into lines
                    #history = game.get(NUM_DISPLAY_LINES)
                    #cmds = history.split('\n')
                    
                    #i = 0
                    #for cmd in cmds:
                    #    if len(cmd.strip())>0 and HISTORY_BOTTOM_Y+SCROLL_DIRECTION*i*lineheight > HISTORY_Y:                        
                    #        add_line(prompt+cmd,HISTORY_X+charwidth,HISTORY_BOTTOM_Y+SCROLL_DIRECTION*i*lineheight,font)
                    #        i+=1
                
                    # Fill background and refresh screen
                    screen.fill(BG_COLOR)
                    screen.blit(cmd_text,rect)
                    screen.blit(game_name,game_label_rect)
                    
                    blit_surfaces(screen,colors['white'],surfaces,3)
                    
                    # Draw text
                    if len(lines_out)>0:
                        for txt_surf, txt_rect in lines_out:
                            screen.blit(txt_surf, txt_rect) 

                    
                    # Draw blinking cursor
                    if time.time() %1 > 0.5:
                        pygame.draw.rect(screen,colors['white'], cursor)

        
        pygame.display.update()


if __name__ == "__main__":
    main()

