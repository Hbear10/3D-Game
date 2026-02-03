import pygame
import math
import time
#import random

from render import *

print("Hello World!")

map = [[1,1,1,1,1],
       [1,1,0,0,1],
       [1,1,"W",1,1],
       [1,1,1,1,1]]

raycast_column_width = 4
raycast_resolution = FOV / (1280 / raycast_column_width)
print(raycast_resolution)

pygame.init()
screen = pygame.display.set_mode((1280,720))

clock = pygame.time.Clock()
running = True


planes_to_draw = []
player_pos = [2.5,2.5]
player_angle = 0 #in degrees, gets turned into radians later

def draw_beam(x_point,distance):
    colour_index = 0.5/distance
    pygame.draw.rect(screen,color=(0, int(255*colour_index), int(255*colour_index) ),rect=pygame.Rect(x_point,360-(360/distance)/2,raycast_column_width,360/distance))


def raycast():
    t= time.time()
    count = 0
    ray_pos=[2,2]
    while count < 1280//raycast_column_width:
        ray_pos[0],ray_pos[1] = player_pos #index-coord: 0-x, 1-y  ,note to self that the map is y,x not x,y
        ray_distance = 0
        is_blocked = False
        angle = math.radians(raycast_resolution*count-(FOV/2)+player_angle)
        #print(angle)
        ray_index = 0.001 #how much we increase by
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
    print(time.time()-t)

def draw_screen():
    screen.fill("dark grey")
    pygame.draw.rect(screen,(34,34,34), pygame.Rect(0,0,1280,360))
    raycast()


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
                player_angle-=90
                draw_screen()
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                player_angle+=90
                draw_screen()


    pygame.display.flip()

    clock.tick(60)  

pygame.quit()