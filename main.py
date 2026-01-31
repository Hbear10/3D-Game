import pygame
import math
#import random

from render import *

print("Hello World!")

map = [[1,1,1,1,1],
       [1,1,0,1,1],
       [1,0,"W",1,1]]




        


#test_plane4 = plane((0.5,2),(1.5,2))
#test_plane5 = plane((2.5,2),(3.5,2))



pygame.init()
screen = pygame.display.set_mode((1280,720))

clock = pygame.time.Clock()
running = True

screen.fill("grey")

planes_to_draw = []
player_pos = (2.5,2.5)

def create_planes():
    global planes_to_draw

    planes_to_draw = [] #[plane((-1,1),(-0.5,1)),plane((-0.5,1),(-0.5,2)),plane((-0.5,2),(0.5,2))]

    start_pos = [[0,0]]#x,y
    for i in map:
        if "W" in i:
            start_pos[0][0] = i.index("W")
            start_pos[0][1] = map.index(i)
            break

    count = 0
    while count != len(map):
        if 0 in map[count]:
            print(0)
            X_occurrences = [j for j, y in enumerate(map[count]) if y == 0] #general syntax for this line from stack overflow
            for x in X_occurrences:
                start_pos.append([x,count])
        count+=1

    print(start_pos)
    #start_pos.append([start_pos[0][0],start_pos[0][1]-1])

    for scan_spot in start_pos:
        if map[scan_spot[1]-1][scan_spot[0]] == 1: #up
            planes_to_draw.append(plane( [scan_spot[0]-player_pos[0],player_pos[1]-scan_spot[1]] , [scan_spot[0]-player_pos[0]+1,player_pos[1]-scan_spot[1]] ))
        if map[scan_spot[1]][scan_spot[0]+1] == 1: #right
            planes_to_draw.append(plane( [scan_spot[0]+1-player_pos[0],player_pos[1]-scan_spot[1]-1] , [scan_spot[0]+1-player_pos[0],player_pos[1]-scan_spot[1]] ))
            #print(planes_to_draw[-1].x2)
        if map[scan_spot[1]][scan_spot[0]-1] == 1: #left
            planes_to_draw.append(plane( [scan_spot[0]-player_pos[0],player_pos[1]-scan_spot[1]-1] , [scan_spot[0]-player_pos[0],player_pos[1]-scan_spot[1]] ))
        
    
    #print(start_pos)

    # if map[start_pos[1]-1][start_pos[0]] == 1: #up
    #     planes_to_draw.append(plane( (start_pos[0]-player_pos[0],player_pos[1]-start_pos[1]) , (player_pos[0]-start_pos[0],player_pos[1]-start_pos[1]) ))
    # if map[start_pos[1]][start_pos[0]+1] == 1: #right
    #     planes_to_draw.append(plane( (player_pos[0]-start_pos[0],player_pos[1]-start_pos[1]-1) , (player_pos[0]-start_pos[0],player_pos[1]-start_pos[1]) ))
    #     #print(planes_to_draw[-1].x2)
    # if map[start_pos[1]][start_pos[0]-1] == 1: #left
    #     planes_to_draw.append(plane( [start_pos[0]-player_pos[0],player_pos[1]-start_pos[1]-1] , [start_pos[0]-player_pos[0],player_pos[1]-start_pos[1]] ))



def draw_plane(plane_obj, colour="cyan"):
    
    pygame.draw.polygon(screen, colour, [(plane_obj.p1,360-(240/plane_obj.d1)),(plane_obj.p1,360+(240/plane_obj.d1)),
                                         (plane_obj.p2,360+(240/plane_obj.d2)),(plane_obj.p2,360-(240/plane_obj.d2))])
    #x coord/ distance width ways along the screen is calculated before in the object class
    # take distance from player and then use that ratio to get height of bar


create_planes()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    screen.fill("light grey")

    #c = "cyan"
    colours_temp = ["cyan","red","green","pink","blue","brown","orange","purple","cyan","red","green","pink","blue","brown","orange","purple"]
    c_count=0

    pygame.draw.rect(screen,"dark grey", pygame.Rect(0,0,1280,360))

    for i in planes_to_draw:
        #print(i)
        
        draw_plane(i,colour=colours_temp[c_count])
        # if c == "cyan":
        #     #print(i.x1,i.x2)

        #     #thx stack overflow, delete later
        #     #r = lambda: random.randint(0,255)
        #     #c=('#%02X%02X%02X' % (r(),r(),r()))

        #     #c = random.choice(pygame.Color)
        #     c="red"
        # else:
        #     c = "green"

        c_count+=1

    # draw_plane(test_plane)
    # draw_plane(test_plane2,"red")
    # draw_plane(test_plane3)
    # draw_plane(test_plane4)
    # draw_plane(test_plane5)


    # plane_x1 = math.degrees(math.atan(test_plane.x1[0]/test_plane.x1[1]**2))*128//9+640
    

    # #print(math.degrees(plane_x1))

    # #plane_y1 = 1
    # distance1 = math.sqrt(test_plane.x1[0]**2+test_plane.x1[1]**2)
    # plane_x2 = 426
    # plane_x2 = math.degrees(math.atan(test_plane.x2[0]/test_plane.x2[1]**2))*128//9+640
    # #plane_y2 = 2
    # distance2 = math.sqrt(test_plane.x2[0]**2+test_plane.x2[1]**2)
    
    # pygame.draw.polygon(screen, "cyan", [(plane_x1,360-(240/distance1)),(plane_x1,360+(240/distance1)),
    #                                      (plane_x2,360+(240/distance2)),(plane_x2,360-(240/distance2))])

   

    pygame.display.flip()

    clock.tick(60)  

pygame.quit()