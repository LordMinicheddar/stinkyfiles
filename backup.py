print("""                 _                                                      __________        .__        ___________                      
                                                                        \______   \_____  |  |   ____\__    ___/______  ____   ____  
                                                                        |     ___/\__  \ |  |  /     \|    |  \_  __ \_/ __ \_/ __ \ 
                                                                        |    |     / __ \|  |_|  Y Y  \    |   |  | \/\  ___/\  ___/ 
                                                                        |____|    (____  /____/__|_|  /____|   |__|    \___  >\___  >
                                                                                        
                                ;`',
                                `,  `,                                                               
                                ',   ;   ,,-""==..,
                                \    ','          \ v                                                           
                        ,-""'-., ;    '    __.-="-.;
                        ," ,,_    "V      _."
                    ;,'   ''-,          "=--,_
                            ,-''    _  _       `,
                            /   ,.-+(_)(_)´--.,   ;
                            ,'  /   ; (_)       `\ ,
                            ; ,/    ;._.;         ;
                            !,'     ;   ;
                            V'      ;   ;
                                    ;._.;
                                    ;   ;
                                    ;   ;        ~
                    ~              ;._.;
                            ~    ;   ;
                                .´   `.                ~
                            __,.--;.___.;--.,___
                    _,,-""      ;     ;       ""-,,_
                .-´´            ;     ;             ``-.
                ",              ´       `               ,"        ~
                    "-_                                _-"
                ~       ``----..,_          __,,..---´
                                ```''''´´´                  ~
                                            ~
                            ~                                                                                                                                          """)




print("--------------------------------------------------------------------------------------------------------------------------------------------------")


print(""" __      __       .__                           __           __________        .__            ___________                      
/  \    /  \ ____ |  |   ____  ____   _____   _/  |_  ____   \______   \_____  |  |   _____   \__    ___/______   ____   ____  
\   \/\/   // __ \|  | _/ ___\/  _ \ /     \  \   __\/  _ \   |     ___/\__  \ |  |  /     \    |    |  \_  __ \_/ __ \_/ __ \ 
 \        /\  ___/|  |_\  \__(  <_> )  Y Y  \  |  | (  <_> )  |    |     / __ \|  |_|  Y Y  \   |    |   |  | \/\  ___/\  ___/ 
  \__/\  /  \___  >____/\___  >____/|__|_|  /  |__|  \____/   |____|    (____  /____/__|_|  /   |____|   |__|    \___  >\___  >
       \/       \/          \/            \/                                 \/           \/                         \/     \/ """)


print("--------------------------------------------------------------------------------------------------------------------------------------------------")


print("""
What would you like to do:
[1] Adventure text game...
[2] Rock Paper scisors...
[3] Calculator...
[4] POOP...
""")
choice = input("")
if choice == "1" :
   print("You have selected" " " "[Aventure Text Game]")
   print('')
elif choice == "2" :
   print("You have selected" " " "[Rock,Paper,Scisors]")
   print('')
elif choice == "3" :
   print("You have selected" " " "[Calculator]")
   print('')
   
elif choice == "4" :
   print("You have selected" " " "[poop]")
   print('')
   
#-----------------------------------------------------Adventure Game--------------------------------------------------------------------------------------------
if choice == "1":
   


   weapon = False

def strangeCreature():
  actions = ["fight","flee"]
  global weapon
  print("You come across one of the Black Sovereigns enforcers his name is Kaelith. He stands at an imposing height of 6'5, with a lithe yet muscular build honed for agility and strength. His eyes are an eerie, glowing silver, reflecting the souls he has claimed and the dark magic that courses through his veins. He wears a suit of dark prism armour that blends seamlessly into the shadows, adorned with runic symbols that pulse with a faint, malevolent light. Once a proud knight of the Luminar Order, Kaelith was betrayed by those he trusted most. Left for dead in the depths of the Shadowfell, a realm of eternal twilight and malevolent spirits, he was found by an ancient, dark entity known as the Black Sovereign. In exchange for his life and a promise of vengeance, Kaelith swore his loyalty to the Black Sovereign, becoming one of the many enforcers in the mortal realm controlled by Black Sovereign. Now, he walks the line between life and death, bound by dark oaths and driven by a thirst for retribution.")
  userInput = ""
  while userInput not in actions:
    print("Options: flee/fight")
    userInput = input()
    if userInput == "fight":
      if weapon:
        print("You kill Kaelith with the acient dagger you found earlier. After moving forward, you find one of the exits. Congats!")
      else:
        print("The goul-like creature has killed you.")
      quit()
    elif userInput == "flee":
      showSkeletons()
    else:
      print("Please enter a valid option.")
      
def showSkeletons():
  directions = ["backward","forward"]
  global weapon
  print("You see a wall of skeltons as you walk into the room. Someone is watching you. Where would you like to go?")
  userInput = ""
  while userInput not in directions:
    print("Options: left/backward/forward")
    userInput = input()
    if userInput == "left":
      print("You find that this door opens into a wooden barricade. You samsh down the barricade to discover an acient dagger you take it, this will come in handy later.")
      weapon = True
    elif userInput == "backward":
      introScene()
    elif userInput == "forward":
      strangeCreature()
    else:
      print("Please enter a valid option.")
      

def hauntedRoom():
  directions = ["right","left","backward"]
  print("You hear strange voices. You think that these could be your freinds. Where would you like to go?")
  userInput = ""
  while userInput not in directions:
    print("Options: right/left/backward")
    userInput = input()
    if userInput == "right":
      print("Multiple goul-like creatures start emerging as you enter the room. You are killed.")
      quit()
    elif userInput == "left":
      print("You made it! You've found an exit.")
      quit()
    elif userInput == "backward":
      introScene()
    else:
      print("Please enter a valid option.")

def cameraScene():
  directions = ["forward","backward"]
  print("You see a burnt out torch that has been dropped on the ground. Someone has been here recently. Where would you like to go?")
  userInput = ""
  while userInput not in directions:
    print("Options: forward/backward")
    userInput = input()
    if userInput == "forward":
      print("You made it! You've found an exit.")
      quit()
    elif userInput == "backward":
      showShadowFigure()
    else:
      print("Please enter a valid option.")
      
def showShadowFigure():
  directions = ["right","backward"]
  print("You open the door to see a dark shadowy figure this must be one of the Black Sovereigns forces. You are scared. Where would you like to go?")
  userInput = ""
  while userInput not in directions:
    print("Options: right/left/backward")
    userInput = input()
    if userInput == "right":
      cameraScene()
    elif userInput == "left":
      print("You find that this door opens into a wall.")
    elif userInput == "backward":
      introScene()
    else:
      print("Please enter a valid option.")


def introScene():
  directions = ["left","right","forward"]
  print("You are in the main banquet hall there are four doors in each side of the hall theses lead to hallways which will take you to escape. Where would you like to go?")
  userInput = ""
  while userInput not in directions:
    print("Options: left/right/backward/forward")
    userInput = input()
    if userInput == "left":
      showShadowFigure()
    elif userInput == "right":
      showSkeletons()
    elif userInput == "forward":
      hauntedRoom()
    elif userInput == "backward":
      print("You find a trap door this takes you to the catacombs.")
    else: 
      print("Please enter a valid option.")

if choice == "1":
  while True:
    print("Welcome to the Adventure Game!")
    print("In the heart of the forsaken land of Eldrath, where the skies are eternally shrouded in bruised clouds and the soil is tainted with the blood of ancient battles, a sinister tale begins. The sun, long banished by an unforgiving curse, casts only the faintest ember of light upon the desolate landscape. Here, shadows stretch and twist like grasping fingers, and the air is thick with the whispers of tormented souls. Once, Eldrath was a realm of splendor, where towering spires reached towards the heavens and lush forests teemed with life. But that was before the coming of the Black Sovereign, a dread sorcerer who clawed his way from the depths of the Abyss, bringing with him a tide of darkness that swallowed the land. His cruel reign has turned Eldrath into a kingdom of nightmares, where the very essence of despair weaves through every breath taken by its cursed denizens. Amidst this bleakness stands the last bastion of hope: a crumbling fortress on the edge of the Abyss, where a band of unlikely heroes gather. Their faces are etched with the scars of past sorrows, their eyes flickering with the last sparks of defiance. Among them are warriors, outcasts, and mages, each driven by their own ghosts and secrets. They have been drawn together by a prophecy—a whisper carried by the winds of fate—that speaks of a hidden relic capable of breaking the Black Sovereign's grasp.But the path to redemption is fraught with peril. Beyond the fortress walls, the land is a twisted maze of forsaken ruins and haunted woods, where every shadow harbors a lurking menace. The once-proud cities are now graveyards of the living, overrun by fiends and twisted creatures that feed on fear. Rivers run black with the tears of the fallen, and the very trees seem to scream in agony.")
    print("You are a measly peasent with only a loin cloth to your name, however you have to escape the crumbaling fortress before the dark forces of the Black Sovereign destroy your home. You must leave adventurer ")
    print("You can choose to walk in multiple directions to find a way out.")
    print("Let's start with your name: ")
    name = input()
    print("Good luck, " +name+ ".")
    introScene()


#-----------------------------------------------------Adventure Game--------------------------------------------------------------------------------------------


from random import randint

#-----------------------------------------------------Rock,Paper,Scisors-----------------------------------------------------------------------------------------
if choice == "2":
    from random import randint

    #create a list of play options
    t = ["Rock", "Paper", "Scissors"]

    #assign a random play to the computer
    computer = t[randint(0,2)]

    #set player to False
    player = False

    while player == False:
    #set player to True
        player = input("Rock, Paper, Scissors?")
        if player == computer:
            print("Tie!")
        elif player == "Rock":
            if computer == "Paper":
                print("You lose!", computer, "covers", player)
            else:
                print("You win!", player, "smashes", computer)
        elif player == "Paper":
            if computer == "Scissors":
                print("You lose!", computer, "cut", player)
            else:
                print("You win!", player, "covers", computer)
        elif player == "Scissors":
            if computer == "Rock":
                print("You lose...", computer, "smashes", player)
            else:
                print("You win!", player, "cut", computer)
        else:
            print("That's not a valid play. Check your spelling!")
        #player was set to True, but we want it to be False so the loop continues
        player = False
        computer = t[randint(0,2)]
        #create a list of play options
    t = ["Rock", "Paper", "Scissors"]
        #assign a random play to the computer
    computer = t[randint(0,2)]

    #set player to False
    player = False
    while player == False:
    #set player to True
        player = input("Rock, Paper, Scissors?")
        if player == computer:
            print("Tie!")
        elif player == "Rock":
            if computer == "Paper":
                print("You lose!", computer, "covers", player)
            else:
                print("You win!", player, "smashes", computer)
        elif player == "Paper":
            if computer == "Scissors":
                print("You lose!", computer, "cut", player)
            else:
                print("You win!", player, "covers", computer)
        elif player == "Scissors":
            if computer == "Rock":
                print("You lose...", computer, "smashes", player)
            else:
                print("You win!", player, "cut", computer)
        else:
            print("That's not a valid play. Check your spelling!")
        #player was set to True, but we want it to be False so the loop continues
        player = False
        computer = t[randint(0,2)]
#-----------------------------------------------------Rock,Paper,Scisors-----------------------------------------------------------------------------------------
#-----------------------------------------------------Calculator-------------------------------------------------------------------------------------------------
if choice == "3":

        

        # Python program for simple calculator
        
        # Function to add two numbers
    def add(num1, num2):
        return num1 + num2
        
        # Function to subtract two numbers
    def subtract(num1, num2):
        return num1 - num2
        
        # Function to multiply two numbers
    def multiply(num1, num2):
        return num1 * num2
        
        # Function to divide two numbers
    def divide(num1, num2):
        return num1 / num2
        
    print("Please select operation -\n" \
            "1. Add\n" \
            "2. Subtract\n" \
            "3. Multiply\n" \
            "4. Divide\n")
        
        
        # Take input from the user
    select = int(input("Select operations form 1, 2, 3, 4 :"))
        
    number_1 = int(input("Enter first number: "))
    number_2 = int(input("Enter second number: "))
        
    if select == 1:
        print(number_1, "+", number_2, "=",
                        add(number_1, number_2))
        
    elif select == 2:
        print(number_1, "-", number_2, "=",
                        subtract(number_1, number_2))
        
    elif select == 3:
        print(number_1, "*", number_2, "=",
                        multiply(number_1, number_2))
        
    elif select == 4:
        print(number_1, "/", number_2, "=",
                        divide(number_1, number_2))
    else:
        print("Invalid input")
#-----------------------------------------------------Calculator-------------------------------------------------------------------------------------------------

def poop():
   if choice == "4":
      print("poop")
poop()