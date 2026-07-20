import pygame
from PIL import Image
import math
#import time

import maze
import block_scan
import Enum
import Spritesheet
#from render import *

print("Hello World!")

#The traversable map is stored as a 2D array
map = [[1,1,1,1,1,1,1,1,1],
       [1,0,0,0,0,0,0,0,1],
       [1,0,"S",0,1,1,1,1,1],
       [1,0,0,0,1],
       [1,0,"S",0,1],
       [1,0,0,0,1],
       [1,0,"S",0,1],
       [1,0,1,0,1],
       [1,0,0,0,1],
       [1,0,"B",0,1],
       [1,0,0,0,1],
       [1,0,"W",0,1],#W on this line is just an indicator for me for where the player starts, it doesn't affect any processing
       [1,1,1,1,1]]

player_pos = [2.5,10.5]#The coordinate of the player, (xy)

FOV = 100 #The field of view of the player

def new_maze():
    global map, player_pos

    map,player_pos = maze.maze_generate(11)


raycast_column_width = 2 #The width of each pixel column, increase it to improve performance as it reduces the amount of rays sent


pygame.init()
screen = pygame.display.set_mode((1280,720)) #720p

clock = pygame.time.Clock()#Used later to set FPS cap
game_font = pygame.font.Font('Evil Empire.otf', 24)

player_angle=0 # Direction the player is facing

class wall_image():
    def __init__(self,image_name):
        self.main_image = Image.open("Assets/"+image_name)
        self.width = (self.main_image.size)[0]
        self.height = (self.main_image.size)[1]
        self.img_slices = []
        for i in range(self.width):
            self.img_slices.append(self.main_image.crop((i,0,i+1,16)))



class battle_sprites():
    def __init__(self, image_name, resolution=32):
        self.resolution = resolution
        self.battle_image = pygame.image.load(f"assets/{image_name}.png").convert_alpha()
        self.battle_image = pygame.transform.scale_by(self.battle_image,(256/resolution))

    def draw_enemy(self):
        img_rect = self.battle_image.get_rect()
        img_rect.center=(640,360)
        screen.blit(self.battle_image,img_rect)
        

enemy = battle_sprites("FireSlimeKing")


class battle_container():
    def __init__(self,max_hp=10,max_ep=10,strength=10,defence=10):
        self.max_hp=max_hp
        self.hp=max_hp
        self.max_ep = max_ep
        self.ep=max_ep

        self.strength = 10
        self.defence = 10
        


class player_battle_container(battle_container):
    pass

player_stats = player_battle_container()


door = Image.open("Assets/Door.png")

sprites_loaded = {"door" : pygame.image.load("Assets/Door.png").convert_alpha()}

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
menu_selected = {"Battle":0}

class sprite_obj():
    def __init__(self,x,y):
        self.sprite_image = sprites_loaded["door"]
        self.sprite_x = x
        self.sprite_y = y
        self.distance = math.sqrt((x-player_pos[0])**2+(y-player_pos[1])**2)* math.cos(math.radians(90) + math.radians(player_angle)-math.atan2( (player_pos[1]-(y)) , (player_pos[0]-(x))))
        self.left_point = 0
        self.right_point = 16



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


def draw_beam(x_point,distance,image_index): #literally just takes the point along the screen and draws a line based on distance away from the camera, image index is for what column along an image to take
    ray_slice = brick.img_slices[image_index].transform((raycast_column_width,int(360/distance)),Image.Transform.EXTENT,[0,0,1,16]) #transforms the image slice to the right size, 
    pygame_surface = pygame.image.fromstring(ray_slice.tobytes(),ray_slice.size,ray_slice.mode).convert() #Turns the PIL image into a pygame image
    screen.blit(pygame_surface, pygame_surface.get_rect(center = (x_point+(raycast_column_width//2), 360))) # Draws the image slice onto the screen



def smaller_point_dist(pointA,pointB,pointReference): # takes 3 points, and compares the first 2 to the third and returns the nearest point and the distance
    distA = math.sqrt((pointA[0]-pointReference[0])**2+(pointA[1]-pointReference[1])**2) #pythagoras
    distB = math.sqrt((pointB[0]-pointReference[0])**2+(pointB[1]-pointReference[1])**2) #pythagoras
    if distA < distB:#return the closer point and the distance
        return pointA, distA
    else:
        return pointB, distB

#code for the each individual ray, this uses the DDA algorithm to calculate the distance. 
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

        if map[ray_pos_grid[1]][ray_pos_grid[0]] == "S":#if there are any sprites on the screen that should be rendered
            if (ray_pos_grid[0],ray_pos_grid[1]) not in sprites_pos_that_can_be_rendered:
                #print(degree_angles)
                sprites_pos_that_can_be_rendered.append( (ray_pos_grid[0],ray_pos_grid[1]) ) 
                sprites.append( sprite_obj(ray_pos_grid[0]+0.5,ray_pos_grid[1]+0.5) )
            else:
                sprites[-1].left_point = 0

        if map[ray_pos_grid[1]][ray_pos_grid[0]] == 1:#if there is a wall
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
            
            return (round(ray_distance*math.cos(math.radians(player_angle)-angle),5),image_index)#returns the distance to a wall (multipled by the cos of the angle to fix distortion) and the image index
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
        draw_beam(i*raycast_column_width,ray_store[i][0],ray_store[i][1])

    #print(time.perf_counter()-t)


def draw_text(surface,text:str,colour:str,left: float,top: float,angle=0,fontSize=24):
    text_surface = pygame.font.Font('Evil Empire.otf', fontSize).render(text, True, colour)  #create text box in chosen colour
    text_surface = pygame.transform.rotate(text_surface,-angle)
    text_rect = text_surface.get_rect()                #
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



        if sprite_distance > 0.04 and (90> (math.degrees(sprite_bearing)+player_angle)%360 or (math.degrees(sprite_bearing)+player_angle)%360>270) and sprite.left_point != sprite.right_point:
            sprite_scale_by = (20/sprite_distance) 
            screen.blit(pygame.transform.scale_by(sprites_loaded["door"],sprite_scale_by),                        #image
                        (640-(160/sprite_distance) - int(500*math.tan(sprite_bearing+math.radians(player_angle))-sprite_scale_by*sprite.left_point),#x start,  - the scale left point because - move it left and then fix to write spot
                                    (360-(8*sprite_scale_by))),                                                   #y start              
                        (sprite_scale_by*sprite.left_point,0,(sprite.right_point)*sprite_scale_by,16*sprite_scale_by))
    


def draw_screen():
    screen.fill("dark grey")
    pygame.draw.rect(screen,(34,34,34), pygame.Rect(0,0,1280,360))
    raycast()
    #print(sprites)
    draw_sprites()
    pygame.display.flip()


def draw_battle_UI():
    if tick_timers["Battle"]%3==0 and tick_timers["Battle"] != 27:
        #draw_screen()
        screen.blit(pygame.image.load("Assets/saveBackground.png"),(0,0))
    
    else:
        pass

    screen.blit(arms[tick_timers["Battle"]//3],(768,208))#animate in the arm
    if tick_timers["Battle"] >= 27:
        #background panel of UI - Draw options onto this
        pygame.draw.polygon(screen,"#3ec54b", ((980,440),(1220,565),(1195,650),(950,520)) )

        optionColours = ["#d4e650","#d4e650","#d4e650","#d4e650"]
        optionColours[menu_selected["Battle"]] = "#FF0000"


        
        draw_text(screen,"Attack",optionColours[0],990,450,34,40)
        draw_text(screen,"Energy",optionColours[1],1095,520,34,40)
        draw_text(screen,"Item",optionColours[2],980,495,34,40)
        draw_text(screen,"Guard",optionColours[3],1075,550,34,40)



def draw_player_stats():
    pygame.draw.rect(screen, color="brown", rect=pygame.Rect(0,528,512,192))
    pygame.draw.rect(screen, color="black", rect=pygame.Rect(2,530,508,188))

    pygame.draw.rect(screen, color="brown", rect=pygame.Rect(30,558,132,132))
    pygame.draw.rect(screen, color="white", rect=pygame.Rect(32,560,128,128))
    screen.blit(player_selfie, (32,560))

    draw_text(screen, "HP",(255,255,255),192,560)
    pygame.draw.rect(screen, color="red", rect=pygame.Rect(192,590,256,32))

    draw_text(screen, "EP",(255,255,255),192,624)
    pygame.draw.rect(screen, color="blue", rect=pygame.Rect(192,654,256,32))

    

def main():
    global player_angle, brick
    player_angle = 0

    brick = wall_image("Brick.png")
    #print(brick.img_slices[5].show())


    #ray_slice = brick.img_slices[5].transform((raycast_column_width,300),Image.Transform.EXTENT,[0,0,1,16])#.show()
    #pygame_surface = pygame.image.fromstring(ray_slice.tobytes(),ray_slice.size,ray_slice.mode).convert()

    draw_screen()

    #turning = 0
    running = True

    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # if event.key == pygame.K_w or event.key == pygame.K_UP:
                #     player_angle_confined = player_angle%360 #angle confined to 0<=theta<=360
                #     if player_angle_confined == 0:
                #         pass
                #         #player_pos[1]-=0.25
                #     elif player_angle_confined == 90:
                #         player_pos[0]+=0.25
                #     elif player_angle_confined == 180:
                #         player_pos[1]+=0.25
                #     elif player_angle_confined == 270:
                #         player_pos[0]-=0.25
                #     draw_screen()
                # if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                #     if turning == 0:
                #         turning =-5
                        
                #if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    #if turning == 0:
                        #turning = 5
                pass
                    

        keys=pygame.key.get_pressed()
        if game_state.value == "Moving":
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                if map[int(player_pos[1]-0.15* math.cos(math.radians(player_angle)) / abs(math.cos(math.radians(player_angle))) )][int(player_pos[0])] != 1:
                    player_pos[1]-=0.05*math.cos(math.radians(player_angle))
                try: 
                    if map[int(player_pos[1])][int(player_pos[0]+0.15* math.sin(math.radians(player_angle)) / abs(math.sin(math.radians(player_angle))) )] != 1:
                        player_pos[0]+=0.05*math.sin(math.radians(player_angle))
                except:
                    pass
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                player_angle -= 5
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                player_angle += 5
            
            if True in [keys[pygame.K_UP],keys[pygame.K_LEFT],keys[pygame.K_RIGHT],keys[pygame.K_w],keys[pygame.K_a],keys[pygame.K_d]]:
                draw_screen()

            if map[int(player_pos[1])][int(player_pos[0])]=="S": #can change later so we in the centre 0.5 square
                new_maze()
                draw_screen()
            elif map[int(player_pos[1])][int(player_pos[0])]=="B":
                game_state.set_value("Battle")
                pygame.image.save(screen, "Assets/saveBackground.png")
            
        elif game_state.value == "Battle":
            if tick_timers["Battle"] < 27: #(10-1)*3 #refer to draw battle UI to see animation, each frame 3 ticks
                tick_timers["Battle"] += 1

            #print("Hi")
            draw_battle_UI()

            enemy.draw_enemy()
            draw_player_stats()

            # for event in pygame.event.get():
            #     if event.type == pygame.KEYUP:
            #         if event.key == pygame.K_w or event.key == pygame.K_UP:
            #             if menu_selected["Battle"] < 2:
            #                 menu_selected["Battle"] += 2
            #             else:
            #                 menu_selected["Battle"] -= 2
            # if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            #     player_angle -= 5
            # if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            #     player_angle += 5
            
            # if True in [keys[pygame.K_UP],keys[pygame.K_LEFT],keys[pygame.K_RIGHT],keys[pygame.K_w],keys[pygame.K_a],keys[pygame.K_d]]:
            #     draw_battle_UI()

            

            pygame.display.flip()


        # if turning != 0:
        #     player_angle+=turning
        #     draw_screen()
        #     if player_angle%90==0:
        #         turning=0

        clock.tick(30)  

    pygame.quit()


if __name__ == '__main__':
    main()