import math

FOV = 100

class plane():
    def __init__(self,x1,x2):
        self.x1 = x1 # left coords
        if self.x1[1] < 0:
            self.x1[1] = abs(x1[0]*math.tan( math.radians(90-(FOV/2)) ))
            #print(math.tan(90-(FOV/2)))
            # print(self.x1[1])
        
        self.x2 = x2 # right coords
        if self.x2[1] < 0:
            self.x2[1] = 0.1
        #print(x1,x2)

        #if x1[1]==0:
            #self.d1 = math.sqrt(((x1[0])**2+(x1[1])**2)) # distance to left pos
        #else:
        
        self.d1 = math.sqrt(((x1[0])**2+(x1[1])**2)) # distance to left pos
        self.d2 = math.sqrt(((x2[0])**2+(x2[1])**2)) # distance to right pos


        if x1[1]<0:
            self.p1 = math.degrees( math.atan(x1[0]/(x1[1])))*(1280/(FOV))+640
        else:
            self.p1 = math.degrees(math.atan(x1[0]/(x1[1])))*(1280/(FOV))+640

        if x2[1]<=0:
            self.p2 = math.degrees( math.atan(x2[0]/(x2[1])) +1000)*(1280/(FOV))+640
        else:
            self.p2 = math.degrees(math.atan(x2[0]/(x2[1])))*(1280/(FOV))+640


            