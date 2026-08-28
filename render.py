#import math
# import pygame
from PIL import Image
#move rendering functions into here 
          

#for map tilings
class wall_image():
    def __init__(self,image_name):
        self.main_image = Image.open("Assets/"+image_name)
        self.width = (self.main_image.size)[0]
        self.height = (self.main_image.size)[1]
        self.img_slices = []
        for i in range(self.width):
            self.img_slices.append(self.main_image.crop((i,0,i+1,16)))

brick = wall_image("Brick.png")



class tile():
    def __init__(self,tileType,wall_image=None,spriteInfo=None):
        self.tileType=tileType #Wall,Path,Sprite,Enemy, Item
        self.wallImage = wall_image
        self.spriteInfo = spriteInfo