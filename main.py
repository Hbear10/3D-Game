import pygame
from PIL import Image
import math
import random
#import time

import maze
import block_scan
import Enum
import Spritesheet
from battleElements import *
from render import *

print("Hello World!")






player_pos = [2.5,10.5]#The coordinate of the player, (xy)


def new_maze(wall_tiles = [wall_image("Brick.png"), wall_image("Blue_Brick.png")]):
    global map, player_pos

    map,player_pos = maze.maze_generate(11)

    #add in random thingies here
    #add some things to the R points

    for x in range(len(map)):
        for y in range(len(map[x])):
            if map[x][y] == 1:
                # map[x][y]=tile("Wall",wall_image=wall_image("Brick.png"))
                map[x][y]=tile("Wall",wall_image=random.choice(wall_tiles))
            elif map[x][y] == "S":
                map[x][y] = tile("Sprite",spriteInfo="S")
            else:
                map[x][y] = tile("Path")
 

raycast_column_width = 2 #The width of each pixel column, increase it to improve performance as it reduces the amount of rays sent


pygame.init()
screen = pygame.display.set_mode((1280,720)) #720p

clock = pygame.time.Clock()#Used later to set FPS cap
game_font = pygame.font.Font('Evil Empire.otf', 24)

player_angle=0 # Direction the player is facing



wallTest = tile("Wall",wall_image("Column.png"))


### Testing Vars, 
FPS = 30
battleAnimTime = 10 #has to be a multiple of 10 as animations are 10 frames long so it just won't render if it isnt a multiple of 10, value is how many frames it takes
FOV = 100 #The field of view of the player, Changing is not recommended as rendering may become buggy especially with sprite rendering



#The traversable map is stored as a 2D array, this is my testing map
map = [[1,1,1,1,1,1,1,1,1],
       [1,0,0,0,0,0,0,0,1],
       [1,0,"S",0,1,1,1,1,1],
       [1,0,0,0,1],
       [1,0,"S",0,1],
       [1,0,0,0,1],
       [1,0,"S",0,1],
       [1,0,1,0,tile("Wall",wall_image=wall_image("Blue_Brick.png"))],
       [1,0,0,0,tile("Wall",wall_image=wall_image("SmoothStone.png"))],
       [1,0,0,0,1,1,1,1,1],
       [1,0,0,0,"BasicSlime","BasicSlime","BasicSlime","BasicSlime",1],
       [1,0,"S",0,1,1,1,1,1],
       [1,0,"BasicSlime",0,tile("Wall",wall_image=wall_image("SmoothStone.png")),1,1,1,1],
       [wallTest,0,0,0,0,0,0,0,1],
       [1,0,"W",0,0,0,"KingFireSlime",0,1],#W on this line is just an indicator for me for where the player starts, it doesn't affect any processing
       [1,1,1,1,1,1,1,1,1]]



for x in range(len(map)):
    for y in range(len(map[x])):
        if map[x][y]==1:
            map[x][y]=tile("Wall",wall_image=wall_image("Brick.png"))
        elif map[x][y]==0 or map[x][y]=="W":
            map[x][y]=tile("Path")
        elif map[x][y]=="S":
            map[x][y]=tile("Sprite",spriteInfo=map[x][y])
        elif type(map[x][y])==str:
            map[x][y]=tile("Enemy",spriteInfo=map[x][y])


# print(type(tile("Wall",wall_image("Smooth_Stone.png"))))

class battle_sprites():
    def __init__(self, image_name, resolution=32):
        self.resolution = resolution
        self.battle_image = pygame.image.load(f"Assets/{image_name}.png").convert_alpha()
        self.battle_image = pygame.transform.scale_by(self.battle_image,(256/resolution))

    def draw_enemy(self,x_increment=0,y_increment=0):
        img_rect = self.battle_image.get_rect()
        img_rect.center=(640+x_increment,360-y_increment)
        screen.blit(self.battle_image,img_rect)
        

enemy = battle_sprites("KingFireSlime")


player_stats = player_battle_container()
# enemy_obj = enemy_battle_container(name="King Fire Slime")
#blue is player, red is enemy
turnOrder = ["#0000FF","#0000FF","#FF0000","#0000FF","#FF0000"]

# door = Image.open("Assets/Door.png")

sprites_loaded = {"door" : pygame.image.load("Assets/Door.png").convert_alpha(),"KingFireSlime": pygame.image.load("Assets/KingFireSlime.png").convert_alpha(),"BasicSlime": pygame.image.load("Assets/BasicSlime.png").convert_alpha()}

icons = {"SpeedSyringe": pygame.image.load("Assets/Syringe.png").convert_alpha(),"HeavyPlating": pygame.image.load("Assets/HeavyPlating.png").convert_alpha(),
         "SpikeyBand": pygame.image.load("Assets/SpikeyBand.png").convert_alpha(),"FireShard": pygame.image.load("Assets/FireShard.png").convert_alpha(),
         "IceShard": pygame.image.load("Assets/IceShard.png").convert_alpha(),"EarthShard": pygame.image.load("Assets/EarthShard.png").convert_alpha(),
         "HPUP": pygame.image.load("Assets/Sprite.png").convert_alpha(),"Battery": pygame.image.load("Assets/Battery.png").convert_alpha(),}


relics = load_relics()
randomRelics = []

#UI images
player_selfie = pygame.image.load("Assets/PlayerSelfie.png").convert_alpha()
player_selfie = pygame.transform.scale_by(player_selfie,4)

#player_arm = pygame.image.load("assets/RoboArm.png").convert_alpha()
#player_arm = pygame.transform.scale_by(player_arm,16)

arms = Spritesheet.animation("RoboArm-Sheet",32,32,10,16).frames
#player_arm = arms.frames[5]

#Set up the refresh background so I can quickly redraw for animations without having to rerender the entire background
#This saves the screen as an image which I can then draw.
pygame.image.save(screen, "Assets/saveBackground.png")


#uses ticks/count timers, +1 per loop for time tracking for animations etc.
tick_timers = {"Battle":0}
menu_selected = {"Battle":0, "Battle-Energy":0,"Battle-Item":0,"Battle-Won":0}
playerTurn = True
turnCounter = {"Player":0,"Enemy":0}
displayInv = False

class sprite_obj():
    def __init__(self,x,y,imageID="door"):
        self.sprite_image = sprites_loaded[imageID]
        self.sprite_x = x
        self.sprite_y = y
        self.distance = math.sqrt((x-player_pos[0])**2+(y-player_pos[1])**2)* math.cos(math.radians(90) + math.radians(player_angle)-math.atan2( (player_pos[1]-(y)) , (player_pos[0]-(x))))
        self.left_point = 0
        self.right_point = 16


energy_moves = load_energy_moves()
player_stats.set_energyMoves(energy_moves[0],energy_moves[1],energy_moves[2],energy_moves[3])


items = load_items()
player_stats.add_item(items[0],5)#add 5 potions
player_stats.add_item(items[1],5)#add 5 super potions
player_stats.add_item(items[2],5)#add 5 bombs


enemy_obj = load_enemy("KingFireSlime")

# enemy_obj.moves = {enemy_moves[0]:0.7,enemy_moves[1]:0.3}

# enemy_obj.make_move(player_stats)
# enemy_obj.make_move()
# enemy_obj.make_move()
# enemy_obj.make_move()
# enemy_obj.make_move()



sprites = []
sprites_pos_that_can_be_rendered = []#to check for what new objects to create


game_state = Enum.StateOfGame()
game_state.set_value("Moving")




def order_sprites():#bubble sort, sorting the list into ascending order
    global sprites

    made_a_change = True
    while made_a_change and len(sprites) > 1:#until the list is ordered and if there is enough sprites to actually sort
        made_a_change = False #at the start there haven't been any swapps
        for i in range(len(sprites)-1):#check each pair

            if sprites[i].distance > sprites[i+1].distance:#if it is in the wrong order

                made_a_change = True#will swap so set to true

                #swap
                temporary = sprites[i]  
                sprites[i] = sprites[i+1]
                sprites[i+1] = temporary


def draw_beam(x_point,distance,image_index,image=brick): #literally just takes the point along the screen and draws a line based on distance away from the camera, image index is for what column along an image to take

    ray_slice = image.img_slices[image_index].transform((raycast_column_width,int(360/distance)),Image.Transform.EXTENT,[0,0,1,16]) #transforms the image slice to the right size, 

    pygame_surface = pygame.image.fromstring(ray_slice.tobytes(),ray_slice.size,ray_slice.mode).convert() #Turns the PIL image into a pygame image
    screen.blit(pygame_surface, pygame_surface.get_rect(center = (x_point+(raycast_column_width//2), 360))) # Draws the image slice onto the screen



def smaller_point_dist(pointA,pointB,pointReference): # takes 3 points, and compares the first 2 to the third and returns the nearest point and the distance
    distA = math.sqrt((pointA[0]-pointReference[0])**2+(pointA[1]-pointReference[1])**2) #pythagoras
    distB = math.sqrt((pointB[0]-pointReference[0])**2+(pointB[1]-pointReference[1])**2) #pythagoras
    if distA < distB:#return the closer point and the distance
        return pointA, distA
    else:
        return pointB, distB

#code for the each individual ray, this uses the DDA algorithm to calculate the distance. Is quite long as there appeared to be many edge cases.
def raycast_ray(count):
    global sprites

    ray_pos = [player_pos[0],player_pos[1]] #index-coord: 0=x, 1=y  ,note to self that the map indexing is y,x not x,y
    ray_pos_grid = [int(ray_pos[0]),int(ray_pos[1])] #gets the index on the map/array of the player
    ray_distance = 0
    is_blocked = False

    DIST = 5*FOV #dist is a constant of distance to imaginary wall that we are casting on
    angle = math.radians((math.degrees(math.atan((count*raycast_column_width-640) / DIST))+player_angle)%360) #math.radians((raycast_resolution*count-(FOV/2)+player_angle)%360)
    #This uses angles with fixed pixel increments instead of fixed angle increments which removes distortion on the sides of the screen more info in the doc

    side_step_x = [0,0] #points of the ray where they move to the next grid line along the x, or y
    side_step_y = [0,0]


    x_direction = 1 #these are for if the x and y go up or down and left or right
    y_direction = 1

    if angle <= 1.5707 or angle > 4.712: #up, these values are approximations of the radians of pi/2 and 3pi/2
        y_direction= -1
    if angle >3.14159: #left
        x_direction= -1

    while not is_blocked:#Until the ray meets a boundary
        degree_angles = math.degrees(angle)#convert angle from radians to degrees as it makes some calculations easier

        if map[ray_pos_grid[1]][ray_pos_grid[0]].tileType == "Sprite" or map[ray_pos_grid[1]][ray_pos_grid[0]].tileType == "Enemy":#if there are any sprites on the screen that should be rendered
            if (ray_pos_grid[0],ray_pos_grid[1]) not in sprites_pos_that_can_be_rendered:
                #print(degree_angles)
                sprites_pos_that_can_be_rendered.append( (ray_pos_grid[0],ray_pos_grid[1]) )
                if map[ray_pos_grid[1]][ray_pos_grid[0]].spriteInfo == "S":
                    sprites.append( sprite_obj(ray_pos_grid[0]+0.5,ray_pos_grid[1]+0.5) )
                else:
                    #Enemy
                    sprites.append( sprite_obj(ray_pos_grid[0]+0.5,ray_pos_grid[1]+0.5,imageID=map[ray_pos_grid[1]][ray_pos_grid[0]].spriteInfo) )
            else:
                sprites[-1].left_point = 0

        if map[ray_pos_grid[1]][ray_pos_grid[0]].tileType == "Wall":#if there is a wall
            is_blocked = True
            
            image_index=0# which column of an image/wall the ray hit, 0.0625 is 1/16, starts from 0 and goes to 15
            if degree_angles%180==0:
                image_index = int((ray_pos[0]%1)/0.0625)
            elif degree_angles%90==0:
                image_index = int((ray_pos[1]%1)/0.0625)
            elif ray_pos == side_step_x:
                image_index = int((ray_pos[1]%1)/0.0625)
            elif ray_pos == side_step_y:
                image_index = int((ray_pos[0]%1)/0.0625)

            if map[ray_pos_grid[1]][ray_pos_grid[0]].tileType == "Wall":
                #returns the distance to a wall (multipled by the cos of the angle to fix distortion) and the image index
                return (round(ray_distance*math.cos(math.radians(player_angle)-angle),5),image_index,map[ray_pos_grid[1]][ray_pos_grid[0]].wallImage)
        else:

            if degree_angles%90!=0:
                scale_x = math.tan(angle)*y_direction #sohcahtoa for how much to move when index of one
                scale_y = 1/math.tan(angle)*x_direction  
            else:
                scale_x = int(math.sin(angle)) #0=0,90=1, 180=0, 270=-1
                scale_y = int(math.cos(math.radians(degree_angles+180)))# 0=-1, 90=0, 180=1, 270=0

            #many many edge cases
            if degree_angles%90==0:#hardcoding for when tan = 0 or i
                if ray_pos == player_pos and ray_pos[0]%1!=0 and ray_pos[1]%1!=0:#not on grid lines
                    
                    if degree_angles == 0:
                        
                        distance_travelled=ray_pos[1]-int(ray_pos[1])
                        ray_pos_grid[1]-= math.ceil(ray_pos[1]%1)
                        ray_pos[1]=int(ray_pos[1])

                    elif degree_angles == 90:
                        distance_travelled=math.ceil(ray_pos[0])-ray_pos[0]
                        ray_pos[0]=math.ceil(ray_pos[0])
                        ray_pos_grid[0]+=1

                    elif degree_angles == 180:
                        distance_travelled=math.ceil(ray_pos[1])-ray_pos[1]
                        ray_pos_grid[1]+=math.ceil(ray_pos[1]%1)
                        ray_pos[1]=math.ceil(ray_pos[1])

                    elif degree_angles == 270:
                        distance_travelled=ray_pos[0]-int(ray_pos[0])
                        ray_pos[0]=int(ray_pos[0])
                        ray_pos_grid[0]-=1

                elif ray_pos == player_pos and ray_pos[1]%1==0 and ray_pos[0]%1!=0:#when on y grid
                    if degree_angles == 0:
                        distance_travelled=1
                        ray_pos_grid[1]-= 2#when use int to get grid pos it don't work properly, and only for the negative direction
                        ray_pos[1]-=1
                        
                    elif degree_angles == 90:
                        distance_travelled=math.ceil(ray_pos[0])-ray_pos[0]
                        ray_pos[0]=math.ceil(ray_pos[0])
                        ray_pos_grid[0]+=1

                    elif degree_angles == 180:
                        distance_travelled=1
                        ray_pos_grid[1]+=1
                        ray_pos[1]=math.ceil(ray_pos[1])

                    elif degree_angles == 270:
                        distance_travelled=ray_pos[0]-int(ray_pos[0])
                        ray_pos[0]=int(ray_pos[0])
                        ray_pos_grid[0]-=1

                elif ray_pos == player_pos and ray_pos[0]%1==0 and ray_pos[1]%1!=0:#when on x grid
                    if degree_angles == 0:
                        distance_travelled=ray_pos[1]-int(ray_pos[1])
                        ray_pos_grid[1]-= 1
                        ray_pos[1]=int(ray_pos[1])

                    elif degree_angles == 90:
                        distance_travelled=1
                        ray_pos[0]=math.ceil(ray_pos[0])
                        ray_pos_grid[0]+=1

                    elif degree_angles == 180:
                        distance_travelled=math.ceil(ray_pos[1])-ray_pos[1]
                        ray_pos_grid[1]+=1
                        ray_pos[1]=math.ceil(ray_pos[1])

                    elif degree_angles == 270:
                        distance_travelled=1
                        #print(ray_pos[0],int(ray_pos[0]))
                        ray_pos[0]-=1
                        ray_pos_grid[0]-=2
                
                elif ray_pos == player_pos:#both grid lines
                    if degree_angles==90 or degree_angles==180:
                        ray_pos[0] += scale_x
                        ray_pos[1] += scale_y
                        ray_pos_grid[0] += scale_x
                        ray_pos_grid[1] += scale_y
                        distance_travelled=1
                    else:
                        ray_pos[0] += scale_x
                        ray_pos[1] += scale_y
                        ray_pos_grid[0] += scale_x*2 #when ray moving in a negative direction it needs to be doubled on the first push on the grid otherwise it tracks wrong due to the interger func at decleration. 
                        ray_pos_grid[1] += scale_y*2
                        distance_travelled=1
                
                else:
                    ray_pos[0] += scale_x
                    ray_pos[1] += scale_y
                    ray_pos_grid[0] += scale_x
                    ray_pos_grid[1] += scale_y
                    distance_travelled=1
            #side step x is where x+=1, y is for y+=1
            elif ray_pos==player_pos and ray_pos[0]%1!=0 and ray_pos[1]%1!=0:#not on grid line
                
                #if angle !=90:
                if x_direction == 1:#right
                    side_step_x = [math.ceil(ray_pos[0]),ray_pos[1]-(-ray_pos[0]+math.ceil(ray_pos[0]))*scale_y]
                else: #left
                    side_step_x = [int(ray_pos[0]),ray_pos[1]+(-ray_pos[0]+int(ray_pos[0]))*scale_y]

                if y_direction == 1:#dwon
                    side_step_y = [ray_pos[0]-(-ray_pos[1]+math.ceil(ray_pos[1]))*scale_x,math.ceil(ray_pos[1])]
                else: # same as ==-1, up
                    side_step_y = [ray_pos[0]+(-ray_pos[1]+int(ray_pos[1]))*scale_x,int(ray_pos[1])]
      
            elif ray_pos==player_pos and ray_pos[0]%1==0 and ray_pos[1]%1!=0:#x grid line
                if x_direction == -1:
                    side_step_x = ray_pos[0],ray_pos[1]
                else:
                    side_step_x=[ray_pos[0]+x_direction,ray_pos[1]-scale_y]
                
                if y_direction == 1:#dwon
                    side_step_y = [ray_pos[0]-(-ray_pos[1]+math.ceil(ray_pos[1]))*scale_x,math.ceil(ray_pos[1])]
                else: # same as ==-1, up
                    side_step_y = [ray_pos[0]+(-ray_pos[1]+int(ray_pos[1]))*scale_x,int(ray_pos[1])]

            elif ray_pos==player_pos and ray_pos[0]%1!=0 and ray_pos[1]%1==0:#on y grid line
                if x_direction == 1:#right
                    side_step_x = [math.ceil(ray_pos[0]),ray_pos[1]-(-ray_pos[0]+math.ceil(ray_pos[0]))*scale_y]
                else: #left
                    side_step_x = [int(ray_pos[0]),ray_pos[1]+(-ray_pos[0]+int(ray_pos[0]))*scale_y]

                if y_direction == -1:
                    side_step_y = ray_pos[0],ray_pos[1]
                else:
                    side_step_y = [ray_pos[0]-scale_x,ray_pos[1]+1] 

            elif ray_pos==player_pos and ray_pos[0]%1==0 and ray_pos[1]%1==0:#on both grid lines
                if x_direction == -1:
                    side_step_x = ray_pos[0],ray_pos[1]
                else:
                    side_step_x=[ray_pos[0]+x_direction,ray_pos[1]-scale_y]
                
                if y_direction == -1:
                    side_step_y = ray_pos[0],ray_pos[1]
                else:
                    side_step_y = [ray_pos[0]-scale_x,ray_pos[1]+1] 
            
            else:
                
                if ray_pos==side_step_x:
                    side_step_x=[ray_pos[0]+x_direction,ray_pos[1]-scale_y]#move this pos along by 1 in the x
                elif ray_pos==side_step_y:
                    side_step_y = [ray_pos[0]-scale_x,ray_pos[1]+y_direction]#move this pos along by 1 in the y


            if degree_angles%90!=0:
                ray_pos,distance_travelled = smaller_point_dist(side_step_x,side_step_y,ray_pos)
                
                if ray_pos == side_step_x:
                    ray_pos_grid[0]+=x_direction
                elif ray_pos == side_step_y:
                    ray_pos_grid[1]+=y_direction
            

            ray_distance+=distance_travelled


def raycast():
    global sprites,sprites_pos_that_can_be_rendered

    sprites = []
    sprites_pos_that_can_be_rendered = []

    #t= time.perf_counter()
    
    ray_store=[]
    for i in range(1280//raycast_column_width):#cast all the rays
        ray_store.append(raycast_ray(i))
    for i in range(1280//raycast_column_width):#draw all the rays
        if len(ray_store[i]) == 2:
            draw_beam(i*raycast_column_width,ray_store[i][0],ray_store[i][1])
        else:
            draw_beam(i*raycast_column_width,ray_store[i][0],ray_store[i][1],ray_store[i][2])

    #print(time.perf_counter()-t)


#Next 3 functions use turn counter variable inside main scope therefore aren't placed in battleElements file
#Calculate next 5 turns to update the side bar
def calculate_turn_order(player,enemy):

    pTime = turnCounter["Player"]
    pSpeed = player.speed

    eTime = turnCounter["Enemy"]
    eSpeed = enemy.speed

    order = []

    for _ in range(5):
        if pTime >= eTime:
            order.append("#0000FF")
            eTime+=eSpeed
        else:
            order.append("#FF0000")
            pTime+=pSpeed

    return order

#Uses turnCounter to determine if the player or enemy should move next
def determine_turn():
    global playerTurn, turnOrder

    if turnCounter["Player"] >= turnCounter["Enemy"]:
        playerTurn = True
    else:
        playerTurn = False

    #update the side bar
    turnOrder = calculate_turn_order(player_stats,enemy_obj)

#Does as the name implies
def update_turn_counters(playerMoved=True):
    global turnCounter

    if playerMoved:
        turnCounter["Enemy"] += enemy_obj.speed
    else:
        turnCounter["Player"] += player_stats.speed



def deal_damage(user,opponent):
    damage = int(user.physicalStrength*1.5-opponent.defence)
    if damage < 0:
        damage = 0
    opponent.hp -= damage



def draw_text(surface,text:str,colour:str,left: float,top: float,angle=0,fontSize=24,centre=False):
    text_surface = pygame.font.Font('Evil Empire.otf', fontSize).render(text, True, colour)  #create text box in chosen colour
    text_surface = pygame.transform.rotate(text_surface,-angle)
    text_rect = text_surface.get_rect()
    if centre==True:
        text_rect.center=(left,top)
    else:                #
        text_rect.left = left
        text_rect.top = top
    
    surface.blit(text_surface, text_rect) 



def draw_sprites():
    #print(len(sprites))

    order_sprites()

    for sprite in sprites[::-1]:

        sprite_distance = sprite.distance

        #print("hjijdfg hj ",math.degrees(math.atan((player_pos[0]-(sprite.sprite_x))  /  (player_pos[1]-(sprite.sprite_y))))%360)
        bearing_point_from_player = math.radians(90 - math.degrees(math.atan2((player_pos[0]-(sprite.sprite_x))  ,  (-player_pos[1]+(sprite.sprite_y))))%360)
        #print(f"{(sprite.sprite_x-0.5*math.sin(theta),sprite.sprite_y-0.5*math.cos(theta))} {player_pos}")
        #print(block_scan.scan(map, player_pos, (sprite.sprite_x-0.5*math.sin(theta),sprite.sprite_y+0.5*math.cos(theta))))
        sprite_visible_index = 0
        while not block_scan.scan(map, player_pos, (sprite.sprite_x+ ((8-sprite_visible_index)/8) * 0.5*math.sin(bearing_point_from_player),sprite.sprite_y+ ((8-sprite_visible_index)/8) *0.5*math.cos(bearing_point_from_player))) and sprite_visible_index <= 16:
            sprite_visible_index+=1

            #pass

        #else:
            #print("x")
            #n=1
            #if block_scan.scan(map, player_pos, (sprite.sprite_x+(4/8)*0.5*math.sin(theta),sprite.sprite_y+0.25*math.cos(theta))):
                 #print("Next")
        #print(n)
        sprite.left_point = sprite_visible_index

        sprite_visible_index=16
        while not block_scan.scan(map, player_pos, (sprite.sprite_x+ ((8-sprite_visible_index)/8) * 0.5*math.sin(bearing_point_from_player),sprite.sprite_y+ ((8-sprite_visible_index)/8) *0.5*math.cos(bearing_point_from_player))) and sprite_visible_index >= 0:
            sprite_visible_index-=1
        sprite.right_point = sprite_visible_index

            
            #print(f"{math.degrees(theta)=}")

        sprite_bearing = math.radians(90) - math.atan2( (player_pos[1]-(sprite.sprite_y)) , (player_pos[0]-(sprite.sprite_x)))
        #print(f"{math.degrees(sprite_bearing)=}")


        #Fix sprites of different sizes
        #I want to allow for spirtes up to 64x64 because why not, I will probably limit to 16, 32 and 64 though
        sprite_width = sprite.sprite_image.get_width()
        if sprite_width != 64:
            sprite.sprite_image = pygame.transform.scale_by(sprite.sprite_image, 64/sprite_width)

        # sprite.left_point*4
        # sprite.right_point*4


        if sprite_distance > 0.04 and (90> (math.degrees(sprite_bearing)+player_angle)%360 or (math.degrees(sprite_bearing)+player_angle)%360>270) and sprite.left_point != sprite.right_point:
            sprite_scale_by = (22/sprite_distance)
            screen.blit(pygame.transform.scale_by(sprite.sprite_image,sprite_scale_by/4),                        #image
                        (640-(160/sprite_distance) - int(500*math.tan(sprite_bearing+math.radians(player_angle))-sprite_scale_by*sprite.left_point),#x start,  - the scale left point because - move it left and then fix to right spot
                                    (360-(8*sprite_scale_by))),                                                   #y start              
                        (sprite_scale_by*sprite.left_point,0,(sprite.right_point)*sprite_scale_by,16*sprite_scale_by))



def draw_inventory_roaming():
    inv = player_stats.items
    items = list(inv.keys())
    

    pygame.draw.rect(screen, "brown",pygame.Rect(50,50,200,25+len(items)*25))
    pygame.draw.rect(screen, "#000000",pygame.Rect(52,52,196,21+len(items)*25))

    draw_text(screen, "Inventory","#FFFFFF",150,65,centre=True)

    for i in range(len(items)):
        draw_text(screen,f"{items[i].name}       x{inv[items[i]]}   ","#FFFFFF",60,75+i*25)




def draw_screen():
    screen.fill("dark grey")
    pygame.draw.rect(screen,(34,34,34), pygame.Rect(0,0,1280,360))
    raycast()
    #print(sprites)
    draw_sprites()

    if displayInv == True:
        draw_inventory_roaming()

    pygame.display.flip()



def draw_turn_counters():
    #turn order box
    pygame.draw.rect(screen,"brown",pygame.Rect(0,0,100,420))
    pygame.draw.rect(screen,"#000000",pygame.Rect(0,0,98,418))
    
    pygame.draw.polygon(screen, turnOrder[0],((48,16),(80,48),(48,80),(16,48)))
    pygame.draw.polygon(screen, turnOrder[1],((48,96),(80,128),(48,160),(16,128)))
    pygame.draw.polygon(screen, turnOrder[2],((48,176),(80,208),(48,240),(16,208)))
    pygame.draw.polygon(screen, turnOrder[3],((48,256),(80,288),(48,320),(16,288)))
    pygame.draw.polygon(screen, turnOrder[4],((48,336),(80,368),(48,400),(16,368)))


#next 3 functions are used to draw UI in of battle menus
def draw_battle_UI():
    
    screen.blit(pygame.image.load("Assets/saveBackground.png"),(0,0))
    

    screen.blit(arms[tick_timers["Battle"]//3],(768,208))#animate in the arm
    if tick_timers["Battle"] >= 27:
        #background panel of UI - Draw options onto this
        pygame.draw.polygon(screen,"#3ec54b", ((980,440),(1220,565),(1195,650),(950,520)) )

        #battle options
        optionColours = ["#d4e650","#d4e650","#d4e650","#d4e650"]
        optionColours[menu_selected["Battle"]] = "#FF0000"

        draw_text(screen,"Attack",optionColours[0],990,450,34,40)
        draw_text(screen,"Energy",optionColours[1],1095,520,34,40)
        draw_text(screen,"Item",optionColours[2],975,485,34,40)
        draw_text(screen,"Guard",optionColours[3],1075,550,34,40)


    draw_turn_counters()


def draw_battle_energy_UI():
    screen.blit(arms[9],(768,208))#arm

    #background panel of UI - Draw options onto this
    pygame.draw.polygon(screen,"#3ec54b", ((980,440),(1220,565),(1195,650),(950,520)) )

    optionColours = ["#d4e650","#d4e650","#d4e650","#d4e650"]
    optionColours[menu_selected["Battle-Energy"]] = "#FF0000"#change selected option's colour to red so that it is clear what is selected

    draw_text(screen,player_stats.energyMoves[0].name,optionColours[0],990,450,34,30)   #move 1
    draw_text(screen,player_stats.energyMoves[1].name,optionColours[1],1095,520,34,30)  #move 2 
    draw_text(screen,player_stats.energyMoves[2].name,optionColours[2],975,485,34,30)   #move 3
    draw_text(screen,player_stats.energyMoves[3].name,optionColours[3],1075,550,34,30)  #move 4

    #box for move info to be drawn in
    pygame.draw.rect(screen, "brown",pygame.Rect(1020,160,200,200))
    pygame.draw.rect(screen, "#000000",pygame.Rect(1022,162,196,196))

    #selected energy move name
    selectedMove = player_stats.energyMoves[menu_selected["Battle-Energy"]]
    draw_text(screen, selectedMove.name,"#FFFFFF",1120,185,centre=True)

    #extra info about the specfied move to show what it does
    draw_text(screen,f"Physcial:    {selectedMove.physicalValue}","#FFFFFF",1030,205)
    draw_text(screen,f"Fire:            {selectedMove.fireValue}","#FFFFFF",1030,230)
    draw_text(screen,f"Earth:         {selectedMove.earthValue}","#FFFFFF",1030,255)
    draw_text(screen,f"Ice:              {selectedMove.iceValue}","#FFFFFF",1030,280)
    draw_text(screen,f"Heal:           {selectedMove.healValue}","#FFFFFF",1030,305)
    draw_text(screen,f"EP Cost:       {selectedMove.EPcost}","#FFFFFF",1030,330)

    draw_turn_counters()


def draw_battle_item_UI():
    pygame.draw.polygon(screen,"#3ec54b", ((980,435),(1220,565),(1195,650),(950,520)) )
    invItems = list(player_stats.items.keys())
    draw_text(screen,invItems[menu_selected["Battle-Item"]].name,"#d4e650",980,470,34,40)

    pygame.draw.polygon(screen, "#d4e650",((1008,448),(960,520),(963,470)))
    pygame.draw.polygon(screen, "#d4e650",((1208,600),(1150,620),(1180,560)))

    pygame.draw.rect(screen, "brown",pygame.Rect(1020,160,200,200))
    pygame.draw.rect(screen, "#000000",pygame.Rect(1022,162,196,196))

    #selected energy move name
    selectedItem = invItems[menu_selected["Battle-Item"]]
    draw_text(screen, selectedItem.name,"#FFFFFF",1120,185,centre=True)

    draw_text(screen,f"Type:          {selectedItem.effectType}","#FFFFFF",1030,205)
    draw_text(screen,f"Power:       {selectedItem.potency}","#FFFFFF",1030,230)
    draw_text(screen,f"Amount:    {player_stats.items[selectedItem]}","#FFFFFF",1030,255)

    draw_turn_counters()


def draw_battle_won_UI():
    translucentSurface = pygame.Surface((1280,720), pygame.SRCALPHA) #This is a surface that can be drawn on with opacities so I can have a blurry background
    pygame.draw.rect(translucentSurface,(16, 7, 54, 128),pygame.Rect(0,0,1280,720))#draws the a translucent rectangle onto the new surface, 4th element in colour array is opacity
    screen.blit(pygame.image.load("Assets/saveBackground.png"),(0,0))#puts the saved image on the back for something to draw onto and as a backdrop
    screen.blit(translucentSurface, (0,0))    #draw the new surface with the blurry stuff

    #main box
    pygame.draw.rect(screen, (16, 7, 54),pygame.Rect(384,64,512,592),border_radius=10)
    draw_text(screen,f"You defeated the {enemy_obj.name}","#FFFFFF",640,96,fontSize=32,centre=True)
    draw_text(screen,f"Choose a Reward:","#FFFFFF",640,120,fontSize=24,centre=True)


    #use this to highlight which reward is currently selected/hovered over
    reward_selection_colours = ["brown","brown","brown"]
    reward_selection_colours[menu_selected["Battle-Won"]]="#FFFFFF"

    #Rewards/Relics
    pygame.draw.rect(screen,reward_selection_colours[0], pygame.Rect(420,150,440,100),border_radius=10)
    pygame.draw.rect(screen,"#000000", pygame.Rect(422,152,436,96),border_radius=10)

    pygame.draw.rect(screen,"#FFFFFF", pygame.Rect(428,158,84,84),border_radius=2)
    screen.blit(pygame.transform.scale_by(icons[randomRelics[0].image],5),(430,160))

    draw_text(screen,randomRelics[0].name,"#FFFFFF",525,160,fontSize=36)
    draw_text(screen,randomRelics[0].description,"#FFFFFF",525,200,fontSize=16)
    draw_text(screen,randomRelics[0].effectDescription,"#FFFFFF",525,220,fontSize=16)



    pygame.draw.rect(screen,reward_selection_colours[1], pygame.Rect(420,270,440,100),border_radius=10)
    pygame.draw.rect(screen,"#000000", pygame.Rect(422,272,436,96),border_radius=10)

    pygame.draw.rect(screen,"#FFFFFF", pygame.Rect(428,278,84,84),border_radius=2)
    screen.blit(pygame.transform.scale_by(icons[randomRelics[1].image],5),(430,280))

    draw_text(screen,randomRelics[1].name,"#FFFFFF",525,280,fontSize=36)
    draw_text(screen,randomRelics[1].description,"#FFFFFF",525,320,fontSize=16)
    draw_text(screen,randomRelics[1].effectDescription,"#FFFFFF",525,340,fontSize=16)



    pygame.draw.rect(screen,reward_selection_colours[2], pygame.Rect(420,390,440,100),border_radius=10)
    pygame.draw.rect(screen,"#000000", pygame.Rect(422,392,436,96),border_radius=10)

    pygame.draw.rect(screen,"#FFFFFF", pygame.Rect(428,398,84,84),border_radius=2)
    screen.blit(pygame.transform.scale_by(icons[randomRelics[2].image],5),(430,400))

    draw_text(screen,randomRelics[2].name,"#FFFFFF",525,400,fontSize=36)
    draw_text(screen,randomRelics[2].description,"#FFFFFF",525,440,fontSize=16)
    draw_text(screen,randomRelics[2].effectDescription,"#FFFFFF",525,460,fontSize=16)

    #:D
    draw_text(screen,f":D","#FFFFFF",640,600,fontSize=24,centre=True)

    
    pygame.display.flip()

#player icon player health etc.
def draw_player_stats():
    pygame.draw.rect(screen, color="brown", rect=pygame.Rect(0,528,512,192))
    pygame.draw.rect(screen, color="black", rect=pygame.Rect(2,530,508,188))

    pygame.draw.rect(screen, color="brown", rect=pygame.Rect(30,558,132,132))
    pygame.draw.rect(screen, color="white", rect=pygame.Rect(32,560,128,128))
    screen.blit(player_selfie, (32,560))

    draw_text(screen, "HP",(255,255,255),192,560)
    pygame.draw.rect(screen, color="#550000", rect=pygame.Rect(192,590,256,32))
    pygame.draw.rect(screen, color="red", rect=pygame.Rect(192,590,256*(player_stats.hp/player_stats.max_hp),32))
    draw_text(screen,f"{player_stats.hp}/{player_stats.max_hp}","#FFFFFF",320,606,centre=True)

    draw_text(screen, "EP",(255,255,255),192,624)
    pygame.draw.rect(screen, color="#000055", rect=pygame.Rect(192,654,256,32))
    pygame.draw.rect(screen, color="#0000FF", rect=pygame.Rect(192,654,256*(player_stats.ep/player_stats.max_ep),32))
    draw_text(screen,f"{player_stats.ep}/{player_stats.max_ep}","#FFFFFF",320,670,centre=True)


#enemy name, hp
def draw_enemy_stats():
    pygame.draw.rect(screen, color="brown", rect=pygame.Rect(440,90,400,120))
    pygame.draw.rect(screen, color="black", rect=pygame.Rect(442,92,396,116))

    draw_text(screen, enemy_obj.name, "#FFFFFF", 640,125,fontSize=30,centre=True)

    draw_text(screen, "HP",(255,255,255),450,150)

    pygame.draw.rect(screen, color="#550000", rect=pygame.Rect(485,150,335,32))
    pygame.draw.rect(screen, color="red", rect=pygame.Rect(485,150,335*(enemy_obj.hp/enemy_obj.max_hp),32))
    
    draw_text(screen,f"{str(enemy_obj.hp)}/{str(enemy_obj.max_hp)}","#FFFFFF",640,166,0,centre=True)


#If player or enemy health goes over their max HP sets back down to max HP
def check_over_max_hp():
    if player_stats.hp > player_stats.max_hp:
        player_stats.hp = player_stats.max_hp
    
    if enemy_obj.hp > enemy_obj.max_hp:
        enemy_obj.hp = enemy_obj.max_hp


def check_battle_end():
    global randomRelics

    if player_stats.hp <= 0:
        pass
    if enemy_obj.hp <= 0:
        #End battle and go to battle won menu
        game_state.set_value("Battle-Won")
        # map[int(player_pos[1])][int(player_pos[0])] = 0

        #Choose 3 Random Relics
        # randomRelics = [random.choice(relics),random.choice(relics),random.choice(relics)]
        randomRelics = []
        for _ in range(3):
            randomRelics.append(random.choice(relics))
        draw_screen()



class battleAnimation():
    def __init__(self,animID="",length=30,x=32,y=32,scale=8):
        self.animID = animID
        if animID != "":
            self.frames = Spritesheet.animation(f"{animID}-Sheet",x,y,number_of_frames=10,scale=scale).frames
        else:
            self.frames = []

        self.lengthTime=length
        self.numberOfFrames = len(self.frames)



    def enemyMoveAnim(self,surface,x=0,y=0):
        c=1

        pygame.image.save(surface,"Assets/saveBattleAnimationBackground.png")

        # pygame.draw.rect(surface=surface, color="green", rect=pygame.Rect(c,c,c,c))

        # print(self.lengthTime//self.numberOfFrames)

        for _ in range(self.lengthTime):
            
            if c % (self.lengthTime/self.numberOfFrames) == 0:
                screen.blit(pygame.image.load("Assets/saveBattleAnimationBackground.png"),(0,0))
                screen.blit(self.frames[(c-1)//(self.lengthTime//self.numberOfFrames)],(x,y))
                # pygame.draw.rect(surface=surface, color="green", rect=pygame.Rect(c,c,c,c))
                pygame.display.flip()
            pygame.time.wait(int(1000/30))#1 frame,      (1000ms/30 frames)ms

            c+=1

    def transitionAnim(self,surface):
        c=1

        for _ in range(self.lengthTime):
            c+=1
            pygame.draw.rect(surface=surface, color="#000000", rect=pygame.Rect(0,0,c*64,720))

            pygame.display.flip()
            pygame.time.wait(int(1000/30))#1 frame,      (1000ms/30 frames)ms

    def playerMoveAnim(self,surface,x=0,y=0):
        c=1

        pygame.image.save(surface,"Assets/saveBattleAnimationBackground.png")

        
        # print(self.lengthTime//self.numberOfFrames)


        for _ in range(self.lengthTime):
            
            if c % (self.lengthTime/self.numberOfFrames) == 0:
                screen.blit(pygame.image.load("Assets/saveBattleAnimationBackground.png"),(0,0))
                screen.blit(self.frames[(c-1)//(self.lengthTime//self.numberOfFrames)],(x,y))
                # pygame.draw.rect(surface=surface, color="green", rect=pygame.Rect(c,c,c,c))
                pygame.display.flip()
            pygame.time.wait(int(1000/30))#1 frame,      (1000ms/30 frames)ms

            c+=1

            screen.blit(pygame.image.load("Assets/saveBattleAnimationBackground.png"),(0,0))

        

a = battleAnimation(animID="Fire2Enemy",x=16)

#main function
def main():
    global player_angle, brick, turnOrder, playerTurn, displayInv, enemy_obj,turnCounter

    player_angle = 0
    turnOrder = calculate_turn_order(player_stats,enemy_obj)
    

    
    draw_screen()
    running = True


    #main loop
    while running:        

        keys=pygame.key.get_pressed()
        if game_state.value == "Moving":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_o or event.key == pygame.K_i:#toggle inventory
                        displayInv = not displayInv #flip variable
                        # a.enemyMoveAnim(screen)
                        draw_screen()

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                if map[int(player_pos[1]-0.15* math.cos(math.radians(player_angle)) / abs(math.cos(math.radians(player_angle))) )][int(player_pos[0])].tileType != "Wall":
                    player_pos[1]-=0.05*math.cos(math.radians(player_angle))
                try: 
                    if map[int(player_pos[1])][int(player_pos[0]+0.15* math.sin(math.radians(player_angle)) / abs(math.sin(math.radians(player_angle))) )].tileType != "Wall":
                        player_pos[0]+=0.05*math.sin(math.radians(player_angle))
                except:
                    pass

            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                if map[int(player_pos[1]+0.15* math.cos(math.radians(player_angle)) / abs(math.cos(math.radians(player_angle))) )][int(player_pos[0])].tileType != "Wall":
                    player_pos[1]+=0.05*math.cos(math.radians(player_angle))
                try: 
                    if map[int(player_pos[1])][int(player_pos[0]-0.15* math.sin(math.radians(player_angle)) / abs(math.sin(math.radians(player_angle))) )].tileType != "Wall":
                        player_pos[0]-=0.05*math.sin(math.radians(player_angle))
                except:
                    pass

            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                player_angle -= 5
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                player_angle += 5
            
            if True in [keys[pygame.K_UP],keys[pygame.K_LEFT],keys[pygame.K_RIGHT],keys[pygame.K_w],keys[pygame.K_a],keys[pygame.K_d],keys[pygame.K_s],keys[pygame.K_DOWN]]:
                draw_screen()

            if map[int(player_pos[1])][int(player_pos[0])].spriteInfo=="S": #can change later so we in the centre 0.5 square
                new_maze()
                battleAnimation(length=20,).transitionAnim(screen)
                draw_screen()
            elif map[int(player_pos[1])][int(player_pos[0])].tileType=="Enemy":
                turnCounter = {"Player":0,"Enemy":0}
                turnOrder = calculate_turn_order(player_stats,enemy_obj)
                enemy_obj = load_enemy( map[int(player_pos[1])][int(player_pos[0])].spriteInfo )
                map[int(player_pos[1])][int(player_pos[0])] = tile("Path")
                battleAnimation(length=20,).transitionAnim(screen)

                draw_screen()
                pygame.display.flip()
                
                game_state.set_value("Battle")
                pygame.image.save(screen, "Assets/saveBackground.png")
                
   
        elif game_state.value == "Battle":
            player_stats.cancel_guard()

            if playerTurn == False:#ie enemy turn
                move = enemy_obj.choose_move()

                pygame.draw.rect(screen,"brown",pygame.Rect(192,256,192,64))
                pygame.draw.rect(screen,"black",pygame.Rect(194,258,188,60))
                draw_text(screen, f"{enemy_obj.name}","#FFFFFF",288,275,centre=True)
                draw_text(screen, f"used {move.name}","#FFFFFF",288,300,centre=True)


                a = battleAnimation(animID=move.anim,length=battleAnimTime,x=16,y=32)
                a.enemyMoveAnim(screen,576,480)

                enemy_obj.use_move(player_stats,move)
                # enemy_obj.make_move(player_stats)

                #update turns
                update_turn_counters(playerMoved=False)
                determine_turn()  

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:

                    #move around the menu
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        if menu_selected["Battle"] < 2:
                            menu_selected["Battle"] += 2
                        else:
                            menu_selected["Battle"] -= 2
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        if menu_selected["Battle"] % 2==0:
                            menu_selected["Battle"]+=1
                        else:
                            menu_selected["Battle"]-=1

                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        if menu_selected["Battle"] % 2==0:
                            menu_selected["Battle"]+=1
                        else:
                            menu_selected["Battle"]-=1
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        if menu_selected["Battle"] < 2:
                            menu_selected["Battle"] += 2
                        else:
                            menu_selected["Battle"] -= 2


                    if playerTurn:
                        if event.key == pygame.K_SPACE:
                            if menu_selected["Battle"] == 0:#attack
                                battleAnimation("Physical1Player",length=battleAnimTime,x=16,y=32).playerMoveAnim(screen,576,360)

                                deal_damage(player_stats,enemy_obj)
                                playerTurn = False
                                update_turn_counters()
                                determine_turn()

                            elif menu_selected["Battle"] == 1:#energy
                                game_state.set_value("Battle-Energy")

                            elif menu_selected["Battle"] == 2:#item
                                # player_stats.hp+=2
                                if len(player_stats.items):#if inventory isn't empty
                                    game_state.set_value("Battle-Item")
                                else:
                                    pass #Error sound

                            elif menu_selected["Battle"] == 3:#guard
                                # player_stats.hp -= 2
                                player_stats.guard()
                                playerTurn = False
                                update_turn_counters()
                                determine_turn()

                        
                    

            if tick_timers["Battle"] < 27: #(10-1)*3 #refer to draw battle UI to see animation, each frame 3 ticks
                tick_timers["Battle"] += 1

            
            #draw things onto screen
            draw_battle_UI()

            battle_sprites(enemy_obj.ID).draw_enemy()
            draw_player_stats()
            draw_enemy_stats()

            check_battle_end()


            

            pygame.display.flip()

        elif game_state.value == "Battle-Energy":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                        game_state.set_value("Battle")

                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        # print("HI")
                        if menu_selected["Battle-Energy"] < 2:
                            menu_selected["Battle-Energy"] += 2
                        else:
                            menu_selected["Battle-Energy"] -= 2
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        if menu_selected["Battle-Energy"] % 2==0:
                            menu_selected["Battle-Energy"]+=1
                        else:
                            menu_selected["Battle-Energy"]-=1

                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        if menu_selected["Battle-Energy"] % 2==0:
                            menu_selected["Battle-Energy"]+=1
                        else:
                            menu_selected["Battle-Energy"]-=1
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        # print("HI")
                        if menu_selected["Battle-Energy"] < 2:
                            menu_selected["Battle-Energy"] += 2
                        else:
                            menu_selected["Battle-Energy"] -= 2
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        

                        move = player_stats.energyMoves[menu_selected["Battle-Energy"]]


                        if player_stats.ep >= move.EPcost:
                            game_state.set_value("Battle")
                            playerTurn = False
                            
                            update_turn_counters()
                            determine_turn()
                            

                            player_stats.ep -= move.EPcost

                            energyDamage=0

                            if move.physicalValue != 0:
                                tempDamage = (move.physicalValue+player_stats.physicalStrength)*1.25-enemy_obj.defence
                                if tempDamage > 0:
                                    energyDamage+=tempDamage
                            if move.fireValue != 0:
                                tempDamage = (move.fireValue*player_stats.fireStrength)*1.25-(enemy_obj.defence*enemy_obj.fireDefence)
                                if tempDamage > 0:
                                    energyDamage+=tempDamage
                            if move.earthValue != 0:
                                tempDamage = (move.earthValue*player_stats.earthStrength)*1.25-(enemy_obj.defence*enemy_obj.earthDefence)
                                # print(enemy_obj.earthDefence)
                                if tempDamage > 0:
                                    energyDamage+=tempDamage
                            if move.iceValue != 0:
                                tempDamage = (move.iceValue*player_stats.iceStrength)*1.25-(enemy_obj.defence*enemy_obj.iceDefence)
                                if tempDamage > 0:
                                    energyDamage+=tempDamage

                            if move.animID != "None":
                                battleAnimation(f"{move.animID}Player",length=battleAnimTime,x=32,y=16,scale=6).playerMoveAnim(screen,640,360)

                            player_stats.hp += move.healValue
                            enemy_obj.hp -= int(energyDamage)



                        else:
                            pass#add error noise rahah type noise



                    
            

            draw_battle_energy_UI()
            draw_enemy_stats()
            draw_player_stats()

            check_over_max_hp()
            check_battle_end()

            pygame.display.flip()

        elif game_state.value == "Battle-Item":
            numItems = len(player_stats.items.keys())

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                        game_state.set_value("Battle")

                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        if menu_selected["Battle-Item"]==0:
                            menu_selected["Battle-Item"] = numItems-1
                        else:
                            menu_selected["Battle-Item"] -= 1

                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        if menu_selected["Battle-Item"]==numItems-1:
                            menu_selected["Battle-Item"] = 0
                        else:
                            menu_selected["Battle-Item"] += 1

                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        selectedItem = list(player_stats.items.keys())[menu_selected["Battle-Item"]]
                        player_stats.items[selectedItem] -= 1

                        if player_stats.items[selectedItem] == 0:
                            
                            player_stats.items.pop(selectedItem)
                            
                            if menu_selected["Battle-Item"] == numItems-1:
                                menu_selected["Battle-Item"] -= 1
                                numItems -= 1

                        if selectedItem.effectType == "Heal":
                            player_stats.hp += selectedItem.potency
                        elif selectedItem.effectType == "Damage":
                            battleAnimation("Physical1Player",length=battleAnimTime,x=16,y=32).playerMoveAnim(screen,576,360)
                            enemy_obj.hp -= selectedItem.potency


                        game_state.set_value("Battle")
                        playerTurn = False
                        update_turn_counters()
                        determine_turn()

    

             

            if len(player_stats.items): #if items isnt empty
                draw_battle_item_UI()
            draw_enemy_stats()
            draw_player_stats()

            check_over_max_hp()
            check_battle_end()

            pygame.display.flip()

        elif game_state.value == "Battle-Won":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_SPACE, pygame.K_RETURN):
                        game_state.set_value("Moving")
                        draw_screen()
                        pygame.display.flip()

                        # player_stats.relics.append("Speed Syringe")
                        # player_stats.speed *= 1.1

                        player_stats.relics.append(randomRelics[menu_selected["Battle-Won"]].name)
                        relic_apply_stat_change(player_stats, randomRelics[menu_selected["Battle-Won"]])

                        break
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        menu_selected["Battle-Won"] = (menu_selected["Battle-Won"]-1)% 3#cycle up, %3 to go back to the bottom
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        menu_selected["Battle-Won"] = (menu_selected["Battle-Won"]+1)%3 #cycle down, %3 to go back to the top


            if game_state.value != "Battle-Won":#ie there has been a state change so I don't want to draw all the bottom stuff
                #this happens above when a reward is selected
                #so we continue out of the statement
                continue


            draw_battle_won_UI()

        clock.tick(FPS)  

    pygame.quit()


if __name__ == '__main__':
    main()