import pygame
import math
#import random

from render import *

print("Hello World!")

map = [[1,1,1,1,1],
       [1,1,0,0,1],
       [1,1,"W",1,1]]

raycast_column_width = 5
raycast_resolution = FOV / (1280 / raycast_column_width)
print(raycast_resolution)

pygame.init()
screen = pygame.display.set_mode((1280,720))

clock = pygame.time.Clock()
running = True

screen.fill("dark grey")
pygame.draw.rect(screen,(34,34,34), pygame.Rect(0,0,1280,360))

planes_to_draw = []
player_pos = [2.5,2.5]

# def create_planes():
#     global planes_to_draw

#     planes_to_draw = [] #[plane((-1,1),(-0.5,1)),plane((-0.5,1),(-0.5,2)),plane((-0.5,2),(0.5,2))]

#     start_pos = [[0,0]]#x,y
#     for i in map:
#         if "W" in i:
#             start_pos[0][0] = i.index("W")
#             start_pos[0][1] = map.index(i)
#             break

#     count = 0
#     while count != len(map):
#         if 0 in map[count]:
#             print(0)
#             X_occurrences = [j for j, y in enumerate(map[count]) if y == 0] #general syntax for this line from stack overflow
#             for x in X_occurrences:
#                 start_pos.append([x,count])
#         count+=1

#     print(start_pos)
#     #start_pos.append([start_pos[0][0],start_pos[0][1]-1])

#     for scan_spot in start_pos:
#         if map[scan_spot[1]-1][scan_spot[0]] == 1: #up
#             planes_to_draw.append(plane( [scan_spot[0]-player_pos[0],player_pos[1]-scan_spot[1]] , [scan_spot[0]-player_pos[0]+1,player_pos[1]-scan_spot[1]] ))
#         if map[scan_spot[1]][scan_spot[0]+1] == 1: #right
#             planes_to_draw.append(plane( [scan_spot[0]+1-player_pos[0],player_pos[1]-scan_spot[1]-1] , [scan_spot[0]+1-player_pos[0],player_pos[1]-scan_spot[1]] ))
#             #print(planes_to_draw[-1].x2)
#         if map[scan_spot[1]][scan_spot[0]-1] == 1: #left
#             planes_to_draw.append(plane( [scan_spot[0]-player_pos[0],player_pos[1]-scan_spot[1]-1] , [scan_spot[0]-player_pos[0],player_pos[1]-scan_spot[1]] ))
        
    

# def draw_plane(plane_obj, colour="cyan"):
    
#     pygame.draw.polygon(screen, colour, [(plane_obj.p1,360-(240/plane_obj.d1)),(plane_obj.p1,360+(240/plane_obj.d1)),
#                                          (plane_obj.p2,360+(240/plane_obj.d2)),(plane_obj.p2,360-(240/plane_obj.d2))])
#     #x coord/ distance width ways along the screen is calculated before in the object class
#     # take distance from player and then use that ratio to get height of bar


def draw_beam(x_point,distance):
    colour_index = 0.5/distance
    pygame.draw.rect(screen,color=(0, int(255*colour_index), int(255*colour_index) ),rect=pygame.Rect(x_point,360-(360/distance)/2,raycast_column_width,360/distance))

#create_planes()

def raycast():
    count = 0
    ray_pos=[2,2]
    while count < 1280//raycast_column_width:
        ray_pos[0],ray_pos[1] = player_pos #index-coord: 0-x, 1-y  ,note to self that the map is y,x not x,y
        ray_distance = 0
        is_blocked = False
        angle = math.radians(raycast_resolution*count-(FOV/2))
        print(angle)
        ray_index = 0.01 #how much we increase by
        #print(1)
        while not is_blocked:
            if map[int(ray_pos[1])][int(ray_pos[0])] == 1:
                is_blocked = True
                draw_beam(count*raycast_column_width,ray_distance)
                #print(2)
                #print(ray_pos)
            else:
                #print("AHAHAHAH")
                #print(count)
                ray_distance+=ray_index
                ray_pos[0] += math.sin(angle)*ray_index       #sin(theta)*n
                ray_pos[1] -= math.cos(angle)*ray_index       #cos(theta)*n, minus because as you go up it decreases index

                

        count+=1

raycast()


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    #screen.fill("light grey")

    #c = "cyan"
    colours_temp = ["cyan","red","green","pink","blue","brown","orange","purple","cyan","red","green","pink","blue","brown","orange","purple"]
    c_count=0


    #for i in planes_to_draw:
        #print(i)
        
        #draw_plane(i,colour=colours_temp[c_count])


        #c_count+=1
   

    pygame.display.flip()

    clock.tick(60)  

pygame.quit()