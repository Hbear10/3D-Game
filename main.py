import pygame
from PIL import Image
import math
import time
#import random
import maze

from render import *

print("Hello World!")

map = [[1,1,1,1,1],
       [1,1,0,0,1],
       [1,1,0,1,1],
       [1,0,0,0,1],
       [1,0,0,0,1],
       [1,0,"W",1,1],
       [1,1,1,1,1]]

# map = [[1,1,1,1,],
#         [1,0,0,1],
#         [1,0,0,1],
#         [1,"W",1,1],
#         [1,1,1,1]]

player_pos = [2.5,5.5]

map,player_pos = maze.maze_generate(11)

#player_pos[0]+=1.5
#player_pos[1]+=1.5
#print(map,player_pos)
raycast_column_width = 2
raycast_resolution = FOV / (1280 / raycast_column_width)

pygame.init()
screen = pygame.display.set_mode((1280,720))

clock = pygame.time.Clock()
running = True

planes_to_draw = []

player_angle = 0 #in degrees, gets turned into radians later


class image():
    def __init__(self,image_name):
        self.main_image = Image.open("Assets/"+image_name)
        self.width = (self.main_image.size)[0]
        self.height = (self.main_image.size)[1]
        self.img_slices = []
        for i in range(self.width):
            self.img_slices.append(self.main_image.crop((i,0,i+1,16)))
    

brick = image("Brick.png")
#print(brick.img_slices[5].show())


ray_slice = brick.img_slices[5].transform((raycast_column_width,320),Image.Transform.EXTENT,[0,0,1,16])#.show()
pygame_surface = pygame.image.fromstring(ray_slice.tobytes(),ray_slice.size,ray_slice.mode).convert()



def draw_beam(x_point,distance,image_index): #literally just takes the point along the screen and draws a line based on distance away from the camera
    if distance > 1:
        colour_index = 1/distance
    else:
        colour_index = 1

    #ray_slice = brick.img_slices[5].transform((1,16),Image.Transform.AFFINE,[1,0,0,0,2,0]).show()


    ray_slice = brick.img_slices[image_index].transform((raycast_column_width,int(450/distance)),Image.Transform.EXTENT,[0,0,1,16])#.show()
    pygame_surface = pygame.image.fromstring(ray_slice.tobytes(),ray_slice.size,ray_slice.mode).convert()
    screen.blit(pygame_surface, pygame_surface.get_rect(center = (x_point+(raycast_column_width//2), 360)))
    
    #pygame.draw.rect(screen,color=(0, int(255*colour_index), int(255*colour_index) ),rect=pygame.Rect(x_point,360-(300/distance)/2,raycast_column_width,300/distance))


def smaller_point_dist(pointA,pointB,pointReference): # takes 3 points, and compares the first 2 to the third and returns the nearest point and the distance
    distA = math.sqrt((pointA[0]-pointReference[0])**2+(pointA[1]-pointReference[1])**2) #pythagoras
    distB = math.sqrt((pointB[0]-pointReference[0])**2+(pointB[1]-pointReference[1])**2) #pythagoras
    if distA < distB:
        return pointA, distA
    else:
        return pointB, distB


def raycast():
    t= time.perf_counter()

    count = 0
    ray_pos=[1.5,2.5]
    while count < 1280//raycast_column_width:
        ray_pos[0],ray_pos[1] = player_pos #index-coord: 0=x, 1=y  ,note to self that the map indexing is y,x not x,y
        ray_pos_grid = [int(ray_pos[0]),int(ray_pos[1])] #gets the index on the map/array of the player
        ray_distance = 0
        is_blocked = False

        DIST = 500 #dist is a constant of distance to imaginary wall that we are casting on
        angle = math.radians((math.degrees(math.atan((count*raycast_column_width-640) / DIST))+player_angle)%360) #math.radians((raycast_resolution*count-(FOV/2)+player_angle)%360)
        #This uses angles with fixed pixel increments instead of fixed angle increments which removes distortion on the sides of the screen more info in the doc

        side_step_x = [0,0] #points of the ray where they move to the next grid line along the x, or y
        side_step_y = [0,0]


        x_direction = 1 #these are for if the x and y go up or down
        y_direction = 1

        if angle <= 1.5707 or angle > 4.712: #up
            y_direction= -1
        if angle >3.14159: #left
            x_direction= -1

        while not is_blocked:
            degree_angles = math.degrees(angle)

            if map[ray_pos_grid[1]][ray_pos_grid[0]] == 1:#if there is a wall
                is_blocked = True
                
                image_index=0
                if degree_angles%180==0:
                    image_index = int((ray_pos[0]%1)/0.0625)
                elif degree_angles%90==0:
                    image_index = int((ray_pos[1]%1)/0.0625)
                elif ray_pos == side_step_x:
                    image_index = int((ray_pos[1]%1)/0.0625)
                elif ray_pos == side_step_y:
                    image_index = int((ray_pos[0]%1)/0.0625)

                draw_beam(count*raycast_column_width,round(ray_distance*math.cos(math.radians(player_angle)-angle),5),image_index)#function, calculate the spot along the screen and the true distance with fixed for fish bowl distortion
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
                            ray_pos[0]=int(ray_pos[0])
                            ray_pos_grid[0]-=2
                    
                    elif ray_pos == player_pos:
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
                        side_step_x=[ray_pos[0]+x_direction,ray_pos[1]-scale_y]
                    elif ray_pos==side_step_y:
                        side_step_y = [ray_pos[0]-scale_x,ray_pos[1]+y_direction]


                if degree_angles%90!=0:
                    ray_pos,distance_travelled = smaller_point_dist(side_step_x,side_step_y,ray_pos)
                    
                    if ray_pos == side_step_x:
                        ray_pos_grid[0]+=x_direction
                    elif ray_pos == side_step_y:
                        ray_pos_grid[1]+=y_direction
                

                ray_distance+=distance_travelled


        count+=1
    print(time.perf_counter()-t)


def draw_screen():
    screen.fill("dark grey")
    pygame.draw.rect(screen,(34,34,34), pygame.Rect(0,0,1280,360))
    raycast()
    
    pygame.display.flip()


draw_screen()


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                player_angle_confined = player_angle%360 #angle confined to 0<=theta<=360
                if player_angle_confined == 0:
                    player_pos[1]-=0.25
                elif player_angle_confined == 90:
                    player_pos[0]+=0.25
                elif player_angle_confined == 180:
                    player_pos[1]+=0.25
                elif player_angle_confined == 270:
                    player_pos[0]-=0.25
                draw_screen()
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                for _ in range(30):
                    player_angle-=3
                    draw_screen()
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                player_angle+=90
                draw_screen()


    clock.tick(30)  

pygame.quit()