import pygame
from PIL import Image
import math
#import time

import maze
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
       [1,0,0,0,1],
       [1,0,0,0,1],
       [1,0,0,0,1],
       [1,0,0,0,1],
       [1,0,"W",0,1],#W on this line is just an indicator for me for where the player starts, it doesn't affect any processing
       [1,1,1,1,1]]

player_pos = [2.5,10.5]#The coordinate of the player

FOV = 100 #The field of view of the player

def new_maze():
    global map, player_pos

    map,player_pos = maze.maze_generate(11)


raycast_column_width = 2 #The width of each pixel column, increase to improve performance as it reduces the amount of rays sent


pygame.init()
screen = pygame.display.set_mode((1280,720)) #720p

clock = pygame.time.Clock()#Used later to set FPS cap

player_angle=0 # Direction the player is facing

class image():
    def __init__(self,image_name):
        self.main_image = Image.open("Assets/"+image_name)
        self.width = (self.main_image.size)[0]
        self.height = (self.main_image.size)[1]
        self.img_slices = []
        for i in range(self.width):
            self.img_slices.append(self.main_image.crop((i,0,i+1,16)))
    

sprites = []

sprite_img = pygame.image.load("assets/Door.png").convert_alpha()

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
            if (ray_pos_grid[0],ray_pos_grid[1]) not in sprites:
                sprites.append( (ray_pos_grid[0],ray_pos_grid[1]) ) 

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
                        print(ray_pos[0],int(ray_pos[0]))
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
    global sprites

    sprites = []

    #t= time.perf_counter()
    
    ray_store=[]
    for i in range(1280//raycast_column_width):#cast all the rays
        ray_store.append(raycast_ray(i))
    for i in range(1280//raycast_column_width):#draw all the rays
        draw_beam(i*raycast_column_width,ray_store[i][0],ray_store[i][1])

    #print(time.perf_counter()-t)



def draw_sprites():
    print(len(sprites))
    for sprite in sprites:
        sprite_distance = (math.sqrt( (player_pos[0]-(sprite[0]+0.5))**2 + (player_pos[1]-(sprite[1]+0.5))**2 ))   
        
        #print(math.cos(math.radians(player_angle)-math.cos( (player_pos[0]-(sprite[0]+0.5)) )))
        #sprite_distance =  sprite_distance * math.cos( math.radians(player_angle)-math.atan2( (player_pos[1]-(sprites[0][1]+0.5)) , (player_pos[0]-(sprites[0][0]+0.5)) ))

        sprite_bearing = math.radians(90) - math.atan2( (player_pos[1]-(sprite[1]+0.5)) , (player_pos[0]-(sprite[0]+0.5)) )
        #print((math.degrees(sprite_bearing)+player_angle)%360 , math.degrees(sprite_bearing),player_angle)
        #print(f"{sprite_bearing=}, {player_pos[0]=}, {(sprite[0]+0.5)=}")
        #print(sprite_distance)
        if sprite_distance > 0.04 and (90> (math.degrees(sprite_bearing)+player_angle)%360 or (math.degrees(sprite_bearing)+player_angle)%360>270):
            screen.blit(pygame.transform.scale_by(sprite_img,20/sprite_distance), (640-(160/sprite_distance) - int(500*math.tan(sprite_bearing+math.radians(player_angle))),(360-(160/sprite_distance))))
    


def draw_screen():
    screen.fill("dark grey")
    pygame.draw.rect(screen,(34,34,34), pygame.Rect(0,0,1280,360))
    raycast()
    #print(sprites)
    draw_sprites()
    pygame.display.flip()


def main():
    global player_angle, brick
    player_angle = 0

    brick = image("Brick.png")
    #print(brick.img_slices[5].show())


    #ray_slice = brick.img_slices[5].transform((raycast_column_width,300),Image.Transform.EXTENT,[0,0,1,16])#.show()
    #pygame_surface = pygame.image.fromstring(ray_slice.tobytes(),ray_slice.size,ray_slice.mode).convert()

    draw_screen()

    turning = 0
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


        # if turning != 0:
        #     player_angle+=turning
        #     draw_screen()
        #     if player_angle%90==0:
        #         turning=0

        clock.tick(30)  

    pygame.quit()


if __name__ == '__main__':
    main()