import pygame


def circles(screen,coords):
    pygame.draw.circle(screen, (255,0,0), (int(coords[0]),int(coords[1])),10)
#     pygame.draw.circle(screen, (0,255,0), (int(coords[1][0][0])/3,int(coords[1][0][1])/3),10)

def text(screen,mess,myfont,x,y):
    mouseLabel=myfont.render(mess ,1,(255,255,255))
    screen.blit(mouseLabel,(x,y))
    
def rec(screen,y,v):
    pygame.draw.rect(screen, (255,0,0), (10,y,200,20), 2)    
    pygame.draw.rect(screen, (255,0,0), (10,y,v,20), 0)        