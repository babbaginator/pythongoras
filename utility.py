# LIBR 559 - Final Project
# GAME
# Team: Coco, Daniel, Neil

# =============================================================
# Utility functions
# =============================================================
def addArticle(st):
    import re
    pieces = ['moss','ice','soap','cloth','fabric','paper','music','glass','wood']
    plurals = ['water','blood','soup','gravy']
    if st in pieces:
        return 'a piece of '+st
    
    if st in plurals:
        return 'some '+st
    
    if re.match(r'[aeiou]',st):
        result = "an "+st
    else:
        result = "a "+st
    return result

def roll(diesize=20,modifier=0):
    import random    
    return random.randint(1,diesize)+modifier

def choose(arr):
    import random    
    if not arr == []:
        return arr[random.randint(0,len(arr))-1]
    else:
        return None

# Creates a comma separated list of items then puts the last one on with an 'and' (eg. 'stone, bark, frog, and knife')
def get_list_as_string(things):
    itmlist = ''
    if len(things)==1:
        return addArticle(things[0])
    elif len(things)==2:
        return addArticle(things[0])+' and '+addArticle(things[1])
    else:
        for itm in things[:-1]:
            itmlist = itmlist + addArticle(itm)+', '
        else:
            itmlist = itmlist + "and "+addArticle(things[-1])
    return itmlist

def searchDict(ikey, ivalue, test_list):
    for entry in test_list.keys():
        if getattr(test_list[entry],ikey)==ivalue:
            return test_list[entry]
    return None

def hasDictKey(key,value,test_list):
    print(f'key {key} value {value} list {test_list}')
    for element in test_list.items():
        if getattr(element[1],key)==value:
            return True
    return False


def get_multiline_from_str(text,width):
    paragraphs = text.split('\n')
    lines = []
    for para in paragraphs:
        if len(para)>width:
            i = para[0:width].rfind(' ')
            if i>0:
                lines.append(para[0:i])
                lines = lines+get_multiline_from_str(para[i+1:],width)
            else:
                lines.append(para[0:width])
                lines = lines+get_multiline_from_str(para[width+1:],width)
        else:
            lines.append(para)
    return lines

def get_multiline_from_list(linelist,width):
    lines = []
    for line in linelist:
        lines = lines + get_multiline_from_str(line,width)
    return lines

def add_padding(width):
    msg =''
    for i in range(width):
        msg = msg+' '
    return msg

# =============================================================
# Create box around text 
# =============================================================
def getBoxBorder(length=60):
    msg = ""
    for i in range(length):
        msg = msg +"="
    return msg

def getBoxLine(length=60):
    result = "|"
    for i in range(length-2):
        result = result +" "
    result = result+"|"
    return result

def getBoxText(msg,padding=4,offset=""):
    pad = ""
    for i in range(padding):
        pad = pad + " "
    #result = "|"+pad+msg+pad+offset+"|"
    result = pad+msg+pad+offset
    return result
    
def boxed(msg,padding=4):
    boxwidth = len(msg)+2*padding+2
    boxheight = 2*padding+msg.count('/n')
    print(getBoxBorder(boxwidth))
    print(getBoxLine(boxwidth))
    print(getBoxText(msg,padding))
    print(getBoxLine(boxwidth))
    print(getBoxBorder(boxwidth))

def bigboxed(msg,maxwidth=60):
    lines = msg.split('|')
    padding = 4
    boxwidth = maxwidth+2
    boxheight = 2*padding+len(lines)
    print(getBoxBorder(boxwidth))
    print(getBoxLine(boxwidth))
    for line in lines:
        gap = maxwidth-len(line)
        padding = int(gap/2)
        offset=''
        if gap%2>0:
            offset=' '
        print(getBoxText(line,padding,offset))        
    print(getBoxLine(boxwidth))
    print(getBoxBorder(boxwidth))

def box_msg(msg,maxwidth=50):
    log = []
    lines = msg.split('|')
    padding = 4
    boxwidth = maxwidth+2
    
    #log.append(getBoxBorder(boxwidth))
    #log.append(getBoxLine(boxwidth))
    for line in lines:
        gap = maxwidth-len(line)
        padding = int(gap/2)
        offset=''
        if gap%2>0:
            offset=' '
        log.append("[READ]"+getBoxText(line,padding,offset))        
    #log.append(getBoxLine(boxwidth))
    #log.append(getBoxBorder(boxwidth))
    result = "\n"+"\n".join(log)
    return result

# =============================================================

