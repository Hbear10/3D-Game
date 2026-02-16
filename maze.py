from random import randint, choice


def free_spaces(map: list, coord:list) -> list:
    #print(coord)
    spaces = []
    if coord[1]!=0:#up #if not at top y to avoid list index out of range
        if map[coord[1]-2][coord[0]]==1:
            spaces.append([coord[0],coord[1]-2])
    if coord[1]!=len(map)-1:#down
        if map[coord[1]+2][coord[0]]==1:
            spaces.append([coord[0],coord[1]+2])
    if coord[0]!=0:#left
        if map[coord[1]][coord[0]-2]==1:
            spaces.append([coord[0]-2,coord[1]])
    if coord[0]!=len(map)-1:#right
        if map[coord[1]][coord[0]+2]==1:
            spaces.append([coord[0]+2,coord[1]])

    return spaces


def back_space(map: list, coord:list) -> list:
    space = []
    #print(map)
    if coord[1]!=0:#up #if not at top y to avoid list index out of range
        if map[coord[1]-2][coord[0]]==100 and map[coord[1]-1][coord[0]]==0:
            space = ([coord[0],coord[1]-2])
    if coord[1]!=len(map)-1:#down
        if map[coord[1]+2][coord[0]]==100 and map[coord[1]+1][coord[0]]== 0:
            space = ([coord[0],coord[1]+2])
    if coord[0]!=0:#left
        if map[coord[1]][coord[0]-2]==100 and map[coord[1]][coord[0]-1]==0:
            space = ([coord[0]-2,coord[1]])
    if coord[0]!=len(map)-1:#right
        if map[coord[1]][coord[0]+2]==100 and map[coord[1]][coord[0]+1]==0:
            space = ([coord[0]+2,coord[1]])

    if space == []:
        space = coord

    return space


def still_need_to_backtrack(map):
    back_still_there = False
    length = len(map)
    count = 0
    while not back_still_there and count<length:
        if 100 in map[count]:
            #print("HI")
            back_still_there = True
        count+=1

    return back_still_there


def format_maze(map: list, size: int) -> list:
    output_map = []
    output_map.append([1 for _ in range(size+2)])
    for i in map:
        output_map.append([1]+i+[1])
    output_map.append([1 for _ in range(size+2)])
    
    return output_map


def maze_generate(size: int) -> list:
    
    x_start,y_start = randint(0,size//2)*2,randint(0,size//2)*2

    maze = [[1 for _ in range(size)] for _ in range(size)]

    #print(maze[y_start])
    maze[y_start][x_start] = 100
    tracker_point = [x_start,y_start]
    points =  free_spaces(maze,tracker_point)
    #print(still_need_to_backtrack(maze))
    while still_need_to_backtrack(maze):
        if len(points)!= 0:
            
            move_to = choice(points)
            maze[move_to[1]][move_to[0]] = 100#go back to this one
            maze[(move_to[1]+tracker_point[1])//2][(move_to[0]+tracker_point[0])//2] = 0 #mid point
            tracker_point = move_to[0],move_to[1]
            points =  free_spaces(maze,tracker_point)
        else:
            #print(tracker_point)
            
            point = back_space(maze, tracker_point)
            #print(point)
            #
            maze[tracker_point[1]][tracker_point[0]] = 0
            tracker_point = point[0],point[1]

            points =  free_spaces(maze,tracker_point)


    return [format_maze(maze, size),[x_start+1.5,y_start+1.5]]



def main():
    m = maze_generate(15)
    for i in m[0]:
        print(i)

if __name__ == '__main__':
    main()