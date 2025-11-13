# LIBR 559 - Final Project
# The Temple of Pythongoras
# A Retro Text Adventure Game & Prototype Game Engine
#
# Created by Group 6: Coco, Daniel, Neil
# Summer 2024
# =================================================

# Main Game Code
from utility import *
from dialog import*
import os
import re

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    import sys
    if hasattr(sys,'_MEIPASS'):
        return os.path.join(sys._MEIPASS,os.path.join(ASSETS_DIR,relative_path))
    return os.path.join(ASSETS_DIR, relative_path)

# ==========================================================================
# MESSAGE_BUFFER - Holds all output before sending it to the console/display
# ==========================================================================
class MessageBuffer:
    def __init__(self):
        self.log = []
    
    def add(self,msg:str):   
        if not msg == None:          
            self.log.append(msg)        
    
    def read(self,output):
        lines = output.split('\n')
        for line in lines:
            self.add(line)

    def send(self):
        if len(self.log) == 0:
            return ''
        else:
            msg = '\n'.join(self.log)
            return msg
    
    def dump(self):
        for cmd in self.log:
            print(f'BUFFER: {cmd}')

# ================================================================
# ITEM - Basic building block of other items and game objects
# ================================================================
class Item:
    def __init__(self,name):  
        self.id = name      
        self.name = name
        self.weight = 0
        self.in_use = False
        self.attributes = []
        
        filename = os.path.join('data','items',self.id.replace(' ','_')+'.txt')
        self.load(filename)
    
    # Load specific item configuration details from external txt file
    def load(self,filename):
        try:
            lines = open(resource_path(filename),'r')
            for line in lines:
                if not line.startswith('#') and not line=='\n':  # Ignore comments and empty lines
                    key, value = line.split('=')                
                    value = value.strip()

                    # Depending on the key, read the value as a list, integer, or string
                    match key:
                        case 'attributes'|'spells'|'contents'|'read_text':
                            setattr(self,key.strip(),value.split(','))                
                        case 'HP'|'to_hit'|'damage'|'break_HP':
                            setattr(self, key.strip(),int(value))
                        case _:
                            setattr(self, key.strip(),value) 
        except:
            print(f'File read error: {filename} does not exist')            

    # Reset item back to its initial values
    def reset(self):
        self.__init__(self.id)

    # Check if quality is in the objects attributes list (attributes are like metatags or flags)
    def isType(self,quality):
        if quality in self.attributes:
            return True
        return False   
    
    # Check if the item is of a particular kind (item,container,lockbox,etc)
    def isKind(self,kind):
        if 'kind' in vars(self):
            return self.kind == kind
        return False
    
    # Have item return its description
    def describe(self):
        desc = ''
        if 'describe_text' in vars(self):
            desc = self.describe_text
        elif 'description' in vars(self):           
            desc = self.description
        elif 'read_text' in vars(self):
            desc = "There's something written here.\n"+self.read()
        else:
            desc = self.name+" looks pretty ordinary"
        
        if self.in_use:
            desc = desc +"\n"+self.active_text
        
        return desc
    
    # Read readable item
    def read(self):
        desc = ''
        if 'read_text' in vars(self):
            desc = choose(self.read_text)
        return desc

    # Displays active text for a light source if it is on
    def shine(self):
        if self.in_use and self.isType('lightable'):
            return self.active_text
        else:
            return choose(["The darkness presses in on you","It's pretty dark in here.","You can't see much more without more light","The darkness is overwhelming","The darkness is less of an old friend and more like a nosey neighbor who won't leave you alone."])
            
    
    # Toggle an item field between True and False  
    def toggle(self,key):
        if key in vars(self):
            value = getattr(self,key)
            if isinstance(value,str):
                if value.lower() == 'false':
                    value = 'TRUE'
                else:
                    value = 'FALSE'
            elif isinstance(value,bool):
                value = not value
            else:
                return
            setattr(self,key,value)

    # Return a string summarizing the item's contents. For the base Item, this is just a placeholder method.
    def spill(self):
        return ''

    # If the item is readable, return a line read from the list of possible strings
    def get_line(self):
        if self.isType('readable'):
            return choose(self.read_text)
    
    # Object script handler - interprets short strings of commands and performs actions, changes, and interactions
    def parse(self,cmdscript):
        buffer = MessageBuffer()
        lines = cmdscript.split(';')
        for line in lines:
            args = line.strip().split(' ')
            cmd = args.pop(0)            
            
            match cmd:
                # set a field to an integer, string, or the contents of another field
                case 'set':
                    key = args[0]
                    if args[1] == 'to':
                        setattr(self,key,getattr(self,args[2]))                        
                    elif (args[1].isdigit()==True):
                        value = int(args[1])
                        setattr(self,key,value)
                    else:
                        value = args[1]
                        setattr(self,key,value)                    
                
                case 'toggle':
                    key = args[0]
                    if key in vars(self):
                        self.toggle(key)
                    elif key in vars(game.player):
                        game.player.toggle(key)
                    elif key in vars(game.player.current_room):
                        game.player.current_room.toggle(key)
                    else:
                        value = int(args[1])
                        setattr(self,key,value)
                
                # increment a particular field in this item, the game.player, or the current room by a given amount. 
                case 'add':
                    key = args[0]                    
                    if key in vars(self):
                        value = getattr(self,key) + int(args[1])
                        setattr(self,key,value)
                    elif key in vars(game.player):
                        value = getattr(game.player,key) + int(args[1])
                        setattr(game.player,key,value)                        
                    elif key in vars(game.player.current_room):
                        value = getattr(game.player.current_room,key) + int(args[1])
                        setattr(game.player.current_room,key,value)                        
                    else:
                        value = int(args[1])
                        setattr(self,key,value)
                
                # decrement a particular field in this item, the game.player, or the current room by a given amount
                case 'sub':
                    key = args[0]
                    if key in vars(self):
                        value = getattr(self,key) - int(args[1])
                        setattr(self,key,value)
                    elif key== 'game.player':
                        value = getattr(game.player,args[1]) - int(args[2])
                        setattr(game.player,args[1],value)                        
                    elif key in vars(game.player):
                        value = getattr(game.player,key) - int(args[1])
                        setattr(game.player,key,value)                        
                    elif key == 'here':
                        value = getattr(game.player.current_room,args[1]) - int(args[2])
                        setattr(game.player.current_room,args[1],value)
                        
                    elif key in vars(game.player.current_room):
                        value = getattr(game.player.current_room,key) - int(args[1])
                        setattr(game.player.current_room,key,value)
                        
                    else:
                        value = int(args[1])
                        setattr(self,key,value)
                
                # append the value to a given list in this item, the game.player, or the room
                case 'append':
                    key = args.pop(0)                                     
                    value = []   
                    
                    for arg in args:                        
                        value.append(arg)                       

                    if key in vars(self):
                        start_list = getattr(self,key)                        
                        setattr(self,key,value+start_list)
                    elif key in vars(game.player):
                        start_list = getattr(game.player,key)                        
                        setattr(game.player,key,value+start_list)
                    elif key in vars(game.player.current_room):
                        start_list = getattr(game.player.current_room,key)
                        setattr(game.player.current_room,key,value+start_list)
                    else:
                        setattr(self,key,value+start_list)

                # remove a value from a given list in this item, the game.player, or the current room
                case 'remove':
                    key = args[0]
                    value = []   
                    for arg in args:                        
                        value.append(arg)
                    
                    if key in vars(self):
                        value = getattr(self,key).remove(args[1])
                    elif key in vars(game.player):
                        value = getattr(game.player,key).remove(args[1])                        
                    elif key in vars(game.player.current_room):
                        value = getattr(game.player.current_room,key).remove(args[1])
                    else:
                        setattr(self,key,[])                    
                
                # add a new key to a dictionary in the item
                case 'add_key':
                    att = args.pop(0)
                    key = args.pop(0)
                    value = "".join(args)
                    try:
                        dict = getattr(self,att)
                        dict[key] = value
                    except:
                        dict = {}
                        dict[key]=value
                    setattr(self,att,dict)
                
                # increment an integer field in the game.player
                case 'boost':
                    key = args[0]
                    if key in vars(game.player):
                        value = getattr(game.player,key) + int(args[1])
                    else:
                        value = int(args[1])
                    setattr(game.player,key,value)

                # open a container or lockbox
                case 'open':
                    num = len(args)
                    match num:
                        case 0: 
                            if self.kind in ['container','lockbox']:
                                buffer.add(self.open())
                        case 1:
                            if arg[0] in game.dungeon_items.keys() and game.dungeon_items[arg[0]].kind in ['container','lockbox']:
                                buffer.add(game.dungeon_items[arg[0]].open())
                        case _:
                            print('ERROR: Too many arguments for open script')                    

                # run/interpret a provided object script                
                case 'run':
                    if len(args)>=2:
                        obj = args.pop(0)
                        objcmd = args.pop(0)      
                        if obj == "current_room" or obj == 'here':                            
                            objscript = getattr(game.player.current_room,objcmd)
                            buffer.add(game.player.current_room.parse(objscript))
                            
                        elif obj in game.monsters.keys():
                            objscript = getattr(game.monsters[obj],objcmd)
                            buffer.add(game.monsters[obj].parse(objscript))
                            
                        elif obj in game.dungeon_rooms.keys():
                            objscript = getattr(game.dungeon_rooms[obj],objcmd)
                            buffer.add(game.dungeon_rooms[obj].parse(objscript))
                            
                        elif obj in game.dungeon_items.keys():                            
                            objscript = getattr(game.dungeon_items[obj],objcmd)
                            buffer.add(game.dungeon_items[obj].parse(objscript))
                            
                        else:
                            print(f'Error: Bad script: {" ".join(args)}')
                    
                case _:
                    return buffer.send()

    # Use or activate an item - if the item has an activate or invoke effect, it will run that script and display the corresponding text
    def activate(self):
        buffer = MessageBuffer()
        if 'invoke_effect' in vars(self):            
            if self.isType('togglable'):
                buffer.add(self.parse(self.invoke_effect))
                if self.in_use:
                    buffer.add(self.invoke_text_on)
                else:
                    buffer.add(self.invoke_text_off)
            elif self.in_use:
                buffer.add("The "+self.name+" is already active.")
            else:
                self.in_use = True
                buffer.add(self.parse(self.invoke_effect))
                buffer.add(self.invoke_text)
            
            if self.isType('lightable'):
                buffer.add(game.player.current_room.describe())
            return buffer.send()
        
        if 'activate_effect' in vars(self):            
            buffer.add(self.parse(self.activate_effect))
            if self.isType('togglable'):
                if self.in_use:
                    buffer.add(self.activate_text_on)
                else:
                    buffer.add(self.activate_text_off)
            else:
                buffer.add(self.activate_text)

            if self.isType('lightable'):
                buffer.add(game.player.current_room.describe())
            return buffer.send()
        buffer.add('You attempt to use '+self.name+', but nothing happens.')
        return buffer.send()
    
    # Alias for the activate command since sometimes we find it easier to type 'item.use()'
    def use(self):
        return self.activate()

# ============================================================
# DOOR - Used for interactive doors in the environment
# ============================================================
class Door(Item):
    def __init__(self,name):
        self.kind = 'door'
        self.openstate = 'closed'
        self.lockstate = 'unlocked'
        self.attributes = ['immovable','breakable']
        Item.__init__(self,name)
    
    # Check if the door is open
    def isOpen(self):
        return self.openstate == 'open'

    # Check if the door is closed
    def isClosed(self):
        return self.openstate == 'closed'
    
    # Check if the door is locked
    def isLocked(self):
        return self.lockstate == 'locked'
    
    # Open door if closed and report if the door is locked
    def open(self):
        buffer = MessageBuffer()
        if self.isClosed():
            if not self.isLocked():
                buffer.add('You open the '+self.name+'.')
                self.openstate = 'open'
            else:
                buffer.add("You can't open it. It's locked!")
        else:
            buffer.add('The door is already open')
        return buffer.send()

    # Close door if open or report that the door is already closed
    def close(self):        
        if self.isOpen():
            return 'You close the '+self.name
            self.openstate = 'closed'
        else:
            return 'The door is already closed'

    # Lock the door if unlocked
    def lock(self):
        if self.lockstate == 'unlocked':
            self.lockstate = 'locked'
            return 'The '+self.name+' is now locked'
        else:
            return 'The '+self.name+' was already locked'
    
    # Unlock the door. Print the unlock msg and run the unlock script
    def unlock(self):
        buffer = MessageBuffer()
        if self.isLocked():
            self.lockstate = 'unlocked'
            if hasattr(self,'msg_unlock'):
                buffer.add(self.msg_unlock)
            else:
                buffer.add('The '+self.name+' is now unlocked')
            if hasattr(self,'unlock_script'):
                buffer.add(self.parse(self.unlock_script))
        else:
            buffer.add("The "+self.name+" wasn't locked")
        return buffer.send()


# =================================================================================
# WEAPON - Extends ITEM to handle weapon-related actions and interactions
# =================================================================================
class Weapon(Item):
    def __init__(self,name):
        self.category = 'blade'
        self.num_hands = 1
        self.to_hit = 0
        self.damage = 0
        self.hit_text=''
        self.miss_text=''
        self.crit_text='[CRIT]Critical Hit'
        Item.__init__(self,name)     

# ====================================================================================
# PILE - An ITEM that is a pseudo-container giving out only one item at a time
# ====================================================================================
class Pile(Item):
    def __init__(self,name):        
        self.count=1000                     # Default pile size is 1000, but can be set lower
        Item.__init__(self,name)        
        if not 'contents' in vars(self):
            self.contents = ['rock']    

    # Is the pile empty?
    def isEmpty(self):
        return self.count == 0
    
    # Does the pile contain this type of item?
    def isHolding(self,itm):
        return itm in self.contents

    # Take something from the pile (if the pile isn't empty)
    def take_one(self):
        import random
        if self.count>0:
            thing = self.contents[random.randint(0,len(self.contents))-1]
            self.count = self.count-1
        else:
            thing=''           
        return thing
    
    # Put an item back into the pile
    def return_one(self):
        self.count +=1

# ======================================================================================
# CONTAINER - Extends ITEM to be a container that holds things and has Open, Close, 
#             and Empty functionality
# ======================================================================================
class Container(Item):
    def __init__(self,name):
        self.openstate = 'closed'
        Item.__init__(self,name)        
        if not 'contents' in vars(self):
            self.contents = []    

    # Check if the container is open
    def isOpen(self):
        return self.openstate == 'open'

    # Check if the container is closed
    def isClosed(self):
        return self.openstate == 'closed'
    
    # Check if container is empty
    def isEmpty(self):
        return self.contents == []
   
    # Check if container is holding a particular item
    def isHolding(self,itm):
        return itm in self.contents

    # Return a list of contents if the container isn't empty
    def spill(self):
        value = ''
        if self.isOpen():
            if not self.isEmpty():     
                value = 'The '+self.name+' contains '+get_list_as_string(self.contents)
        return value

    # Open a closed container and display contents. If already open, just describe the contents.
    def open(self):
        buffer = MessageBuffer()
        if self.isClosed():
            buffer.add('You open the '+self.name)
            self.openstate = 'open'
            things = get_list_as_string(self.contents)
            buffer.add('Inside it you find '+things+'.')            
        else:
            buffer.add(self.describe())
        return buffer.send()
    
    # Close the container
    def close(self):
        msg = ''
        if not self.isClosed():
            msg = 'You close the '+ self.name
            self.openstate = 'closed'
        return msg
    
    # Check if container has a given item
    def has_item(self,itm):
        return itm in self.contents
    
    # Add an item to the container
    def add_item(self,itm):        
        self.contents.append(itm)
        return 'You put the '+itm+' inside the '+self.name
    
    # Remove an item to the container
    def remove_item(self,itm):
        msg = ''
        if self.has_item(itm):
            msg = 'You remove the '+ itm +' from the '+self.name
            self.contents.remove(itm)
        return msg
    
    # Describe the container and its contents (if the container is open)
    def describe(self):
        buffer = MessageBuffer()
        buffer.add(Item.describe(self))        
        if self.isEmpty():
            buffer.add("The "+self.name+" is currently empty")
        else:
            buffer.add(self.spill())
        
        return buffer.send()
        
# =============================================================================
# LOCKBOX - Extends CONTAINER to include Lock and Trapped States
# =============================================================================
class Lockbox(Container):
    def __init__(self,name):
        self.lockstate = 'unlocked'
        self.trapstate = 'untrapped'
        Container.__init__(self,name)
    
    # Check if container is locked
    def isLocked(self):
        return self.lockstate == 'locked'
    
    # Check if container is trapped
    def isTrapped(self):
        return self.trapstate == 'trapped'

    # Lock the container
    def lock(self):
        msg = ''
        if self.lockstate == 'unlocked':
            self.lockstate = 'locked'
            msg = 'The '+self.name+' is now locked'
        return msg
    
    # Unlock the container. Trigger the trap if it exists
    def unlock(self):
        buffer = MessageBuffer()
        if self.isLocked():
            self.lockstate = 'unlocked'
            if hasattr(self,'msg_unlock'):
                buffer.add(self.msg_unlock)
            else:
                buffer.add('The '+self.name+' is now unlocked')
            if self.isTrapped():
                if 'trap_effect' in vars(self):
                    buffer.add('It was trapped! '+self.trap_effect)
                else:
                    buffer.add('It was trapped!')
        return buffer.send()

# ============================================================================================
# MONSTER - Basic building block for all Non-Player Characters (people and creatures you 
#           encounter in the game)
# ============================================================================================
class Monster:
    def __init__(self,name):
        self.id=name
        self.name = name    
        self.attributes = []    
        self.responses = 'dlg_default'
        
        filename = os.path.join('data','monsters',self.id.replace(' ','_')+'.txt')
        self.load(filename)
    
    # Load config file
    def load(self,filename):
        try:
            lines = open(resource_path(filename),'r')
            for line in lines:
                if not line.startswith('#') and not line=='\n':  # Ignore comments and empty lines
                    key, value = line.split('=')
                    if key=='treasure' or key=='block_direction' or key=='attributes' or key=='item':
                        setattr(self,key.strip(),value.strip().split(','))
                    else:
                        value = value.strip()
                        match key:
                            case 'AC'|'HP'|'to_hit'|'damage':
                                setattr(self, key.strip(),int(value))
                            case _:
                                setattr(self, key.strip(),value) 
                    

        except:
            print('Configuration file read error')
            raise

    # Reset back to the starting values
    def reset(self):
        self.__init__(self.id)
    
    # Does this monster have this quality/tag?
    def isType(self,quality):
        if quality in self.attributes:
            return True
        return False   
    
    # Toggle an item field between True and False  
    def toggle(self,key):
        if key in vars(self):
            value = getattr(self,key)
            if isinstance(value,str):
                if value.lower() == 'false':
                    value = 'TRUE'
                else:
                    value = 'FALSE'
            elif isinstance(value,bool):
                value = not value
            else:
                return
            setattr(self,key,value)

    # Return the monster's description
    def describe(self):
        if 'describe_text' in vars(self):
            return self.describe_text
        elif 'description' in vars(self):           
            return self.description
        else:
            desc = self.name+" looks like any other "+self.name
            return desc
    
    # Respond to a question or comment
    def respond(self,phrase=''):
        if len(phrase)>0:
            # 
            # REPLACE THIS WITH A RE SEARCH ON TOPIC and see if MONSTER has a RESPONSE
            response = game.voices.get_line(self.id) 
        else:
            response = game.voices.get_line(self.id)
        
        return "The "+self.name+" says: "+response

    def print(self):
        return self.describe()

    def roll_attack(self):
        return roll(20,self.to_hit)
    
# ===============================================================================================
# ROOM - Basic building block for all places/scenes that can be entered or visited in the game.
# ===============================================================================================
class Room:
    def __init__(self, id):
        self.id = id
        self.items = []        
        self.npcs = []
        self.texts = []
        self.map = {}
        self.dark_map = {}
        self.doors = []
        self.count = 0
        self.isSolved = False
        self.light_state = 'lit'
        if not id == 'none':
            self.load(id)
    
    # Load config file
    def load(self,id):
        self.id = id
        try:
            filename = os.path.join('data','rooms',self.id.replace(' ','_')+'.txt')            
            lines = open(resource_path(filename),'r')
            for line in lines:
                if not line.startswith('#') and not line=='\n':  # Ignore comments and empty lines
                    key, value = line.split('=')
                    match key:
                        case 'items'|'npcs'|'texts'|'solution'|'doors':
                            setattr(self,key.strip(),value.strip().split(','))
                        case 'map'|'dark_map':
                            exits = value.strip().split(',')
                            for exit in exits:
                                dir,room = exit.split(':')
                                self.map[dir] = room
                        case _:
                            setattr(self,key.strip(),value.strip())             
        except:
            print(f'Error: No room configuration file for {id}.txt')            
    
    # Reset room back to initial values
    def reset(self):
        self.__init__(self.id)
    
    # Check if the room is lit
    def isLit(self):
        return self.light_state=='lit'
    
    # Turn lights on in the room
    def lightsOn(self):
        self.light_state='lit'
    
    # Turn lights off in the room (switch to dark mode)
    def lightsOff(self):
        self.light_state='dark'

    # Toggle an item field between True and False  
    def toggle(self,key):
        if key in vars(self):
            value = getattr(self,key)
            if isinstance(value,str):
                if value.lower() == 'false':
                    value = 'TRUE'
                else:
                    value = 'FALSE'
            elif isinstance(value,bool):
                value = not value
            else:
                return
            setattr(self,key,value)

    # Does the room has this monster or NPC 
    def isNPC(self,monster):
        try:
            if monster in self.npcs:
                return True
            return False
        except:
            return False

    # Does the room have someone blocking an exit?
    def hasBlocker(self):
        for monster in self.npcs:
            if game.monsters[monster].isType('blocker'):
                return True

    # Return the room's npc that is a blocker 
    #    At the moment, it is safe to assume only one blocker per room, 
    #      but eventually support for different npcs blocking a room 
    #      will need to be implemented    
    def getBlocker(self):
        for monster in self.npcs:
            if game.monsters[monster].isType('blocker'):
                return game.monsters[monster]            
        return None

    # Add an exit to the room (not currently used)
    def addExit(self,dir,room):
        self.map[dir]=room
    
    # Remove an exit to the room (not currently used)
    def removeExit(self,dir):
        del self.map[dir]

    # Check if an exit exists in a given direction
    def hasExit(self,dir):
        return dir in self.map.keys()

    # Add an item to the room. If there is a pile and the item belongs to the pile, return it to the pile
    def add_item(self,item):
        if item in game.dungeon_items.keys():
            if hasattr(game.dungeon_items[item],'pile') and game.dungeon_items[item].pile in self.items:
                game.dungeon_items[game.dungeon_items[item].pile].return_one()
            else:
                self.items.append(item)
    
    # Does this item exist in the room or one of the containers in the room?
    def has_item(self,item):    
        import re    
        if item in game.dungeon_items.keys():
            if item in self.items:
                return True
            for itm in self.items:
                if game.dungeon_items[itm].kind in ['container','lockbox'] and game.dungeon_items[itm].has_item(item):
                    return True
        return False

    # Run a solution script when the game.player solves the puzzle, riddle, or condition
    def run_solution(self):
        buffer = MessageBuffer()
        buffer.add(self.parse(self.solved_script))
        self.isSolved = True                                
        self.short_description = self.solved_description
        buffer.add(self.describe())
        return buffer.send()
    
    def is_solution(self,solve):
        if 'solution' in vars(self):
            if solve in self.solution:                
                return True
        return False

    # Check if the solution command is one of the accepted solution
    def check_solution(self,solve):
        buffer = MessageBuffer()
        if self.isSolved == True:            
            buffer.add("You did that already and it worked.")
            return buffer.send()
        else:
            cmds = solve.split(' ')
            cmd = cmds.pop(0)
            match cmd:

                # If using an item, check to see if the game.player has the item
                case 'use':
                    tool = solve.replace('use ','')
                    if game.player.has_item(tool):
                        buffer.add(self.run_solution())
                    else:
                        buffer.add("This seems like a brilliant idea. Too bad you don't have "+addArticle(tool))
                
                # If unlocking a door or container, make certain there is enough light to do so
                case 'unlock':
                    locked_thing = solve.replace('unlock ','')
                    if game.player.current_room.isLit() or game.player.has_light():
                        if locked_thing in game.player.current_room.items:
                            if hasattr('unlock_key',game.dungeon_items[locked_thing]) and game.dungeon_items[locked_thing].unlock_key in game.player.inventory:
                                buffer.add(self.run_solution())
                            else:
                                buffer.add('If only you had something to unlock the '+locked_thing+' with')
                    
                        elif locked_thing == 'door' or locked_thing in game.player.current_room.doors:
                            if len(game.player.current_room.doors) == 1:
                                door_key = game.player.current_room.doors[0].replace('_',' ')
                                if game.dungeon_items[door_key].unlock_key in game.player.inventory:
                                    buffer.add(self.run_solution())
                                else:
                                    buffer.add("You don't seem to have the right key.")
                            elif locked_thing in game.player.current_room.doors and game.dungeon_items[locked_thing].unlock_key in game.player.inventory:
                                    buffer.add(self.run_solution())
                            else:
                                buffer.add('You try to unlock '+locked_thing+', but fail.')
                        else:
                            buffer.add('You try to unlock '+locked_thing+', but fail.')
                    else:
                        buffer.add("You fumble around for a few minutes, but find it's impossible to unlock something in the dark")
                        
                # Otherwise just run the solution script
                case _:
                    buffer.add(self.run_solution())
        return buffer.send()

    # Parse and execute room script (similar to the Item script parser/interpreter)
    def parse(self,cmdscript):
        buffer = MessageBuffer()
        lines = cmdscript.split(';')
        for line in lines:
            args = line.strip().split(' ')
            cmd = args.pop(0)            
            match cmd:
                case 'set':
                    key = args[0]
                    if args[1] == 'to':
                        setattr(self,key,getattr(self,args[2]))                        
                    elif (args[1].isdigit()==True):
                        value = int(args[1])
                        setattr(self,key,value)
                    else:
                        value = args[1]
                        setattr(self,key,value)                    

                case 'add':
                    key = args[0]
                    if key in vars(self):
                        value = getattr(self,key) + int(args[1])
                    else:
                        value = int(args[1])
                    setattr(self,key,value)
                case 'sub':
                    key = args[0]
                    if key in vars(self):
                        value = getattr(self,key) - int(args[1])
                    else:
                        value = int(args[1])
                    setattr(self,key,value)
                case 'append':
                    key = args.pop(0)
                    if key == 'inventory':
                        for arg in args:
                            value = game.player.inventory + [arg]                        
                    
                    for arg in args:
                        if key in vars(self):
                            value = getattr(self,key)+[arg] 
                            if key == 'items':
                                buffer.add('You found '+addArticle(arg)+'!')
                        else:
                            value = arg
                        setattr(self,key,value)
                case 'remove':
                    key = args[0]
                    if key == 'inventory':
                        for arg in args:
                            value = game.player.inventory.remove(arg)                        
                    
                    if key in vars(self):
                        value = getattr(self,key).remove(args[1])
                    else:
                        setattr(self,key,[])                    
                case 'add_key':
                    att = args.pop(0)
                    key = args.pop(0)
                    value = "".join(args)
                    
                    if att in vars(self):
                        dict = getattr(self,att)
                        dict[key] = value
                    else:
                        dict = {}
                        dict[key]=value
                    setattr(self,att,dict)
                case 'boost':
                    key = args[0]
                    if key in vars(game.player):
                        value = getattr(game.player,key) + int(args[1])
                    else:
                        value = int(args[1])
                    setattr(game.player,key,value)
                case 'print':
                    buffer.add(getattr(self,args[0]))

                # open a container or lockbox
                case 'open':
                    if arg[0] in game.dungeon_items.keys() and game.dungeon_items[arg[0]].kind in ['container','lockbox']:
                        buffer.add(game.dungeon_items[arg[0]].open())
                
                # run a script associated with a room, monster, or item
                case 'run':                    
                    if len(args)>=2:
                        obj = args.pop(0)
                        objcmd = args.pop(0)      
                        if obj == "current_room" or obj == 'here':                            
                            objscript = getattr(game.player.current_room,objcmd)
                            buffer.add(game.player.current_room.parse(objscript))
                       
                        elif obj in game.monsters.keys():
                            objscript = getattr(game.monsters[obj],objcmd)
                            buffer.add(game.monsters[obj].parse(objscript))
                       
                        elif obj in game.dungeon_rooms.keys():
                            objscript = getattr(game.dungeon_rooms[obj],objcmd)
                            buffer.add(game.dungeon_rooms[obj].parse(objscript))
                       
                        elif obj in game.dungeon_items.keys():                            
                            objscript = getattr(game.dungeon_items[obj],objcmd)
                            buffer.add(game.dungeon_items[obj].parse(objscript))
                       
                        else:
                            print(f'Error: Bad script: {" ".join(args)}')
                    else:
                        print(f'Error (ROOM): {" ".join(args)} not properly formatted')

                case _:                    
                    print(f"Error: Room script not recognized")
        return buffer.send()

    # Show the results of search
    def show(self):
        if 'hidden' in vars(self):
            return self.parse(self.hidden)            

    # Display any items in the room
    def display_items(self):
        import re
        buffer = MessageBuffer()
        if len(self.items)>0:            
            if len(self.items) == 1:
                buffer.add('You see the '+self.items[0]+' here')
            elif len(self.items) == 2:
                buffer.add('The '+self.items[0]+' and '+self.items[1]+' are here.')
            else:
                itmlist = get_list_as_string(self.items)
                buffer.add('You see '+itmlist+' here.')
            for itm in self.items:
                if game.dungeon_items[itm].kind in ['container','lockbox'] and game.dungeon_items[itm].isOpen():
                    buffer.add(game.dungeon_items[itm].spill())
        return buffer.send()
    
    # Display the npcs in the room
    def display_npcs(self):
        msg = ''
        if len(self.npcs)>0:            
            if len(self.npcs) == 1:
                msg = 'You see '+addArticle(game.monsters[self.npcs[0]].name)+' here.'
            elif len(self.items) == 2:
                msg = 'The '+game.monsters[self.npcs[0]].name+' and '+game.monsters[self.npcs[0]].name+' are here.'
            else:
                room_npcs = get_list_as_string(self.npcs)
                msg = 'You see' + room_npcs
        return msg
    
    # Display visible room exits
    def display_exits(self):
        if len(self.map)>0:
            exitlist = ', '.join(self.map.keys())               
            return "You can go: "+exitlist

    # Describe the room
    def describe(self):
        buffer = MessageBuffer()
        buffer.add('\n<< '+self.name+' >>')
        if self.isLit() or game.player.has_light():
            if self.count == 0:
                buffer.add(self.long_description.strip())
                self.count += 1
            else:
                buffer.add(self.short_description.strip())
            
            itms = self.display_items()
            npcs = self.display_npcs()
            exits = self.display_exits()

            if itms or npcs or exits:
                buffer.add('')

            if not itms == None and not itms == '':
                buffer.add(self.display_items())
            if not npcs == None and not npcs == '':
                buffer.add(self.display_npcs())
            if not exits == None and not exits == '':
                buffer.add(self.display_exits())
        else:
            if 'dark_description' in vars(self):
                buffer.add(self.dark_description)
            else:
                buffer.add("It's very dark. You can't see anything.")
            if len(self.npcs)>0:
                buffer.add('You think you hear someone moving around in the darkness')
            if len(self.dark_map)>0:
                exitlist = ', '.join(self.dark_map.keys())  
                buffer.add('You feel a slight breeze coming from the '+exitlist)
            elif len(self.map)>0:
                exitlist = ', '.join(self.map.keys())  
                buffer.add('You feel a slight breeze coming from the '+exitlist)                
        return buffer.send()
    
    # Enter (alias for describe)
    def enter(self):
        return self.describe()
    
# ========================================================================================================
# LOAD DUNGEON - Read dungeon room list file and return a dictionary of Rooms using room names as indexes.
# ========================================================================================================
def load_dungeon():
    roomlist = {}
    lines = open(resource_path('rooms.txt'),'r')
    
    for line in lines:
        name = line.strip()
        roomlist[name]=Room(name)
    
    return roomlist
# ====================================================================================================
# PLAYER - Controls and manages the game.player's interaction with the world, in terms of environment, 
#          items, and creatures
# ====================================================================================================
class Player:    
    def __init__(self,start='starting_room'):
        self.name = 'Player'        
        self.inventory = []
        self.start_room =start        
        self.current_room = Room(start)       
        self.AC = 14
        self.HP = 20
        self.max_HP = 20
        self.weapon = 'fist'
        self.light_source='none'   
        self.container_list=[]

    # Set the current room back to the default starting room
    def start(self):
        self.current_room = game.dungeon_rooms[self.start_room]
    
    # Reset Player back to starting values
    def reset(self):
        self.name = 'Player'        
        self.inventory = []
        self.current_room = game.dungeon_rooms['starting_room']
        self.AC = 14
        self.HP = 20
        self.weapon = 'fist'
        self.light_source='none'       
        self.container_list=[]
    
    # Toggle an item field between True and False  
    def toggle(self,key):
        if key in vars(self):
            value = getattr(self,key)
            if isinstance(value,str):
                if value.lower() == 'false':
                    value = 'TRUE'
                else:
                    value = 'FALSE'
            elif isinstance(value,bool):
                value = not value
            else:
                return
            setattr(self,key,value)

    # Roll attack using a 20-sided die
    def roll_attack(self,weapon='weapon'):
        if weapon=='weapon':
            return roll(20,game.dungeon_items[self.weapon].to_hit)
        return roll(20,game.dungeon_items[weapon].to_hit)        
    
    # Take damage. Return True if game.player takes enough damage to die
    def take_damage(self,amount):
        self.HP=self.HP - amount
        return self.HP<= 0

    # Attack target
    def attack(self,enemy,special):    
        buffer = MessageBuffer()
        # if the monster isn't here, skip the attack
        if not enemy in game.player.current_room.npcs:
            return "You don't see "+addArticle(enemy)+" here to attack."
        
        # look up enemy info
        monster = game.monsters[enemy]    
        crit_mod = 1    
        crit_text = ''
        if special == 'weapon':
            pc_weapon = game.dungeon_items[self.weapon]      # Creating a copy to make it easier to reference
        else:
            pc_weapon = game.dungeon_items[special]          # Override the current weapon to use fist or foot

        weapon_name = pc_weapon.name
        

        # STAGE 1 - HANDLE PLAYER ATTACKING MONSTER
        buffer.add('You attack the '+monster.name+' with '+weapon_name)    
        attack_roll = self.roll_attack(weapon_name)     

        # check for critical hit
        if attack_roll>=20:
            crit_mod=2
            crit_text=pc_weapon.crit_text

        # see if attack successfully hits the monster
        if attack_roll > monster.AC:                        
            # game.player hits monster
            monster.HP = monster.HP - crit_mod*pc_weapon.damage
            buffer.add(crit_text)
            buffer.add(pc_weapon.hit_text)
            game.monsters[enemy] = monster
            if monster.HP<=0:                
                buffer.add('[[You have slain the '+monster.name)
                buffer.add(monster.death_text)
                monster.HP = 0
                game.monsters[enemy] = monster
                game.player.current_room.items.append(monster.corpse)                
                game.player.current_room.items = game.player.current_room.items + monster.item
                
                game.player.current_room.npcs.remove(enemy)                
                buffer.add(game.player.current_room.enter())
                return buffer.send()
        else:
            # game.player misses monster
            buffer.add(pc_weapon.miss_text)            
        
        # STAGE 2 - HANDLE MONSTER ATTACKING PLAYER
        if monster.roll_attack() >= self.AC:
            
            # monster hits game.player
            isKilled = self.take_damage(monster.damage)
            buffer.add(monster.hit_text)
            if isKilled:
                buffer.add('You died! The '+monster.name+' has slain you with its treacherous attack.')
                buffer.add('[DIED]'+self.death('You were killed by the '+monster.name))   # Send game.player immediately to Bad Ending
        else:
            # monster misses game.player
            buffer.add(monster.miss_text)
        
        return buffer.send()
    
    # Talk to an npc or to yourself
    def talk(self,targets):
        buffer = MessageBuffer()
        import re
        if len(self.current_room.npcs)>0:
            if len(targets)>0:
                if targets[0] in self.current_room.npcs:
                    target = targets.pop(0)
                    buffer.add('You talk to the '+target+'.')
                    if game.monsters[target].isType('talkative'):                                    
                        buffer.add(game.monsters[target].respond())
                    else:
                        buffer.add('The '+target+' does not appear to enjoy your attempts at small talk.')
                else:
                    target = " ".join(targets)
                    for npc in self.current_room.npcs:
                        match_short = re.search(target,self.current_room.short_description)
                        match_long = re.search(target,self.current_room.long_description)
                        if match_short==None and match_long==None:
                            if re.search(npc,target)==None:
                                buffer.add("I don't see "+addArticle(target)+" here. You must be hallucinating.")                        
                            else:
                                print(f'You talk to the {npc}')
                                if game.monsters[npc].isType('talkative'):                                    
                                    buffer.add(game.monsters[npc].respond())
                                else:
                                    buffer.add("The "+npc+" doesn't respond to your small talk")

                        else:
                            target = npc
                            buffer.add('You talk to the '+target+'.')
            else:
                buffer.add('You talk, but no one is here to hear you.')
        else:
            if len(targets)>0:
                target = " ".join(targets)
                if re.search(target,self.current_room.short_description)==None and re.search(target,self.current_room.long_description)==None:
                    buffer.add("You don't see "+addArticle(target)+" to speak to.")
                else:
                    buffer.add("You try speaking to the "+target+", but it doesn't respond. Perhaps it's shy?")
            else:
                buffer.add('You blather on to no one in particular.')
        return buffer.send()
    
    # Move the game.player 
    def move(self, direction: str):        
        buffer = MessageBuffer()
        # Check if move is toward a valid exit in the current room
        if direction in self.current_room.map.keys():       
            if self.current_room.hasBlocker():
                blocker = self.current_room.getBlocker() 
                if direction in blocker.block_direction:    
                    buffer.add(blocker.block_text)
                else:
                    buffer.add('The '+blocker.name+' ignores your cowardly retreat.')
                    self.current_room = game.dungeon_rooms[self.current_room.map[direction]]
                    buffer.add(self.current_room.enter())
            else:
                self.current_room = game.dungeon_rooms[self.current_room.map[direction]]
                buffer.add(self.current_room.enter())
                if 'game_exit' in vars(self.current_room):
                    game.game_won = True
                    buffer.add('[END]')
        
        # check for short versions
        elif direction in ['n','s','w','e']:
            match direction:
                case 'n':
                    buffer.add(game.player.move('north'))
                case 's':
                    buffer.add(game.player.move('south'))
                case 'w':
                    buffer.add(game.player.move('west'))
                case 'e':
                    buffer.add(game.player.move('east'))
                case _:
                    buffer.add('Where am I?')
        else:
            go_dir = direction
            match direction:
                case 'n':
                    go_dir = 'north'
                case 's':
                    go_dir = 'south'
                case 'e':
                    go_dir = 'east'
                case 'w':
                    go_dir = 'west'
                case 'u':
                    go_dir = 'up'
                case 'd':
                    go_dir = 'down'
                case _:
                    go_dir = direction
            
            buffer.add('You cannot move '+go_dir+'!')
        
        return buffer.send()
    
    # Display the contents of the inventory, including items in carried containers
    def view_inventory(self):
        buffer = MessageBuffer()
        if len(self.inventory)>0:
            buffer.add("You are carrying: "+get_list_as_string(self.inventory))
            for thing in self.container_list:
                if not game.dungeon_items[thing].isEmpty():
                    buffer.add("The "+thing+" contains: "+get_list_as_string(game.dungeon_items[thing].contents))
        else:
            buffer.add("You don't have anything")    
        return buffer.send()
    
    # Add item to game.player inventory
    def add_item(self,item):
        buffer = MessageBuffer()
        if not self.has_item(item):
            buffer.add('You add the '+item+' to your inventory')
            self.inventory.append(item)
            if game.dungeon_items[item].isKind('weapon'):                        
                self.weapon = item
            if game.dungeon_items[item].isType('lightable'):
                self.light_source = item
            if game.dungeon_items[item].kind in ['container','lockbox']:
                self.container_list.append(item)
        else:
            buffer.add("You've already got "+addArticle(item)+", no need to take another.")    
        return buffer.send()

    # Remove item from inventory
    def remove_item(self,item):
        buffer = MessageBuffer()
        if self.has_item(item):
            if item in self.inventory:
                self.inventory.remove(item)
                if item == self.weapon:
                    self.weapon = 'fist'   
                if item == self.light_source:
                    self.light_source = 'none'             
                return
            for itm in self.container_list:
                if game.dungeon_items[itm].has_item(itm):
                    game.dungeon_items[itm].remove_item(itm)
                    if item == self.weapon:
                        self.weapon = 'fist'
                    if item == self.light_source:
                        self.light_source = 'none'             
                    return 
        else:
            buffer.add("You don't have the "+item)
        
        return buffer.send()
    
    # Check to see if game.player has a light source
    def has_light(self):
        # Check if the game.player has a light source that isn't inside a container
        for itm in self.inventory:
            if game.dungeon_items[itm].isType('lightable'):
                return game.dungeon_items[itm].in_use == True
        return False
    
    def has_possible_matches(self,item):
        possible_matches = []
        for itm in game.dungeon_items:            
            if item in itm:
                possible_matches.append(itm)
        
        if len(possible_matches)>0:
            for itm in possible_matches:
                if self.has_item(itm):
                    return True
       
        return False

    # Check if item is in the game.player's inventory
    def has_item(self,item):
        if item in self.inventory:            
            return True
        if len(self.container_list)>0:
            for itm in self.container_list:
                if not game.dungeon_items[itm].isEmpty():
                    if game.dungeon_items[itm].has_item(item):
                        return True
            return False
        
        return False
        
    
    # Look at item in inventory (including items in carried containers). Also look at corpses or other items in room description.
    def look_item(self,item):        
        import re
        if item == 'corpse':
            for itm in self.current_room.items:
                if not re.search('corpse',itm)=='None':
                    return game.dungeon_items[itm].describe()
                
        if self.has_item(item):
            return game.dungeon_items[item].describe()
        
        if re.search(item,self.current_room.short_description)==None and re.search(item,self.current_room.long_description)==None:
            return "It's hard to describe something that isn't here."
        elif 'texts' in vars(self.current_room) and item in self.current_room.texts:
            return game.handle('read '+item)
        else:            
            return 'There is nothing remarkable about the '+item

    # Take an item marked 'plural' and ensure that you don't take duplicates.
    def take_plural_item(self,item):
        if self.has_item(item):
            return 'You already have '+addArticle(item)+'. You decide not to be greedy.'
        return self.add_item(item)
    
    # Pick up item and add it to the game.player inventory
    def pick_up(self, item):    
        import re    
        buffer = MessageBuffer()

        # Check to see if there is a script to run when the item is taken
        if "on_take" in vars(self.current_room):
            take_key = 'on_take_'+item
            if take_key in vars(self.current_room):
                line = getattr(self.current_room,take_key)
                cmds = line.split(';')
                for cmd in cmds:
                    result = self.current_room.parse(cmd)
                    if not result == '':
                        buffer.add(self.current_room.parse(cmd))

        # If the game.player takes all, run through the list picking up items individually
        if item in ['all','everything']:
            if self.current_room.items == []:
                buffer.add("There's nothing to pick up here")
            else:
                itmlist=[]
                for itm in self.current_room.items:
                    itmlist.append(itm)                    
                    if game.dungeon_items[itm].kind in ['container','lockbox'] and game.dungeon_items[itm].isOpen():
                        itmlist = itmlist+game.dungeon_items[itm].contents
            
                while not itmlist==[]:
                    itm = itmlist.pop(0)
                    buffer.add(self.pick_up(itm))
        else:
            
            # If the item is currently in the room's list of items (ie. it's present and recognized as an object)
            if item in self.current_room.items:                     
                
                # If the item is a corpse, leave it alone
                if not re.search('corpse',item) == None:
                    buffer.add("You sicko. Why are you tampering with the "+item+"? Let the poor thing rest in peace.")
                    return buffer.send()
                                
                # If the item is a regular item that already exists in the item directory
                elif item in game.dungeon_items.keys():
                    
                    # If the item is actually a pile, then only take one thing from the pile
                    if game.dungeon_items[item].isKind('pile'):
                        thing = game.dungeon_items[item].take_one()
                        if not thing == '' and thing in self.inventory:
                            buffer.add('You already have '+addArticle(thing)+'. You decide not to be greedy.')
                            return buffer.send()
                        buffer.add(self.add_item(thing))
                        return buffer.send()
                    
                    # If the item is locked (can't be taken until a condition is met)
                    elif game.dungeon_items[item].isType('locked'):
                        buffer.add("Try as you might, you just can't get the "+item+" free.")
                        return buffer.send()
                    
                    # If the item is marked as immovable (can't be taken) 
                    elif game.dungeon_items[item].isType('immovable'):
                        buffer.add("You can't seem to move it. The "+item+" isn't going anywhere.")
                        return buffer.send()
                    
                    # If the item is plural (ie. multiple exist), only one in the inventory at a time.
                    # This covers duplicate items that aren't pulled from piles
                    elif game.dungeon_items[item].isType('plural'):
                        buffer.add(self.take_plural_item(item))
                        return buffer.send()
                    
                    # If the item is a normal item 
                    else:                    
                        self.current_room.items.remove(item)
                        buffer.add(self.add_item(item))
                        return buffer.send()
            
            # If the item is a valid item, but not necessarily in the room
            elif item in game.dungeon_items.keys():

                for itm in self.current_room.items:
                    # Check if item is in a container
                    if game.dungeon_items[itm].isKind('container') and game.dungeon_items[itm].isHolding(item):
                        if game.dungeon_items[itm].isOpen():
                            game.dungeon_items[itm].contents.remove(item)
                            buffer.add(self.add_item(item))
                            return buffer.send()
                    
                    # Check if item is in a pile
                    elif game.dungeon_items[itm].isKind('pile') and game.dungeon_items[itm].isHolding(item):
                        if not game.dungeon_items[itm].isEmpty():
                            thing = game.dungeon_items[itm].take_one()
                            if not thing == '' and thing in self.inventory:
                                buffer.add('You already have '+addArticle(thing)+'. You decide not to be greedy.')
                                return buffer.send()
                            buffer.add(self.add_item(thing))
                            return buffer.send()
            
            # If the game.player taking from an unspecified pile, if take from the first pile in the room if it exists
            elif not re.search('pile',item) == None:
                for itm in self.current_room.items:
                    if game.dungeon_items[itm].isKind('pile') and not game.dungeon_items[itm].isEmpty():
                        thing = game.dungeon_items[itm].take_one()
                        if not thing == '' and thing in self.inventory:
                            buffer.add('You already have '+addArticle(thing)+'. You decide not to be greedy.')
                            return buffer.send()
                        buffer.add(self.add_item(thing))
                        return buffer.send()

            # If the item is a plural (ends with s, but not ss), then try the singular form
            elif not re.search('[a-r,t-z]s$',item) == None:
                itm = item[0:len(item)-1]
                buffer.add(self.pick_up(itm))
           
            # For items in the room description, but not interactive, or anything else that isn't listed or known
            else:
                if re.search(item,self.current_room.short_description)==None and re.search(item,self.current_room.long_description)==None:
                    buffer.add("You don't see "+addArticle(item)+" here.")                
                else:
                    buffer.add("You can't take that.")                                
        return buffer.send()

    # Drop item from game.player inventory 
    def drop_item(self, item):
        buffer = MessageBuffer()
        if item=='all':            
            if len(self.inventory)>0:
                itmlist=[]
                for itm in self.inventory:
                    print(f'ITEMS: {itm}')
                    itmlist.append(itm)                    
                    if game.dungeon_items[itm].kind in ['container','lockbox'] and not game.dungeon_items[itm].isEmpty():
                        itmlist = itmlist+game.dungeon_items[itm].contents
                while not itmlist==[]:
                    itm = itmlist.pop(0)
                    buffer.add(self.drop_item(itm))
            else:
                buffer.add("You don't have anything to drop")
            
        elif item in self.inventory:
            print('about to drop item')
            self.inventory.remove(item)
            buffer.add(self.current_room.add_item(item))            
            buffer.add('You drop the '+item+'.')
            if self.weapon==item:
                self.weapon='fist'
            if item in self.container_list:
                self.container_list.remove(item)
            
        
        elif len(self.container_list)>0:
            for thing in self.container_list:
                if item in game.dungeon_items[thing].contents:
                    buffer.add(game.dungeon_items[thing].remove_item(item))
            
        else:
            buffer.add("What "+item+"? You don't have any")
            
        
        return buffer.send()
    
    # Pull item out of a carried container
    def pull_out_item(self,item,container='any'):
        buffer = MessageBuffer()
        if self.has_item(item) and not item in self.inventory:
            if container == 'any':
                for box in self.container_list:
                    if game.dungeon_items[box].has_item(item):
                        buffer.add(game.dungeon_items[box].remove_item(item))
                        self.inventory.append(item)
                        #buffer.add('You pull the '+item+' out of the '+box+'.')
                        return buffer.send()
            
            elif container in self.container_list:
                if game.dungeon_items[container].has_item(item):
                    buffer.add(game.dungeon_items[container].remove_item(item))
                    self.inventory.append(item)
                    #buffer.add('You pull the '+item+' out of the '+container+'.')
                    return buffer.send()
            else:
                buffer.add("You don't have the "+container)
        elif item in self.inventory:
            buffer.add('You already have the '+item+' out.')
        else:
            buffer.add("You don't have the "+item)

        return buffer.send()



    # Put item into a container or pile, or drop it in the room
    def put_item(self,item,destination='room'):
        buffer = MessageBuffer()
        import re
        match destination:
            case 'room'|'here':
                # Drop the item in the room
                buffer.add(self.drop_item(item))
            case _:
                if self.has_item(item):

                    # Put the item in a container in the room
                    if destination in self.current_room.items and game.dungeon_items[destination].kind in ['container','lockbox']:
                        buffer.add(self.remove_item(item))
                        game.dungeon_items[destination].contents.append(item)
                        buffer.add('You put the '+item+' in the '+destination)

                    # Put the item in a container that the game.player is carrying
                    elif destination in self.inventory and game.dungeon_items[destination].kind in ['container','lockbox']:
                        self.inventory.remove(item)
                        game.dungeon_items[destination].contents.append(item)
                        buffer.add('You put the '+item+' in the '+destination+' that you are carrying')
                    
                    # Return the item to a pile of its own kind
                    elif destination == 'pile' or not re.search('pile',destination) == None:
                        for itm in self.current_room.items:
                            if game.dungeon_items[itm].isKind('pile'):
                                if game.dungeon_items[itm].isHolding(item):
                                    game.dungeon_items[itm].return_one()
                                    buffer.add('You put the '+item+' back in the pile of '+item+'s')
                                    buffer.add(self.remove_item(item))
                                    return buffer.send()
                        # If there's no pile of that type in the room, drop it in the room.
                        buffer.add(self.drop_item(item))
                    
                    # Attempting to put an item in an invalid location fails
                    else:
                        buffer.add("You can't put the "+item+" in the "+destination)
                    return buffer.send()
        buffer.add("You don't have the "+item)
        return buffer.send()

    # When the game.player dies, show death message and then ask if they want to play again
    def death(self,msg):
        buffer = MessageBuffer()
        buffer.add(msg)
        return buffer.send()
    
# Initialize Global Monster Directory
def load_dungeon(filename='rooms.txt'):
    roomlist = {}
    filepath = os.path.join('data',filename)
    lines = open(resource_path(filepath),'r')
    
    for line in lines:
        name = line.strip()
        roomlist[name]=Room(name)
    
    return roomlist

# Initialize Global Item Directory
def load_itemlist(filename='items.txt'):
    itemlist = {}
    filepath = os.path.join('data',filename)
    lines = open(resource_path(filepath),'r')
    
    for line in lines:
        name = line.strip()        
        keyname = name.replace('_',' ')
        key,itmType = keyname.split('|')        
        match itmType:
            case 'lockbox':
                itemlist[key]=Lockbox(key)
            case 'container':
                itemlist[key]=Container(key)
            case 'weapon':
                itemlist[key]=Weapon(key)
            case 'pile':
                itemlist[key]=Pile(key)
            case 'door':
                itemlist[key]=Door(key)
            case _:
                itemlist[key]=Item(key)
    
    return itemlist

# Initialize Global Monster Directory
def load_monsterlist(filename='monsters.txt'):
    monsterlist = {}
    filepath = os.path.join('data',filename)
    
    lines = open(resource_path(filepath),'r')
    
    for line in lines:
        name = line.strip()
        monsterlist[name]=Monster(name)
    
    return monsterlist

# Initialize Global Dialog/Sound Directory
def load_dialog(name='dialog'):
    return DialogManager(name)

class Console:
    def __init__(self):
        self.log = []
        
        self.directions = ['north','west','south','east','n','w','e','s']
        self.commands = self.directions+ ['about','ask','help','move','look','examine','take','get','drop','leave','eat','drink','inventory','quit','hint','stats','stuck','listen','smell','kick','punch','open','close','lock','unlock','talk','light','use']
        
        self.dungeon_items=load_itemlist()
        self.dungeon_rooms=load_dungeon()
        self.monsters=load_monsterlist()
        self.voices=load_dialog()
        self.player = Player()
        self.game_won = False
        
        try:
            lines = open(resource_path('config.txt'),'r')

            for line in lines:
                if not line.startswith('#') and not line=='\n':  # Ignore comments and empty lines
                    key, value = line.split('=')
                    match key:
                        case 'new_commands':
                            raw_cmds = value.strip().split(',')
                            all_cmds = []
                            for itm in raw_cmds:
                                if len(itm.strip())>0:
                                    if itm.find('|')>-1:
                                        all_cmds = all_cmds+itm.strip().split('|')
                                    else:
                                        all_cmds.append(itm)
                            setattr(self,key.strip(),all_cmds)   
                        case 'directions'|'commands':
                            setattr(self,key.strip(),value.strip().split(','))   
                        case 'fontsize'|'displayfontsize'|'titlefontsize':
                            setattr(self, key.strip(),int(value))
                        case _:                        
                            setattr(self, key.strip(),value.strip()) 
            self.commands = self.new_commands + self.directions
            self.commands.sort()
        except:
            print('File read error: console.txt does not exist')    

    def get(self,num=25):
        logsize = len(self.log)        
        msg = ''
        start = 0
        end = logsize
        
        if logsize>num:
            start = logsize-num 
            
        for cmd in self.log[start:end]:
            msg = msg +cmd+"\n"

        return msg  
    
    def get_output(self,buffer,num=25):
        logsize = len(buffer)
        msg = []
        start = 0
        end = logsize
        
        if logsize>num:
            start = logsize-num 
            
        for cmd in buffer[start:end]:
            msg.append(cmd)

        return msg  

    def add(self,msg):
        self.log.insert(0,msg)
    
    def handle(self,msg):
        import re
        buffer = MessageBuffer()        

        # Trim references to 'a piece of'
        if msg.find('a piece of '):
            msg = msg.replace('a piece of ','')
        
        # Remove references to 'some' 
        if msg.find('some '):
            msg = msg.replace('some ','')

        # Strip white space from the front and end of the line
        msg = msg.strip()        

        # Split the line into a list of commands/tokens
        cmds = msg.split(' ')
        
        # Remove any instances of 'the'
        if cmds.count('the') > 0:
            cmds.remove('the')

        # Check to see if command is a Solution for the current room's Puzzle
        solve = " ".join(cmds).strip()
        if self.player.current_room.is_solution(solve):
            buffer.add(self.player.current_room.check_solution(solve))
            return buffer.send()

        if len(cmds)>0 and cmds[0] in self.commands:
            cmd = cmds.pop(0)
            cmd = cmd.lower()
            self.add(msg)
            match cmd:
                # GENERAL COMMANDS                
                
                # Show about message
                case 'about':
                    return self.msg_about
                
                # Display help message
                case 'help':     
                    return self.msg_help  
                
                # Display list of available commands
                case 'commands': 
                    new_msg = ", ".join(self.commands)
                    new_msg = 'You can use the following commands: '+new_msg
                    return new_msg
                
                # Display help message if game.player is confused/stuck
                case 'stuck':
                    buffer.add(self.msg_stuck)
                    return buffer.send()
                
                # Display hint text for the room if it exists
                case 'hint':
                    if 'hint' in vars(self.player.current_room):   # Pulls hints for each room if the room file has one defined
                        return self.player.current_room.hint
                
                 # Display player's current stats (Hit Points, Armor Class, Attack Modifier)
                case 'stats':
                    buffer.add("Current Hit Points: "+str(self.player.HP)+"/"+str(self.player.max_HP))
                    buffer.add("Current Armour Class: "+str(self.player.AC))
                    buffer.add("Current Attack Modifier: "+str(self.dungeon_items[self.player.weapon].to_hit))
                    return buffer.send()

                # Display player inventory
                case 'inventory'|'inv':
                    buffer.add(self.player.view_inventory())
                    return buffer.send()
                
                # Exit game
                case 'quit'|'exit': 
                    return 'quit'
                
                # NAVIGATION

                # Show visible exits in this room
                case 'exits':
                    msg = ", ".join(self.player.current_room.map.keys())
                    return 'Exits: '+msg

                # Move player in a given direction
                case 'go'|'move':                    
                    newdir = cmds.pop(0)
                    if newdir in self.directions:
                        buffer.add(self.player.move(newdir))      
                    elif newdir == 'to':
                        destination = " ".join(cmds)
                        buffer.add("You can't go to "+destination+" from here")
                    else:
                        buffer.add("You can't go "+newdir+" from here")
                    return buffer.send()
                
                # Move in the specified direction
                case 'n'|'s'|'e'|'w'|'north'|'south'|'east'|'west'|'up'|'down':
                    return self.player.move(cmd) 
                
                 # Jump or crouch (not used in this game)
                case 'jump'|'crouch':
                    print(f'You try to {cmd}, but nothing happens.')


                # DIALOG COMMANDS

                # Ask a question to an npc if there's one in the room
                case 'ask':
                    if len(cmds)>0:
                        if cmds[0] in self.player.current_room.npcs:
                            target = cmds.pop(0)
                            if target in self.player.current_room.npcs:
                                if len(cmds)>0:
                                    topic = " ".join(cmds)
                                    buffer.add(self.monsters[target].respond(topic))
                                else:
                                    buffer.add("What did you want to ask the "+target+"?")

                        elif cmds[0] == 'about':
                            cmds.pop(0) # Remove 'about'
                            topic = " ".join(cmds)
                            if len(self.player.current_room.npcs)>0:                            
                                for npc in self.player.current_room.npcs:
                                    buffer.add(self.monsters[npc].respond(topic))
                            else:
                                buffer.add("There's no one here to ask about "+topic)
                        else:
                            topic = " ".join(cmds)
                            if len(self.player.current_room.npcs)>0:                            
                                for npc in self.player.current_room.npcs:
                                    buffer.add(self.monsters[npc].respond(topic))
                            else:
                                buffer.add("There's no one here to ask about "+topic)
                    else:
                        buffer.add('You should ask someone about something.')
                    
                    return buffer.send()
                
                # Say a phrase aloud.
                case 'say':       
                    if len(cmds)>0:                    
                        wrds = " ".join(cmds)
                        match wrds:
                            case 'nothing'|'nada':
                                buffer.add("You hold your tongue. Perhaps now is not the right time to speak?")
                            case _: 
                                if len(self.player.current_room.npcs)>0:                    
                                    buffer.add("You say: '"+wrds.capitalize()+"' ")
                                    for npc in self.player.current_room.npcs:
                                        buffer.add(self.monsters[npc].respond(wrds))
                                else:
                                    buffer.add("'"+wrds.capitalize()+".' "+self.voices.get_line('echoes'))
                    else:
                        buffer.add('What did you want to say?')
                    
                    return buffer.send()
                
                # Talk to an npc
                case 'talk':
                    if len(cmds)>0:                    
                        if cmds[0] in ['to','with']:
                            cmds.pop(0)
                            buffer.add(self.player.talk(cmds))
                        else:                        
                            buffer.add(self.player.talk(cmds))
                    else:
                        buffer.add('You blather on to yourself, sounding increasingly unhinged.')
                    
                    return buffer.send()
                
                # Kiss a person or object
                case 'kiss':        
                    if len(cmds)>0:
                        thing = " ".join(cmds)
                        buffer.add('The '+thing+" does not appreciate your romantic overtures.")
                    else:
                        buffer.add('Kiss what?')
                    
                    return buffer.send()
                
                # Attack a person or object
                case 'attack'|'hit'|'fight'|'kill':
                    if len(cmds)>0:
                        target = ' '.join(cmds)
                        buffer.add(self.attack(target))
                    elif len(self.player.current_room.npcs)==1:
                        target = self.player.current_room.npcs[0]
                        buffer.add(self.attack(target))
                    else:
                        buffer.add('Who or what are you attacking?')
                    
                    return buffer.send()

                # Kick a person or object
                case 'kick':
                    buffer.add(self.kick(cmds))
                    return buffer.send()
                
                # Punch a person or object
                case 'punch':
                    buffer.add(self.punch(cmds))
                    return buffer.send()
            
                # SENSE COMMANDS

                # Look at the item, npc, or room
                case 'look'|'examine':
                    buffer.add(self.look(cmds))
                    return buffer.send()
                

                # Listen to sounds
                case 'listen':
                    buffer.add(self.listen(cmds))
                    return buffer.send()
                
                # Smell the environment
                case 'smell':
                    buffer.add(self.smell(cmds))                    
                    return buffer.send()
                

                # ROOM/ENVIRONMENT COMMANDS

                # Search for hidden items and things                       
                case 'search':
                    buffer.add(self.search(cmds))
                    return buffer.send()
                
                # PLAYER-ENVIRONMENT COMMANDS

                # Lights a lightable item (if the player has one)
                case 'light':       
                    if len(cmds)>0:
                        if cmds[0] in self.dungeon_items.keys() and self.player.has_item(cmds[0]) and self.dungeon_items[cmds[0]].isType('lightable'):
                            buffer.add(self.dungeon_items[cmds[0]].use())
                        else:
                            buffer.add("You don't have a light source to light.")
                    return buffer.send()
                
                # Read items or environmental features
                case 'read':        
                    if len(cmds)>0:
                        unavailable_texts = ['newspaper','tombstone','fortune cookie','will','letter','poem']
                        itm = " ".join(cmds)
                        if itm in self.dungeon_items.keys():
                            if self.player.current_room.has_item(itm) or self.player.has_item(itm):
                                if self.dungeon_items[itm].isType('readable'):                                    
                                    buffer.add(box_msg(self.dungeon_items[itm].read()))
                                else:
                                    buffer.add("There's nothing to read on the "+itm+".")
                            else:
                                buffer.add("You don't see "+addArticle(itm)+" here.")
                        elif 'texts' in vars(self.player.current_room) and itm in self.player.current_room.texts:
                            buffer.add('You read the '+itm+'.')
                            buffer.add(box_msg(self.player.current_room.riddle))
                            
                        elif itm in unavailable_texts:
                            buffer.add("You would love to read "+addArticle(itm)+". Sadly you don't have access to one here.")
                        else:
                            if re.search(itm,self.player.current_room.long_description) == None and re.search(itm,self.player.current_room.short_description) == None:
                                buffer.add("There is no "+itm+" around to read.")
                            else:
                                buffer.add("There's nothing to read on the "+itm)
                    else:
                        buffer.add('What do you wish to read?')
                    
                    return buffer.send()
                
                # Take or get something 
                case 'get'|'take':
                    if len(cmds)>0:                    
                        phrase = " ".join(cmds)
                        if not re.search(' from ',phrase)==None:
                            thing,container = phrase.split(' from ')
                            buffer.add(self.player.pull_out_item(thing.lower(),container))
                        else:
                            buffer.add(self.player.pick_up(phrase.lower()))
                    else:
                        buffer.add('Take what?')            
                    return buffer.send()
                
                # Drop or leave something
                case 'drop'|'leave':
                    if len(cmds)>0:
                        thing = " ".join(cmds)     
                        buffer.add(self.player.drop_item(thing.lower()))
                    else:
                        buffer.add('Drop what?')
                    return buffer.send()
                
                # Put or place something into a container
                case 'put'|'place':
                    if len(cmds)>0:
                        phrase = " ".join(cmds)
                        if not re.search(' in ',phrase)==None:
                            thing,container = phrase.split(' in ')
                            buffer.add(self.player.put_item(thing.lower(),container))
                    return buffer.send()
                
                case 'add':
                    if len(cmds)>0:
                        phrase = " ".join(cmds)
                        if not re.search(' to ',phrase)==None:
                            thing,container = phrase.split(' to ')
                            buffer.add(self.player.put_item(thing.lower(),container))
                    return buffer.send()

                case 'remove':
                    if len(cmds)>0:
                        phrase = " ".join(cmds)
                        if not re.search(' from ',phrase)==None:
                            thing,container = phrase.split(' from ')
                            buffer.add(self.player.pull_out_item(thing.lower(),container))
                    return buffer.send()

                # Eat something (if edible)
                case 'eat':
                    buffer.add(self.eat(cmds))
                    return buffer.send()
                    

                # Drink something (if drinkable)
                case 'drink':
                    buffer.add(self.drink(cmds))
                    return buffer.send()                    

                # Use an item
                case 'use':
                    buffer.add(self.use(cmds))
                    return buffer.send()

                # Open a container, door, or corpse
                case 'open':
                    buffer.add(self.open(cmds))
                    return buffer.send()
                    
            
                # Close a container or door
                case 'close':                
                    buffer.add(self.close(cmds))
                    return buffer.send()
                
                # Unlock a container or door
                case 'unlock':
                    buffer.add(self.unlock(cmds))
                    return buffer.send()
                
                # Lock a container or door
                case 'lock':
                    buffer.add(self.lock(cmds))
                    return buffer.send()

                case _:
                    return cmd+" handled "
        else:
            return 'ERROR: '+msg+' is not a recognized command'
        return buffer.send()
    
    def print(self,num=40):
        logsize = len(self.log)        
        msg = ''
        start = 0
        end = logsize
        
        if logsize>num:
            start = logsize-num          
        for cmd in self.log[start:end]:
            msg = msg +cmd+"\n"

        return msg
    
    def look(self,cmds):        
        buffer = MessageBuffer()
        phrase = " ".join(cmds)
        if len(cmds)>0:
            nextcmd = cmds.pop(0)

            # Handle prepositions
            if nextcmd in ['in','on','at','under','inside']:
                item = " ".join(cmds)
                if self.player.current_room.isNPC(item):
                    buffer.add(self.monsters[item].describe())
                elif self.player.current_room.has_item(item):
                    buffer.add(self.dungeon_items[item].describe())                            
                elif item == 'door' or item in self.player.current_room.doors:
                    if len(self.player.current_room.doors)>0:                            
                        for door in self.player.current_room.doors:
                            door_key = door.replace('_',' ')
                            buffer.add(self.dungeon_items[door_key].describe())
                    else:
                        buffer.add("There's no door here.")
                elif item == 'room':                                
                    buffer.add(self.player.current_room.describe())                            
                else:                            
                    buffer.add(self.player.look_item(item))
                return buffer.send()
            # Look up or down (currently not used)
            elif nextcmd in ['up','down']:
                buffer.add("You don't see anything important")
                return buffer.send()
            
            # Look in a particular direction
            elif nextcmd in self.directions:
                if 'look_'+nextcmd in vars(self.player.current_room):
                    match nextcmd:
                        case 'north':
                            buffer.add(self.player.current_room.look_north)
                        case 'south':
                            buffer.add(self.player.current_room.look_south)
                        case 'east':
                            buffer.add(self.player.current_room.look_east)
                        case 'west':
                            buffer.add(self.player.current_room.look_west)
                        case _:
                            buffer.add(self.player.current_room.describe())
                elif self.player.current_room.hasExit(nextcmd):
                    buffer.add('There appears to be a way to go '+nextcmd+' from here')
                else:
                    buffer.add("You don't see anything of interest in that direction")
                return buffer.send()
            
            # Look at the room
            elif nextcmd in ['room','here']:
                buffer.add(self.player.current_room.describe())
                return buffer.send()
            
            # Look at an NPC, item, room, or corpse
            else:
                nextcmd = phrase                        
                if self.player.current_room.isNPC(nextcmd):
                    buffer.add(self.monsters[nextcmd].describe())
                elif self.player.current_room.has_item(nextcmd):
                    buffer.add(self.dungeon_items[nextcmd].describe())
                elif nextcmd == 'room':
                    buffer.add(self.player.current_room.describe())
                elif nextcmd == 'corpse' or not re.search('corpse',nextcmd)==None:
                    for itm in self.player.current_room.items:
                        if self.dungeon_items[itm].isType('corpse'):
                            buffer.add(self.dungeon_items[itm].describe())
                else:
                    buffer.add(self.player.look_item(nextcmd))                            
                return buffer.send()
        else:
            buffer.add(self.player.current_room.describe())
            return buffer.send()
    
    # Listen
    def listen(self,cmds):
        buffer = MessageBuffer()
        if len(cmds)>0:
            if cmds[0] == 'to':
                cmds.pop(0)
            if len(cmds)>0:
                
                # If there's someone in the room, show their response
                for npc in self.player.current_room.npcs:
                    if cmds[0]==npc:
                        buffer.add(self.monsters[npc].respond())                                    
                # Otherwise play default sound
                else:
                    target = " ".join(cmds)
                    buffer.add("You try listening to the "+target+", but don't hear anything.")
        else:
            buffer.add('You listen intently. You hear '+self.voices.get_line('sounds')+'.')
        
        return buffer.send()

    # Smell
    def smell(self,cmds):
        buffer = MessageBuffer()
        if len(cmds)>0:
            target = " ".join(cmds)
            if target in self.player.current_room.npcs:
                if 'smell_text' in vars(self.monsters[target]):
                    buffer.add('The '+target+' smells like '+self.monsters[target].smell_text)
                else:
                    buffer.add("The "+target+" doesn't have a noticeable scent.")
            elif self.player.has_item(target):
                if 'smell_text' in vars(self.dungeon_items[target]):
                    buffer.add('The '+target+' smells like '+self.dungeon_items[target].smell_text)
                else:
                    buffer.add("The "+target+" doesn't have a noticeable scent." )
            elif self.player.current_room.has_item(target):
                if 'smell_text' in vars(self.dungeon_items[target]):
                    buffer.add('The '+target+' smells like '+self.dungeon_items[target].smell_text)
                else:
                    buffer.add("The "+target+" doesn't have a noticeable scent.")
            elif target in ['room','place','cave','cavern']:
                if 'smell_text' in vars(self.player.current_room):
                    buffer.add('It smells like '+self.player.current_room.smell_text+' here')
                else:
                    buffer.add("It smells like most caves. A faint whiff bat guano mingled with damp moss, wet rocks, and a touch of mystery.")
            else:
                target = " ".join(cmds)
                buffer.add('It smells pretty much what you figured '+target+' would smell like.')
        else:
            if 'smell_text' in vars(self.player.current_room):
                buffer.add('It smells like '+self.player.current_room.smell_text+' here')
            else:
                buffer.add("It smells like most caves. A faint whiff bat guano mingled with damp moss, wet rocks, and a touch of mystery.")
        return buffer.send()
    
    # Eat
    def eat(self,cmds):
        buffer = MessageBuffer()
        if len(cmds)>0:
            thing = " ".join(cmds)     
            if thing in self.dungeon_items.keys():
                if self.dungeon_items[thing].isType('edible'):
                    if self.player.has_item(thing):                            
                        buffer.add(self.player.remove_item(thing))
                        buffer.add(self.dungeon_items[thing].eat_text)
                        if hasattr(self.dungeon_items[thing],'eat_script'):
                            buffer.add(self.dungeon_items[thing].parse(self.dungeon_items[thing].eat_script))
                    elif self.player.current_room.has_item(thing):
                        self.player.current_room.items.remove(thing)        
                        buffer.add(self.dungeon_items[thing].eat_text)
                        if hasattr(self.dungeon_items[thing],'eat_script'):
                            buffer.add(self.dungeon_items[thing].parse(self.dungeon_items[thing].eat_script))
                    else:                                         
                        buffer.add("You don't have "+addArticle(thing)+"!")    
                else:
                    buffer.add("You can't eat "+addArticle(thing)+"!")
            else:
                if not re.search('corpse',thing)==None:
                    for itm in self.player.current_room.items:
                        if self.dungeon_items[itm].isType('corpse') and self.dungeon_items[itm].isType('edible'):
                            buffer.add(self.dungeon_items[itm].eat_text)                                    
                            if hasattr(self.dungeon_items[itm],'eat_script'):
                                buffer.add(self.dungeon_items[itm].parse(self.dungeon_items[itm].eat_script))
                else:
                    buffer.add("You can't eat "+addArticle(thing))
        else:
            buffer.add('Eat what?')
        
        return buffer.send()
    
    # Drink
    def drink(self,cmds):
        buffer = MessageBuffer()
        if len(cmds)>0:
            thing = " ".join(cmds)
            if self.player.has_item(thing):
                if 'drink_text' in vars(self.dungeon_items[thing]):
                    buffer.add(self.dungeon_items[thing].drink_text)
                    buffer.add(self.dungeon_items[thing].parse(self.dungeon_items[thing].drink_effect))
                    buffer.add(self.dungeon_items[thing].parse(self.dungeon_items[thing].drink_script))
                else:
                    buffer.add("You can't drink "+addArticle(thing)+".")
            else:
                buffer.add("You don't have "+addArticle(thing)+" to drink.")                                            
        else:
            buffer.add('Drink what?')
        
        return buffer.send()

    # Use
    def use(self,cmds):
        buffer = MessageBuffer()
        if len(cmds)>0:
            thing = " ".join(cmds)
            if self.player.has_item(thing):
                if not thing in self.player.inventory:                            
                    buffer.add(self.player.pull_out_item(thing))
                if self.dungeon_items[thing].isType('key'):
                    if not self.player.current_room.doors == []:
                        buffer.add(self.player.current_room.parse('unlock door'))
                    elif thing in self.player.container_list:
                        for itm in self.player.container_list:
                            if hasattr(self.dungeon_items[itm],'unlock_key'):
                                if thing == self.dungeon_items[itm].unlock_key:
                                    buffer.add(self.dungeon_items[itm].unlock())
                                    return buffer.send()
                        buffer.add("The "+thing+" doesn't appear to unlock anything here")
                    else:
                        for itm in self.player.current_room.items:
                            if hasattr(self.dungeon_items[itm],'unlock_key') and self.dungeon_items[itm].unlock_key == thing:
                                buffer.add(self.dungeon_items[itm].unlock())
                                buffer.add(self.dungeon_items[itm].open())
                                return buffer.send()
                                
                else:
                    buffer.add(self.dungeon_items[thing].activate())
            elif self.player.has_possible_matches(thing):
                buffer.add("Which one? You have multiple "+thing+"s.")
            else:
                buffer.add("You don't have "+addArticle(thing)+".")
            
        else:
            buffer.add('What are you trying to use?')
        
        return buffer.send()

    # Open
    def open(self,cmds):
        buffer = MessageBuffer()
        if len(cmds)>0:
            thing = cmds.pop(0)
            phrase = " ".join(cmds)
            if self.player.has_item(thing) or self.player.current_room.has_item(thing):                       
                if self.dungeon_items[thing].isKind('container') or self.dungeon_items[thing].isKind('lockbox'):
                    item = self.dungeon_items[thing]
                    if hasattr(item,'unlock_key') and item.isLocked():
                        if item.unlock_key in self.player.inventory:
                            buffer.add('You think you might have something that could unlock this.')
                        else:
                            buffer.add("You don't seem to have the right key for the "+thing+".")
                    else:
                        buffer.add(self.dungeon_items[thing].open())
                else:
                    buffer.add("The "+thing+" isn't a container.")   
            elif thing == 'corpse':
                for itm in self.player.current_room.items:
                    if self.dungeon_items[itm].isType('corpse'):
                        buffer.add("It's gruesome work, but you carve open a hole in the side of the "+itm+".")
                        buffer.add(self.dungeon_items[itm].open())

            elif thing == 'door' or not re.search('door',phrase)==None:
                if hasattr(self.player.current_room,'doors') and self.player.current_room.isLit() or self.player.has_light():
                    num_doors = len(self.player.current_room.doors)
                    if num_doors==1:
                        door_key = self.player.current_room.doors[0].replace('_',' ')
                        buffer.add(self.dungeon_items[door_key].open())
                    elif num_doors>1:
                        buffer.add('Which door are you trying to open?')
                    else:
                        buffer.add("There's no door here anymore")
                else:
                    buffer.add("You can't find a door to open.")
            else:
                buffer.add("You don't see "+addArticle(thing)+" here to open")                 
        else:
            buffer.add('What are you trying to open?')
        
        return buffer.send()
    
    # Close
    def close(self,cmds):
        buffer = MessageBuffer()
        if len(cmds)>0:
            phrase = " ".join(cmds)
            thing = cmds.pop(0)
            if self.player.has_item(thing) or self.player.current_room.has_item(thing): 
                if self.dungeon_items[thing].isKind('container') or self.dungeon_items[thing].isKind('lockbox'):
                    buffer.add(self.dungeon_items[thing].close())
                else:
                    buffer.add("The "+thing+" isn't a container.")   
            
            elif thing == 'door' or not re.search('door',phrase)==None:
                if hasattr(self.player.current_room,'doors') and self.player.current_room.isLit() or self.player.has_light():
                    num_doors = len(self.player.current_room.doors)
                    if num_doors==1:
                        door_key = self.player.current_room.doors[0].replace('_',' ')
                        buffer.add(self.dungeon_items[door_key].close())
                    elif num_doors>1:
                        buffer.add('Which door are you trying to close?')
                    else:
                        buffer.add("There's no door here anymore")
                else:
                    buffer.add("You can't find a door to close.")
            else:
                buffer.add("You don't see "+addArticle(thing)+" here to close")                 
        else:
            buffer.add('What are you trying to close?')
        return buffer.send()
    
    # Unlock an item or door
    def unlock(self,cmds):
        buffer = MessageBuffer()
        if len(cmds)>0:
            phrase = " ".join(cmds)
            thing = cmds.pop(0)
            if self.player.has_item(thing) or self.player.current_room.has_item(thing):
                if self.dungeon_items[thing].isKind('container') or self.dungeon_items[thing].isKind('lockbox'):
                    item = self.dungeon_items[thing]
                    if hasattr(item,'unlock_key') and item.isLocked():
                        if item.unlock_key in self.player.inventory:
                            buffer.add(item.unlock())
                            buffer.add("Now that the "+thing+" is unlocked, you can probably open it")
                        else:
                            buffer.add("You don't seem to have the right key for the "+thing+".")
                    else:
                        buffer.add("It doesn't appear to be locked.")
                        buffer.add(self.dungeon_items[thing].open())
                else:
                    buffer.add("The "+thing+" isn't a container.")       
            elif thing == 'door' or not re.search('door',phrase)==None:
                if hasattr(self.player.current_room,'doors') and self.player.current_room.isLit() or self.player.has_light():                                
                    num_doors = len(self.player.current_room.doors)
                    if num_doors==1:
                        door_key = self.player.current_room.doors[0].replace('_',' ')
                        buffer.add(self.dungeon_items[door_key].unlock())
                    elif num_doors>1:
                        buffer.add('Which door are you trying to unlock?')
                    else:
                        buffer.add("There's no door here anymore")
                else:
                    buffer.add("You don't see a door to unlock")
            else:
                buffer.add("There's no "+phrase+" to unlock.")
        else:
            buffer.add("What are you trying to unlock")                 
        return buffer.send()
    
    # Lock an item or door
    def lock(self,cmds):
        buffer = MessageBuffer()
        if len(cmds)>0:
            phrase = " ".join(cmds)
            thing = cmds.pop(0)
            if thing in self.player.inventory or thing in self.player.current_room.items:
                if self.dungeon_items[thing].kind in ['container','lockbox']:
                    item = self.dungeon_items[thing]
                    if hasattr(item,'unlock_key') and not item.isLocked():
                        if item.unlock_key in self.player.inventory:
                            buffer.add(item.lock())
                        else:
                            buffer.add("You don't seem to have the right key for the "+thing+".")
                    else:
                        buffer.add("It's already unlocked!")     
                else:
                    buffer.add("The "+thing+" isn't a container.")                            
            elif thing == 'door' or not re.search('door',phrase)==None:
                if hasattr(self.player.current_room,'doors') and self.player.current_room.isLit() or self.player.has_light():
                    num_doors = len(self.player.current_room.doors)
                    if num_doors==1:
                        door_key = self.player.current_room.doors[0].replace('_',' ')
                        buffer.add(self.dungeon_items[door_key].lock())
                    elif num_doors>1:
                        buffer.add('Which door are you trying to lock?')
                    else:
                        buffer.add("There's no door here anymore")
                else:
                    buffer.add("You can't find a door to lock.")                
                
            else:
                buffer.add("You don't see "+addArticle(thing)+" here to lock")                 
        else:
            buffer.add('What are you trying to lock?')
        return buffer.send()

    # Search
    def search(self,cmds):
        buffer = MessageBuffer()
        if len(cmds)>0:
            location = " ".join(cmds)
            isContainer = False
            isLocked = False

            # Check if location is one of the valid hidden locations
            if 'hidden_spots' in vars(self.player.current_room):
                if self.player.current_room.hidden_state=='not found':
                    if location in self.player.current_room.hidden_spots:
                        buffer.add(self.player.current_room.show())
                        self.player.current_room.hidden_state='found'
                        return buffer.send()
                    else:
                        buffer.add('You feel you might be onto something, just not here.')
                        return buffer.send()
                else:
                    buffer.add("You try again, but don't find anything")
                    return buffer.send()
            
            elif location in self.player.current_room.items and self.dungeon_items[location].kind in ['containers','lockbox']:
                if not self.dungeon_items[location].isLocked():
                    buffer.add(self.dungeon_items[location].open())
                    
                else:
                    buffer.add('The '+location+' is locked. There must be some way to unlock it.')
                    isLocked = True

                isContainer = True

            # Search corpses (works in most cases, but not where there is a hidden spot)
            elif location == 'corpse':
                for itm in self.player.current_room.items:
                    if self.dungeon_items[itm].isType('corpse'):
                        if self.dungeon_items[itm].isClosed():
                            buffer.add("It's gruesome work, but you carve open the "+itm+".")
                            buffer.add(self.dungeon_items[itm].open())
                        else:
                            buffer.add(self.dungeon_items[itm].spill())
                        isContainer = True
            else:
                match location:
                    case self.player.current_room: 
                        if 'hidden' in vars(self.player.current_room) and self.player.current_room.hidden_state=='not found':
                            buffer.add(self.player.current_room.show())
                            self.player.current_room.hidden_state='found'
                        else:
                            buffer.add("You don't find anything of interest")                
                    
                    case _:
                        if not isContainer or not isLocked:
                            buffer.add("You don't find anything of interest")
        else:
            if 'hidden' in vars(self.player.current_room) and self.player.current_room.hidden_state=='not found':
                buffer.add(self.player.current_room.show())
                self.player.current_room.hidden_state='found'
            else:
                buffer.add("You don't find anything of interest")
        
        return buffer.send()


    # Combat Management (Handle fights between player and monsters)
    def attack(self,target,special='weapon'):
        buffer = MessageBuffer()
        if target in self.monsters.keys():
            monster = self.monsters[target]
            if monster.HP>0:
                buffer.add(self.player.attack(target,special))
            else:
                buffer.add('The '+monster.name+' is already dead. Why are you still attacking the corpse?')
        elif target in self.player.current_room.items:
            buffer.add("You attack the "+target+" but fail to cause any damage.")

        elif target=='self' or target=='myself':
            buffer.add("Although things look pretty bleak, you resist the urge. Maybe the next room will be better?")

        else:
            buffer.add('There is no '+target+' here to attack.')
        return buffer.send()

    # Kick someone
    def kick(self,cmds):
        buffer = MessageBuffer()
        if len(cmds)>0:
            target = ' '.join(cmds)
            if target in self.player.current_room.npcs:
                buffer.add(self.attack(target,'foot'))
            elif target in self.player.current_room.items:
                buffer.add("You kick the "+target+" and break your toe. That didn't go as planned.")
                isKilled = self.player.take_damage(1)
                if isKilled:
                    buffer.add("You died! Well, that was embarrassing. You didn't expect to kick yourself to death")
                    buffer.add(self.death('You were killed while trying to kick the '+target))   # Send player immediately to Bad Ending
            else:
                buffer.add("You kick at the "+target+", but fail to deal any damage, except to your own pride")
        elif len(self.player.current_room.npcs)==1:
            target = self.player.current_room.npcs[0]
            buffer.add(self.attack(target,'foot'))
        else:
            buffer.add('Who or what are you trying to kick?')
        return buffer.send()
    
    # Punch someone
    def punch(self,cmds):
        buffer = MessageBuffer()
        if len(cmds)>0:
            target = ' '.join(cmds)
            if target in self.player.current_room.npcs:
                buffer.add(self.attack(target,'fist'))
            elif target in self.player.current_room.items:
                buffer.add("You punch the "+target+". Nothing happens, other than you breaking your finger nails.")
                isKilled = self.player.take_damage(1)
                if isKilled:
                    buffer.add("You died! Well, that was embarrassing. You didn't expect to punch your way into an early grave")
                    buffer.add(self.death('You were killed while punching the '+target+'. How sad is that!'))   # Send player immediately to Bad Ending
            else:
                buffer.add("You punch the "+target+". Surprisingly, it doesn't punch back.")
        elif len(self.player.current_room.npcs)==1:
            target = self.player.current_room.npcs[0]
            buffer.add(self.attack(target,'fist'))
        else:
            buffer.add('Who or what are you trying to punch?')       
        return buffer.send()

    # Reset Game Environment
    def reset_game_environment(self):
    # Load Global Lookup Tables (dictionaries) for game.monsters, items, rooms, and sounds/dialog
        for monster in self.monsters.keys():
            self.monsters[monster].reset()
        for room in self.dungeon_rooms.keys():
            self.dungeon_rooms[room].reset()
        for item in self.dungeon_items.keys():
            self.dungeon_items[item].reset()
        
        self.player.reset()
    
# Create Global Game 
game = Console()
game.player.start()