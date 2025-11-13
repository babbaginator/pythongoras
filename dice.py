# Dice

# ==========================================================================
# STRING FORMATTING FOR ABILITY SCORES - Convert signed number to string mod; 
# determine ability score modifier to display
# ==========================================================================

def mod_to_str(mod):
    rollmod = ''
    if mod > 0:
        rollmod = '+'+str(mod)
    elif mod < 0:
        rollmod = str(mod)
    else:
        rollmod = '0'
    return rollmod

def get_stat_mod(value):
    mod = int(value)-10
    if mod<0:
        mod = int((mod-0.5)//2) 
    else:
        mod = mod//2
    return mod

# ==========================================================================
# DIE = Simulates a multi-sided die
# ==========================================================================
class Die:
    def __init__(self,sides= 6):
        self.name = "d"+str(sides)
        self.sides = int(sides)
        self.value = 0
    
    def roll(self):
        import random
        self.last = self.value
        self.value = random.randint(1,self.sides)
        return self.value
    

# ==========================================================================
# DICEROLLER = Manages dice rolling of different types of dice.
# ==========================================================================
class DiceRoller:
    def __init__(self):
        self.name = 'Dice Roller'
        self.value = 0

    def parse(self,dicestring):        
        sign = 1
        ind = dicestring.find('+')    
     
        # If doesn't have + sign, check for - sign
        if ind == -1:
            sign = -1
            ind = dicestring.find('-')
            
            # If doesn't have + or -, then ignore whatever is after the xdy format
            if (ind== -1):
                sign = 0
                
        pos = dicestring.find('d')        

        if pos>-1:
            num = int(dicestring[0:pos])
            if sign == 0:
               dsize = int(dicestring[pos+1:]) 
               result = self.roll_dice(dsize,num)
            else:
                dsize = int(dicestring[pos+1:ind])
                result = self.roll_dice(dsize,num)+sign*int(self.parse(dicestring[ind+1:]))            
        else:
            result = int(dicestring[0:])
        return str(result)

    def roll_dice(self,dSize=6,num=1):
        die = Die(dSize)
        result=0
        for i in range(0,num):
            result = result + die.roll()
        return result     

    def roll(self,dicestring):
        return self.parse(dicestring)

    def d20(self,mod=0):       
        return self.roll("1d20"+mod_to_str(mod))

    def d12(self,mod=0):       
        return self.roll("1d12"+mod_to_str(mod))

    def d10(self,mod=0):       
        return self.roll("1d10"+mod_to_str(mod))

    def d8(self,mod=0):       
        return self.roll("1d8"+mod_to_str(mod))
    
    def d6(self,mod=0):       
        return self.roll("1d6"+mod_to_str(mod))
    
    def d4(self,mod=0):       
        return self.roll("1d4"+mod_to_str(mod))

# ==========================================================================
# ABILITY = Class for generating, managing, and displaying ability scores
# ==========================================================================
class Ability:
    def __init__(self,sname):
        self.name = sname;
        self.value = DICE.roll("3d6")
        self.mod = get_stat_mod(self.value)

    def roll(self):
        self.value = DICE.roll("3d6")
        self.mod = get_stat_mod(self.value)

    def set_stat(self,fscore=10):        
        if fscore>0 and fscore<=30:
            self.value = fscore
        self.mod = get_stat_mod(self.value)

    def print(self):
        result = self.name+" "+str(self.value)+" ("+mod_to_str(self.mod)+")"
        return result
       
    def dump(self):
        print(self.print())

# ==========================================================================
# STATBLOCK = Displays standard range of ability scores
# ==========================================================================
class StatBlock:
    def __init__(self):
        self.stats = ["STR","DEX","CON","INT","WIS","CHA"]
        self.scores = {}
        for stat in self.stats:
            self.scores[stat] = Ability(stat)

    def reroll(self):
        for x in vars(self.scores):
            self.scores[x].roll()
    
    def print(self):
        result = ''
        for x in self.stats:
            result = result+self.scores[x].print()+'\n'
        return result

    def dump(self):
        print(self.print())

# ==========================================================================
# CHARACTER = NPC Character 
# ==========================================================================
class Character:
    def __init__(self,name):
        self.name = name
        

# ==========================================================================
# PLAYER = Player character, the avatar that the player uses to experience 
# the world of the game
# ==========================================================================
class Player:
    def __init__(self):
        self.abilities = StatBlock()
        self.defense = 10 + int(self.abilities.scores["DEX"].mod)
        self.to_hit = int(self.abilities.scores["STR"].mod)
        self.weapon = "fist"
        self.armor = "none"

    def getScore(self,key="STR"):
        return int(self.abilities.scores[key].value)

    def getMod(self,key="STR"):
        return int(self.abilities.scores[key].mod)

    def print(self):
        result = self.abilities.print()+"\n"+"AC: "+str(self.defense)+"\n"+"Weapon ("+self.weapon+"): "+str(self.to_hit)
        return result

# ==========================================================================
# GLOBALS
# ==========================================================================

DICE = DiceRoller()

# ==========================================================================
# MAIN PROGRAM
# ==========================================================================
        
