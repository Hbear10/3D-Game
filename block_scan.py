#This file contains code to detect if there is a wall between 2 points
#I am developing this to calculate which parts of a sprite is visible, however there may be more uses of this later on I am not sure yet
#I called the file block scan as I am scanning to see if the line of sight is blocked


from math import sqrt, sin, cos, asin

#Function that takes the map (note that the grid will probably be (y,x) not (x,y) due to 2D arrays, so when checking the grid you need to switch the coordinate values), 
# and two points (x,y), tests to see if there is a wall in between them, defult value that is a wall is set to 1
#Use a basic ray/raycast to calculate if there is a wall.
#Use fixed step raycasting as it is easier to implement and has less complexity than DDA
def scan(grid:list, pos1:tuple, pos2:tuple, wall_val:int =1) -> bool:
    try:
        x_direction = (pos2[0]-pos1[0])/abs(pos2[0]-pos1[0]) #Calculate the unit direction in x
    except ZeroDivisionError:
        x_direction = 0
    try:
        y_direction = (pos2[1]-pos1[1])/abs(pos2[1]-pos1[1]) #Calculate the unit direction in y
    except ZeroDivisionError:
        y_direction = 0


    point_distance = sqrt((pos2[0]-pos1[0])**2 + (pos2[1]-pos1[1])**2) #Distance between points
    travel_distance = 0.0                                              #Distance ray has travelled
    angle = asin((pos2[0]-pos1[0]) / point_distance)                   #Angle in radians from the y axis

    scan_ray_pos = [pos1[0],pos1[1]] #Postion of the ray that to test if it is a wall, stop list linking

    while travel_distance < point_distance: 
        if grid[int(scan_ray_pos[1])][int(scan_ray_pos[0])] == wall_val:
            return False #There is a wall blocking the line of sight, breaks out of function
        
        travel_distance += 0.5                        #How far the ray has travelled so far

        scan_ray_pos[0] += sin(angle)*0.5*x_direction #How far the ray move 
        scan_ray_pos[1] += cos(angle)*0.5*y_direction

    return True  #Clear line of sight



if __name__ == "__main__":
    print("Hello World")
    map = [[1,1,1,1,1],
           [1,0,0,0,1],
           [1,0,1,0,1],
           [1,0,0,0,1],
           [1,1,1,1,1]]
    
    print(scan(map, (1.5,3.5), (3.5,1.5)))
    print(scan(map, (3.5,3.5), (1.5,1.5)))
