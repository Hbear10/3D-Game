import pygame
import math
import time
#import random

from render import *

print("Hello World!")

map = [[1,1,1,1,1],
       [1,1,0,0,1],
       [1,1,0,1,1],
       [1,0,0,0,1],
       [1,0,0,0,1],
       [1,0,"W",1,1],
       [1,1,1,1,1]]

map = [[1,1,1,1,],
        [1,0,0,1],
        [1,"W",1,1],
        [1,1,1]]
raycast_column_width = 1
raycast_resolution = FOV / (1280 / raycast_column_width)
print(raycast_resolution)

pygame.init()
screen = pygame.display.set_mode((1280,720))

clock = pygame.time.Clock()
running = True

planes_to_draw = []
player_pos = [1.5,2.5]
player_angle = 0 #in degrees, gets turned into radians later


def draw_beam(x_point,distance):
    if distance > 1:
        colour_index = 1/distance
    else:
        colour_index = 1
    pygame.draw.rect(screen,color=(0, int(255*colour_index), int(255*colour_index) ),rect=pygame.Rect(x_point,360-(300/distance)/2,raycast_column_width,300/distance))


def smaller_point_dist(pointA,pointB,pointReference):
    distA = math.sqrt((pointA[0]-pointReference[0])**2+(pointA[1]-pointReference[1])**2)
    distB = math.sqrt((pointB[0]-pointReference[0])**2+(pointB[1]-pointReference[1])**2)
    if distA < distB:
        return pointA, distA
    else:
        return pointB, distB


def raycast():
    t= time.time()
    count = 0
    ray_pos=[1.5,2.5]
    while count < 1280//raycast_column_width:
        ray_pos[0],ray_pos[1] = player_pos #index-coord: 0-x, 1-y  ,note to self that the map is y,x not x,y
        ray_pos_grid = [int(ray_pos[0]),int(ray_pos[1])]
        ray_distance = 0
        is_blocked = False
        DIST = 500 #dist is a constant of distance to imaginary wall that we are casting on
        angle = math.radians((math.degrees(math.atan((count-640) / DIST))+player_angle)%360) #math.radians((raycast_resolution*count-(FOV/2)+player_angle)%360)
        #print(angle)
        #ray_index = 0.0025 #how much we increase by
        #print(1)

        side_step_x = [0,0]
        side_step_y = [0,0]


        x_direction = 1 #these are for if the x and y go up or down
        y_direction = 1

        if angle <= 1.5707 or angle > 4.712:
            y_direction= -1
        if angle >3.14159:
            x_direction= -1

        while not is_blocked:
            if map[ray_pos_grid[1]][ray_pos_grid[0]] == 1:
                is_blocked = True
                #if ray_pos[0]%1==0:
                draw_beam(count*raycast_column_width,ray_distance*math.cos(math.radians(player_angle)-angle))
                #else:
                 #   draw_beam(count*raycast_column_width,ray_distance*math.cos(math.radians(player_angle)-angle))
            else:
                #direction_vector = [math.cos(angle),math.sin(angle)]

                

                if math.degrees(angle)%90!=0:
                    scale_x = math.tan(angle)*y_direction   #ok so I changed the maths no longer -> sx=root(1^2+(dy/dx)^2) #when y +1 x+scale+x
                    scale_y = 1/math.tan(angle)*x_direction          #sx=root(1^2+(dx/dy)^2)
                else:
                    if math.degrees(angle)==0:
                        scale_x=0
                        scale_y=-1
                    elif math.degrees(angle)==90:
                        scale_x=1
                        scale_y=0
                    elif math.degrees(angle)==180:
                        scale_x=0
                        scale_y=1
                    elif math.degrees(angle)==270:
                        scale_x=-1
                        scale_y=0


                if math.degrees(angle)%90==0:#hardcoding for when tan = 0 or i
                    if ray_pos == player_pos and ray_pos[0]%1!=0 and ray_pos[1]%1!=0:#not on grid lines
                        #print(1)
                        if math.degrees(angle) == 0:
                            
                            distance_travelled=ray_pos[1]-int(ray_pos[1])
                            ray_pos_grid[1]-= math.ceil(ray_pos[1]%1)

                            ray_pos[1]=int(ray_pos[1])

                            
                            print((ray_pos[1]%1))
                        elif math.degrees(angle) == 90:
                            #print(111)
                            
                            distance_travelled=math.ceil(ray_pos[0])-ray_pos[0]
                            ray_pos[0]=math.ceil(ray_pos[0])

                            #print(ray_pos,player_pos)
                            ray_pos_grid[0]+=1
                        elif math.degrees(angle) == 180:
                            distance_travelled=math.ceil(ray_pos[1])-ray_pos[1]
                            ray_pos_grid[1]+=math.ceil(ray_pos[1]%1)

                            ray_pos[1]=math.ceil(ray_pos[1])

                        elif math.degrees(angle) == 270:
                            distance_travelled=ray_pos[0]-int(ray_pos[0])
                            print(distance_travelled,111)
                            ray_pos[0]=int(ray_pos[0])

                            ray_pos_grid[0]-=1
                    elif ray_pos == player_pos and ray_pos[1]%1==0:#when on y grid
                        if math.degrees(angle) == 0:
                            distance_travelled=1
                            ray_pos_grid[1]-= 1
                            ray_pos[1]=int(ray_pos[1])
                            print((ray_pos[1]%1))
                        elif math.degrees(angle) == 90:
                            #print(111)
                            
                            distance_travelled=math.ceil(ray_pos[0])-ray_pos[0]
                            ray_pos[0]=math.ceil(ray_pos[0])

                            ray_pos_grid[0]+=1

                            print(ray_pos_grid)
                        elif math.degrees(angle) == 180:
                            distance_travelled=1
                            ray_pos_grid[1]+=1
                            ray_pos[1]=math.ceil(ray_pos[1])

                        elif math.degrees(angle) == 270:
                            distance_travelled=ray_pos[0]-int(ray_pos[0])
                            print(distance_travelled,111)
                            ray_pos[0]=int(ray_pos[0])

                            ray_pos_grid[0]-=1
                    elif ray_pos == player_pos and ray_pos[0]%1==0:#when on x grid
                        if math.degrees(angle) == 0:
                            distance_travelled=ray_pos[1]-int(ray_pos[1])
                            ray_pos_grid[1]-= 1
                            ray_pos[1]=int(ray_pos[1])
                            #print((ray_pos[1]%1))
                        elif math.degrees(angle) == 90:
                            #print(111)
                            
                            distance_travelled=1
                            ray_pos[0]=math.ceil(ray_pos[0])

                            ray_pos_grid[0]+=1

                            #print(ray_pos_grid)
                        elif math.degrees(angle) == 180:
                            distance_travelled=math.ceil(ray_pos[1])-ray_pos[1]
                            ray_pos_grid[1]+=1
                            ray_pos[1]=math.ceil(ray_pos[1])

                        elif math.degrees(angle) == 270:
                            distance_travelled=1
                            #print(distance_travelled,111)
                            ray_pos[0]=int(ray_pos[0])

                            ray_pos_grid[0]-=1
                    else:
                        print(2222222)
                        ray_pos[0] += scale_x
                        ray_pos[1] += scale_y
                        ray_pos_grid[0] += x_direction
                        ray_pos_grid[1] += y_direction
                        distance_travelled=1
                #side step x is where x+=1, y is for y+=1
                elif ray_pos==player_pos and ray_pos[0]%1!=0 and ray_pos[1]%1!=0:
                    
                    
                    #if angle !=90:
                    if x_direction == 1:#right
                        side_step_x = [math.ceil(ray_pos[0]),ray_pos[1]-(-ray_pos[0]+math.ceil(ray_pos[0]))*scale_y]
                    else: #left
                        side_step_x = [int(ray_pos[0]),ray_pos[1]+(-ray_pos[0]+int(ray_pos[0]))*scale_y]


                    if y_direction == 1:#dwon
                        side_step_y = [ray_pos[0]-(-ray_pos[1]+math.ceil(ray_pos[1]))*scale_x,math.ceil(ray_pos[1])]
                    else: # same as ==-1, up
                        side_step_y = [ray_pos[0]+(-ray_pos[1]+int(ray_pos[1]))*scale_x,int(ray_pos[1])]
                        
                        #print(side_step_x,side_step_y)

                    distance_travelled = 0
                    ray_pos,distance_travelled = smaller_point_dist(side_step_x,side_step_y,ray_pos)
                    
                elif ray_pos==player_pos and ray_pos[0]%1==0 and ray_pos[1]%1!=0:
                    side_step_x=[ray_pos[0]+x_direction,ray_pos[1]-scale_y]
                    
                    if y_direction == 1:#dwon
                        side_step_y = [ray_pos[0]-(-ray_pos[1]+math.ceil(ray_pos[1]))*scale_x,math.ceil(ray_pos[1])]
                    else: # same as ==-1, up
                        side_step_y = [ray_pos[0]+(-ray_pos[1]+int(ray_pos[1]))*scale_x,int(ray_pos[1])]

                    distance_travelled = 0
                    ray_pos,distance_travelled = smaller_point_dist(side_step_x,side_step_y,ray_pos)

                elif ray_pos==player_pos and ray_pos[0]%1!=0 and ray_pos[1]%1==0:
                    #if y_direction == -1:
                    #ray_pos[1] = player_pos[1] - 1
                        #print(123456)

                    # print(ray_pos)
                    if x_direction == 1:#right
                        side_step_x = [math.ceil(ray_pos[0]),ray_pos[1]-(-ray_pos[0]+math.ceil(ray_pos[0]))*scale_y]
                    else: #left
                        side_step_x = [int(ray_pos[0]),ray_pos[1]+(-ray_pos[0]+int(ray_pos[0]))*scale_y]


                    if y_direction == -1:
                        side_step_y = [ray_pos[0]-scale_x,ray_pos[1]+x_direction] 
                        print("!!!!!!!")
                    else:
                        side_step_y = [ray_pos[0]-scale_x,ray_pos[1]+x_direction] 

                    #print(ray_pos,side_step_x,side_step_y)
                    distance_travelled = 0
                    ray_pos,distance_travelled = smaller_point_dist(side_step_x,side_step_y,ray_pos)

                else:
                    
                    if ray_pos==side_step_x:
                        side_step_x=[ray_pos[0]+x_direction,ray_pos[1]-scale_y]
                    elif ray_pos==side_step_y:
                        side_step_y = [ray_pos[0]-scale_x,ray_pos[1]+y_direction]


                    ray_pos,distance_travelled = smaller_point_dist(side_step_x,side_step_y,ray_pos)
                    #print(angle, ray_pos)


                if math.degrees(angle)%90!=0:
                    #print(ray_pos)
                    if ray_pos == side_step_x:
                        ray_pos_grid[0]+=x_direction
                        #print(x_direction)
                    elif ray_pos == side_step_y:
                        ray_pos_grid[1]+=y_direction
                    else:
                        print("HUUUUUUUUUUUUUUUUUUUUUUh")
                


                    #if y_direction <1:
                        #side_step_y = [ray_pos[0]+(ray_pos[1]),int(ray_pos[1])]

                    #new_x = [int(ray_pos[0]),ray_pos[1]+x_direction*scale_x]
                    #print(new_x)

                    #if abs(angle) > 45:
                     #   pass


                ray_distance+=distance_travelled
                if angle==0:
                    print(ray_pos,ray_distance,angle)
                #ray_pos[0] += math.sin(angle)*ray_index       #sin(theta)*n
                #ray_pos[1] -= math.cos(angle)*ray_index       #cos(theta)*n, minus because as you go up it decreases index

        count+=1
    print(time.time()-t)

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
                for _ in range(45):
                    player_angle-=2
                    draw_screen()
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                player_angle+=90
                draw_screen()


    

    clock.tick(60)  

pygame.quit()