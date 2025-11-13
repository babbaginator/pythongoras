## The Lost Temple of Pythongoras
A Text Adventure 
by Neil, Coco, and Daniel
Created Summer 2024

#### Project Description:
_The Lost Temple of Pythongoras_ is a text-based adventure game in the tradition of some of the earliest computer games such as _Zork_ and _The Colossal Cave Adventure_.  You find yourself in a mysterious subterranean temple, which you must escape, ideally with some treasure under your belt.  Over the course of the game you will solve puzzles, combat monsters, and discover strange and sometimes useful items. 

#### Technical Requirements:
Playing this game requires Python 3.10 or later to be installed. To play, navigate to the game folder and type "python main.py" (or doubleclick main.py). The folder should also contain the utility.py and dialog.py files which provide additional support functionality. Please preserve the original locations and contents of the files in the "data" folder – moving or altering them may make  the game unplayable.  

> **main** (for main.py and other python files)
>> **data** (general config files for items.txt, monsters.txt, rooms.txt, dialog.txt)
>>> **items** (individual data files) 
>>> **monsters** (individual data files)
>>> **rooms** (individual data files)

#### General Gameplay:  
"The Lost Temple of Pythongoras" functions through text-based description and interaction.  In each room you enter, you will be given a description of the room and its contents.  You interact with these features by typing commands into the command-parser, which interprets them and carries out your actions.

Commands generally take the form of a verb and its object.  For example, to pick up a sword, you can say "get sword".  Articles (like "the" or "a") and prepositions (such as "to" or "in") are not necessary – a command such as "look sword" is perfectly acceptable.  

The command parser has a large, but not infinite vocabulary.  The commands it recognizes are listed at the end of this document.  

Try to combine as many commands and objects as you can – the results may be entertaining, and might even also be useful!

#### Features:
The game engine and object scripting supports the following features:
- **basic navigation and interaction commands** which include directional moving, as well as looking, using, and otherwise interacting with the world
- **containers** that can be opened and closed and their contents listed
- **piles** that allow the player to take an item from a pile without removing the pile
- **doors** that can be opened, closed, locked, unlocked, or support a variety of trigger scripts
- **consummables** like potions or edible moss that can be used and will remove themselves from the inventory
- **light/dark** in different areas of the dungeon which means that some things cannot be seen or done without a light source
- **combat simulation** that uses a virtual die roll, relies on player, monster, and weapon stats, and handles critical hits
- **hidden items** that can only be found through searching
- **readable items and environment details** that can be read by the player and are defined in external files
- **directional looking** when the player looks in different directions, they are given a description of what they see in that direction
- **puzzles with multiple solutions** as defined in the external text file for that room or item. A list of valid solution commands is provided so that if the player uses any of them, they trigger the solution script
- **highly flexible object scripting** which allows exits to be added or removed, attributes to be modified, flags set, phrases printed to the screen, items added or removed, or other scripts to be run
- **simple conversations with npcs** that allows the player to talk to creatures and humanoids and ask or say different things. Responses are defined externally, but through regex, answers can be somewhat on topic.


#### Inventory:
Items that you pick up are added to your inventory, an expandable list of what you are carrying.  Items in your inventory can be interacted with using all the normal game commands – once again, try as much as you can!  

#### Combat:
Combat in this game is based roughly upon the rules of 5th edition Dungeons and Dragons.  Both the player character and any other characters/monsters have the same four attributes:  hit points, representing how much health they have;  armour class, representing how easy it is to hit them;  attack bonus, which represents how good you are at hitting targets, and damage score, representing how much damage is done to the enemy.  

When combat is initiated using the "fight" command, the player makes an attack.  The game "rolls a d20" (that is, generates a random number between 1 and 20), and adds the player’s attack bonus to that result.  If the total is equal to or more than the monster’s armour class, the attack hits, and the player does damage equal to their current weapon’s damage score.  

After the player’s attack, the enemy then makes an attack in the same way – a random number is generated, and its attack bonus is added;  if it is greater than or equal to the player’s AC, the attack hits and it does its damage.  
If either the player’s or the monster’s HP are 0 or less, they die.  

Various items in the game can change your HP, AC, attack bonus and damage;  your current numbers in these categories can be found using the "stats" command.  

#### The Team:
This game was created by Neil Aitken, Coco Chen, and Daniel Unruh in the summer of 2024 as part of a Python coding class at the University of British Columbia School of Information.  Questions, suggestions, or bug reports can be sent to any of the developers.

* Neil: neil.aitken@gmail.com
_Command Parser, Object Script Interpreter, Engine Architecture_
* Coco:
 _Map Layout, Rooms and Navigation_
* Daniel:  daniel.unruh@cantab.net
_Monsters, Items, Puzzles_

#### Future Plans
In terms of the game, we hope to increase the number of rooms, monsters, npcs, and items, as well as creating a more complicated labyrinth to explore. We can leverage the existing code, parser, and object script language to add more content for the current game. However, this project might also be thought of operating as something of a prototype for a general text adventure game engine. 

To turn what we have into a full game engine would likely require a careful rebuild geared toward making the objects more encapsulated and less reliant on global variables. Such a substantial rewrite goes beyond the scope of this class, but might be a fun project to either pursue independently or as an open source project on GitHub.

----

### Appendix A – Game Commands:
_The Lost Temple of Pythongoras_ has 48 commands (12 are aliases)
- north / n – move north
- west / w – move west
- east / e – move east
- south / s – move south
- about – gives a brief introduction to the game
- attack / fight / hit - initiates combat with any other creatures in the area
- ask __ about __ – prompts a character to respond about the input subject.
- close - close a container or a door
- commands – gives a list of commands
- drink – drink an object (if it is drinkable)
- drop / leave – remove an object from your inventory and place it in the room
- eat – eat an object (if it is edidble)
- exits - list all known exits from this room
- get / take – take an object from the room and add it to your - inventory
- help – offers introductory guidance for the game
- hint – gives a hint about how you might solve your current puzzle
- inventory / inv – lists what you are currently carrying
- kick - attack enemy using feet instead of normal weapon
- kiss – give someone or something a smooch
- light - light a light source that you are carrying
- listen – concentrate on trying to hear something
- look / examine – inspect something;  without an object, it will describe the room you are in. can look at objects that are inside of containers you are carrying
- lock - lock a door or lockable container (eg. a chest)
- open - open a container (if not locked) and look inside. can also open corpses and doors.
- punch - attack enemy using your fist instead of normal weapon
- put / place x in y- put an item inside of a specified container
- quit / done / exit – quit the game
- read – read a text
- say – speak a word or phrase;  for example "say potato" means your character will say the word potato out loud
- search – look for anything hidden in your environment
- smell – give something a sniff
- stats – show your current and max hit points (HP), armour class (AC), and attack bonus
- stuck - offers more advice about what to do when you're stuck and don't know what else to try
- talk – initiate a conversation with someone or something
- unlock - unlock a door or lockable container if you have the right key
- use – activate an item, to bring forth its special properties

### Appendix B - Object Script Commands:
Items and Rooms can have scripts in their config files that will be run when certain conditions are met. These are the basic commands that are available. Multiple commands can be given in a line, provided they are separated with a ';'. Any lines in a config file can be disabled by prefixing it with a '#' - which causes the item or room to ignore that line when read during the load call.
- **add** _attribute_ _value_ - increment the attribute by the integer amount in value. The script parser checks to see if attribute belongs to the _item_, if not checks to see if _player_ has that attribute, and failing that, checks to see if the current _room_ has that attribute.
- **add_key** _attribute_ _value_ - add a new key to a dictionary-type _dictname_ in the item, the player, or the current room and assign it a _key:value_ entry. If there is no attribute by that name, create a new dictionary named _dictname_ in the item and assign it a dictionary containing the entry _key:value_
- **append** _attribute_ _value_ - append the _value_ to a list-type _attribute_ in the item, the player, or the current room. If there is no attribute by that name, create a new _attribute_ in the item and assign it a list containing _value_
- **boost** _attribute_ _value_ - increment the _attribute_ in player by the integer amount in value. If the attribute does not exist, create it and assign it the boost value.
- **print** _msgLocation_ - prints the string stored in _msgLocation_
- **remove** _attribute_ _value_ - remove the _value_ from a list-type _attribute_ in the item, the player, or the current room. If there is no attribute by that name, create a new _attribute_ in the item and assign it an empty list
- **run** _target_ _scriptlocation_ - Runs a script stored in _scriptlocation_ (another entry or attribute in the object or datafile) on the _target_ which could be ("here" or "current_room") or the name of a monster, room, or item. The name in _scriptlocation_ is used to index into dungeon_items, dungeon_rooms, or monsters.
- **set** _attribute_ _value_ - sets item attribute to value (integer or string)
- **set** _attribute_ to _string_ - sets item attribute to the contents of another attribute in the item (eg. _set long_description to solved_description_)
- **sub** _attribute_ _value_ - decrement the attribute by the integer amount in value. The script parser checks to see if attribute belongs to the _item_, if not checks to see if _player_ has that attribute, and failing that, checks to see if the current _room_ has that attribute.
