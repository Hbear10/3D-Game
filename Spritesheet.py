import pygame

#returns on frame of a spritesheet
def spritesheet(img_name,width,height,index=0):
    sprite_frame = pygame.Surface((width,height),pygame.SRCALPHA) #SRCALPHA makes transparent :D
    sheet = pygame.image.load(f"Assets/{img_name}.png").convert_alpha()
    sprite_frame.blit(sheet,(index*width*-1,0))
    return sprite_frame


#generate frames of an animation
class animation():
    def __init__(self,img_name,width,height,number_of_frames,scale=1):
        self.frames = []
        for i in range(number_of_frames):
            frame = spritesheet(img_name=img_name,width=width,height=height,index=i)
            frame = pygame.transform.scale_by(frame,scale)
            self.frames.append(frame)

        
#testing
if __name__ == "__main__":
    print("Hello World!")

    pygame.init()
    screen = pygame.display.set_mode((1280,720))
    running = True
    count = 0

    clock = pygame.time.Clock()

    frames = animation("RoboArm-Sheet",32,32,10,16)
                                     
    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("purple")
        
        frame = frames.frames[count//6]
        screen.blit(frame,(0,0))
        pygame.display.flip()

        count+=1
        if count == 60:
            count = 0

        clock.tick(60)

    pygame.quit()