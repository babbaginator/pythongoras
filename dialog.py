# Dialog Manager
import os

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
def res_path(relative_path):
    import sys
    if hasattr(sys,'_MEIPASS'):
        return os.path.join(sys._MEIPASS,os.path.join(ASSETS_DIR,relative_path))
    return os.path.join(ASSETS_DIR, relative_path)

class DialogFile:
    def __init__(self,name):
        self.name = name
        self.dialoglines = []
        filename = os.path.join('data','dialog',name)
        self.load(filename)
        
    
    def load(self,filename):
        try:            
            lines = open(res_path(filename),'r')
            for line in lines:
                if not line.startswith('#') and not line=='\n':  # Ignore comments and empty lines
                    if line.find('=') == -1:
                        self.dialoglines.append(line.strip())                    
                    else:
                        key,value=line.split('=')
                        phrases = value.strip().split(',')                    
                        setattr(self,key.strip(),phrases)
        except:
            print(f'File read error: {filename} does not exist')     

    def get_line(self):
        import random            
        if len(self.dialoglines)>0:
            index=random.randint(0,len(self.dialoglines))-1
            return self.dialoglines[index]
        else:
            return None        

class DialogManager:
    def __init__(self,name):
        self.name = name
        self.dialogs = {}
        filename = os.path.join('data',name+'.txt')
        self.load(filename)
        
    
    def load(self,filename):
        try:
            lines = open(res_path(filename),'r')
            for line in lines:
                if not line.startswith('#') and not line=='\n':  # Ignore comments and empty lines
                    key, value = line.split('=')             
                    dlglist = DialogFile(value.strip())
                    self.dialogs[key]=dlglist              
        except:
            print(f'File read error: {filename} does not exist')            
    def get_line(self,dlg):
        if dlg in self.dialogs.keys():
            return self.dialogs[dlg].get_line()
        else:
            return self.dialogs['default'].get_line()
