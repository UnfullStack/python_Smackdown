#imports
import pygame
from pygame import mixer
import random

f1_name = input("Player 1, select a fighter:\n").lower()
f2_name = input("Player 2, select a fighter:\n").lower()

#setup pygame
pygame.init()
mixer.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1000, 600))

#play music
mixer.music.load("assets/music.mp3")
mixer.music.set_volume(.5)
mixer.music.play()

#--FUNCTIONS AND CLASSES--

#this code was created by a user by the name of DaFluffyPotato
#thank you good sir now i can use spritesheets
#i mostly understand the code
def clip(surface, x, y, x_size, y_size): #Get a part of the image
    handle_surface = surface.copy() #Sprite that will get process later
    clipRect = pygame.Rect(x,y,x_size,y_size) #Part of the image
    handle_surface.set_clip(clipRect) #Clip or you can call cropped
    image = surface.subsurface(handle_surface.get_clip()) #Get subsurface
    return image.copy() #Return

#function for checking if surfaces are touching
def get_touching(f1,f2):
    if f2.state != "walk":
        return f1.images["attack"].get_rect(topleft=(f1.x_pos,f1.y_pos)).colliderect(f2.images[f2.state].get_rect(topleft=(f2.x_pos,f2.y_pos)))
    else:
        return f1.images["attack"].get_rect(topleft=(f1.x_pos,f1.y_pos)).colliderect(f2.images["idle"].get_rect(topleft=(f2.x_pos,f2.y_pos)))

#function for loading a stage
def load_stage(sname,scale=1,pos=(0,0)):
    surf = pygame.image.load(f"assets/STAGE_{sname}.png").convert_alpha()
    surf = pygame.transform.scale_by(surf,scale)
    return surf

#function to run the code for bliting a fighter on screen because it's easier to use this then the full code each time
def place_fighter(fighter):
    #check if it is a variant state or not
    if not fighter.state in ["walk"]:
        screen.blit(fighter.images[fighter.state],(fighter.x_pos,fighter.y_pos))
    else:
        screen.blit(fighter.images[fighter.state + str(fighter.variant)],(fighter.x_pos,fighter.y_pos))

#function to run code for updating fighter state for same reason as last one
def update_state(fighter):
    #deal with states that have db
    if fighter.state in ["attack","stun"]:
        if fighter.state_db == 0:
            #if state ended return to idle
            fighter.state = "idle"
        else:
            fighter.state_db-=1
    #update variant states for multi frame animations
    if fighter.state in ["walk"]:
        if fighter.var_db == 0:
            fighter.variant+=1
            
            if fighter.variant >= 8:
                fighter.variant = 0
            
            fighter.var_db = anim_delay
        else:            
            fighter.var_db-=1

#function for applying the effects of velocity on a fighter
def apply_vels(fighter):
    #this is just addition and subtraction (except for some stuff)
    fighter.x_pos += fighter.x_vel
    fighter.y_pos -= fighter.y_vel
    
    if fighter.y_pos >= 570-fighter.height*fighter.sf:
        fighter.y_pos = 570-fighter.height*fighter.sf
        fighter.y_vel = 0
    else:
        fighter.y_vel-=gravity

    def rotate(self, angle):
        pivot = self.pivot.rotate(angle)
        self.image = pygame.transform.rotate(self.base_image, -angle)
        self.rect = self.image.get_rect(center=self.origin + pivot)

#up next is functions for various actions
def punch(fighter):
    #if the player attack key is pressed, change their state
    fighter.state = "attack"
    fighter.state_db = 5
    
    #clear x velocity
    fighter.x_vel = 0
    
    #downslam for knight
    if fighter.char == "little knight":
        fighter.y_vel = -20
    
    collide = get_touching(fighter1,fighter2)
    
    if collide:
        if fighter == fighter1:
            fighter2.state = "stun"
            fighter2.state_db = 4
            fighter2.variant = 0
            fighter2.x_vel = 0
            
            if random.randint(1,20) != 1:
                fighter2.hp-=5
            else:
                fighter2.hp-=20
                fighter2.y_vel = 20
                pygame.mixer.Sound.play(pygame.mixer.Sound("assets/crit.mp3"))
        else:
            fighter1.state = "stun"
            fighter1.state_db = 4
            fighter1.variant = 0
            fighter1.x_vel = 0
            
            if random.randint(1,5) != 1:
                fighter1.hp-=5
            else:
                fighter1.hp-=20
                fighter1.y_vel = 20
                pygame.mixer.Sound.play(pygame.mixer.Sound("assets/crit.mp3"))

def move(fighter,stop=False,vel=0):
    #check movement types
    if not stop:
        #allow the fighter to move if not busy
        if not fighter.state in ["attack","stun"]:
            fighter.x_vel = vel
            fighter.state = "walk"
            fighter.variant = 0
            fighter.var_db = anim_delay
    else:
        #allow the fighter to stop moving if not busy
        if not fighter.state in ["attack","stun"]:
            fighter.x_vel = 0
            fighter.state = "idle"
        

#define a class for creating a fighter
class CreateFighter(pygame.sprite.Sprite):
    def __init__(self,sheet,xpos,ypos,flip=False):
        super().__init__()
        
        #save the name
        self.char = sheet
        
        #load the full image
        self.ss = pygame.image.load(f"assets/CHAR_{sheet}.png").convert_alpha()
        
        #get sprite data
        #.sheet is a made-up format that stores where sprites are in spritesheets
        s_file = open(f"assets/CHAR_{sheet}.sheet", "r").read()
        
        #load images
        #sf is short for scale factor
        #by default characters have no height if not provided, so you should probably provided it in the sheet file
        self.images = {}
        self.sf = 1
        self.height = 0
        
        #go through all lines in the sheet to get where sprites are
        for line in s_file.split("\n"):
            #get the value and it's.... value also, i guess
            #it's tricky to explain
            split = line.split("=")
            
            #check if this is an image and not a property of the sprite
            if not split[0] in ["scale","height"]:
                #save the position and size as a list
                spot = split[1].split(",")
                
                #convert stuff to integers using map
                #this changes all items to a data type of choice
                spot = list(map(int,spot))
                
                #save an entry in the images for the line using what info we got
                if not flip:
                    self.images[split[0]] = clip(self.ss,spot[0]*self.sf,spot[1]*self.sf,spot[2]*self.sf,spot[3]*self.sf)
                else:
                    self.images[split[0]] = pygame.transform.flip(clip(self.ss,spot[0]*self.sf,spot[1]*self.sf,spot[2]*self.sf,spot[3]*self.sf),True,False)
            elif split[0] == "scale":
                #it is the scale property, so scale the sprite and save the value
                self.ss = pygame.transform.scale_by(self.ss,int(split[1]))
                self.sf = int(split[1])
            elif split[0] == "height":
                #height property
                #pretty self explanatory code
                self.height = int(split[1])
        
        #define some more variables
        self.state = "idle"
        self.state_db = 0
        self.x_pos = xpos
        self.y_pos = ypos
        self.x_vel = 0
        self.y_vel = 0
        self.variant = 0
        self.var_db = 0
        self.hp = 100

#--NOT FUNCTIONS AND CLASSES-- (yes this is the extent of my organization)

#define some variables
bg_color = (120,120,255)
fps = 60
stage = load_stage("test")
gravity = .3
anim_delay = 6
debug = False

#create fighters
fighter1 = CreateFighter(f1_name,0,0)
fighter2 = CreateFighter(f2_name,900,0,True)

#main loop
running = True

while running:
    update_state(fighter1)
    update_state(fighter2)
    
    #go through events
    for event in pygame.event.get():
        #check the event
        if event.type == pygame.QUIT:
            #if the event is closing the window, then, you guessed it, close the window
            running = False
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            #detect key press
            if event.key == pygame.K_e:
                if not fighter1.state in ["attack","stun"]:
                    #run needed function
                    punch(fighter1)
            elif event.key == pygame.K_a:
                #run needed function
                move(fighter1,False,-5)
            elif event.key == pygame.K_d:
                #run needed function
                move(fighter1,False,5)
            elif event.key in [pygame.K_SPACE,pygame.K_w]:
                #do a jump if possible
                if fighter1.y_vel == 0:
                    fighter1.y_vel = 10
            elif event.key == pygame.K_SLASH:
                if not fighter2.state in ["attack","stun"]:
                    punch(fighter2)
            elif event.key == pygame.K_LEFT:
                #run needed function
                move(fighter2,False,-5)
            elif event.key == pygame.K_RIGHT:
                #run needed function
                move(fighter2,False,5)
            elif event.key == pygame.K_UP:
                #do a jump if possible
                if fighter2.y_vel == 0:
                    fighter2.y_vel = 10
        elif event.type == pygame.KEYUP:
            #check if key is released (mainly for movement)
            if event.key == pygame.K_a or event.key == pygame.K_d:
                #allow the fighter to stop moving if not busy and if some key conditions are met
                if (event.key == pygame.K_a and fighter1.x_vel != 5) or (event.key == pygame.K_d and fighter1.x_vel != -5):
                    move(fighter1,True,0)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                #allow the fighter to stop moving if not busy and if some key conditions are met
                if (event.key == pygame.K_LEFT and fighter2.x_vel != 5) or (event.key == pygame.K_RIGHT and fighter2.x_vel != -5):
                    move(fighter2,True,0)
    #update the display and other stuff
    #this is done in a try because of a weird unavoidable error with how displaying graphics work when closing the window
    #only do if it debug is off, though
    #stored in a string for less code in total
    
    code = """
screen.fill(bg_color)
screen.blit(stage,(0,0))
apply_vels(fighter1)
place_fighter(fighter1)
apply_vels(fighter2)
place_fighter(fighter2)
font = pygame.font.SysFont(None, 50)
img = font.render('P1: """ + str(fighter1.hp) + """ P2: """ + str(fighter2.hp) + """', True, (255,255,255))
screen.blit(img, (350, 0))
pygame.display.flip()
        """
    
    if not debug:
        try:
            exec(code)
        except:
            pass
    else:
        exec(code)
    
    #checks for deaths
    if fighter1.hp <= 0:
        print("Player 2 has won!")
        screen.fill((0,0,0))
        place_fighter(fighter1)
        place_fighter(fighter2)
        text = font.render('Player 2 wins!', True, (255,255,255))
        screen.blit(text, (350, 0))
        pygame.display.flip()
        clock.tick(1)
        pygame.quit()
        running = False
        break
    if fighter2.hp <= 0:
        print("Player 1 has won!")
        screen.fill((0,0,0))
        place_fighter(fighter1)
        place_fighter(fighter2)
        text = font.render('Player 1 wins!', True, (255,255,255))
        screen.blit(text, (350, 0))
        pygame.display.flip()
        clock.tick(1)
        pygame.quit()
        running = False
        break
    clock.tick(fps)