'''
@author: qian
para: for adjust parameters only.
others: does not matter
'''

import draw
import pygame
from pygame.locals import *

# def main(data,config):
#     pygame.init()
#     screen=pygame.display.set_mode((glo.width,glo.height))
#     myfont=pygame.font.SysFont("monospace",20)
#     clock=pygame.time.Clock()
#     while not data['kill']:
#         screen.fill((0,0,0))
#         depMsg='Depth = %.4f'%(data['depth'])
#         draw.text(screen,depMsg,myfont,10,80)
#         draw.text(screen,data['msg'],myfont,glo.width>>1,80)
#         draw.text(screen,'Touch thold %.2f'%(data['touchRange']),myfont,glo.width-200,80)
#         if data['touch'] and data['pointing']:
#             draw.text(screen,'Touching',myfont,glo.width-200,120)
#             draw.circles(screen,(glo.x,glo.y))
#         else:
#             draw.text(screen,'Not touching',myfont,glo.width-200,120)
#         pygame.display.update()
#         msElapsed=clock.tick(30)
#            

def para(data,kill):
    '''
    This function create a pygame window that dynamically adjust some parameters for KSI
    Input: arguments are variables in Manager
    data is a dict:
        to be filled
    kill is a list, kill[0] is bool, meaning this process should stop or not.
    '''
    pygame.init()
    screen=pygame.display.set_mode((500,700))
    myfont=pygame.font.SysFont("monospace",20)
    clock=pygame.time.Clock()
    # parameter : minimal value, range
    gainRange=[0,1]
    threshRangeL=[20,40] # to 80
    threshRangeH=[200,55] # to 80
    gauseRange = [1,10] # to 11
    ydisRange=[10,50]
    alphaRange=[0,0.2]
    ythRange=[100,50] # to 80
    stepRange=[0,6] # to 6
    touchRange = [0,1.5]
    while not kill['kill']:
        screen.fill((0,0,0))
        # gain
        gain0='Gain 0 = %.4f'%(data['gain'][0])
        draw.text(screen,gain0,myfont,10,80)
        draw.rec(screen,100,(data['gain'][0]-gainRange[0])/gainRange[1]*200)
        gain1='Gain 1 = %.4f'%(data['gain'][1])
        draw.text(screen,gain1,myfont,10,130)
        draw.rec(screen,150,(data['gain'][1]-gainRange[0])/gainRange[1]*200)
        # sbs
        if data['step']==1:
            thresh0='SbsThresh L 0 = %.4f'%(data['sbsThreshL'][0])
            draw.text(screen,thresh0,myfont,10,180)
            draw.rec(screen,200,200*(data['sbsThreshL'][0]-threshRangeL[0])/threshRangeL[1])
            thresh1='SbsThresh L 1 = %.4f'%(data['sbsThreshL'][1])
            draw.text(screen,thresh1,myfont,10,230)
            draw.rec(screen,250,200*(data['sbsThreshL'][1]-threshRangeL[0])/threshRangeL[1])
        else:
            thresh0='SbsThresh H 0 = %.4f'%(data['sbsThreshH'][0])
            draw.text(screen,thresh0,myfont,10,180)
            draw.rec(screen,200,200*(data['sbsThreshH'][0]-threshRangeH[0])/threshRangeH[1])
            thresh1='SbsThresh H 1 = %.4f'%(data['sbsThreshH'][1])
            draw.text(screen,thresh1,myfont,10,230)
            draw.rec(screen,250,200*(data['sbsThreshH'][1]-threshRangeH[0])/threshRangeH[1])
        gause0='SbsGause 0 = %.4f'%(data['sbsGause'][0])
        draw.text(screen,gause0,myfont,10,280)
        draw.rec(screen,300,200*(data['sbsGause'][0]-gauseRange[0])/gauseRange[1])
        gause1='SbsGause 1 = %.4f'%(data['sbsGause'][1])
        draw.text(screen,gause1,myfont,10,330)
        draw.rec(screen,350,200*(data['sbsGause'][1]-gauseRange[0])/gauseRange[1])
        # special case
        gain0='Dis 23-0 = %.4f'%(data['ydis'][0])
        draw.text(screen,gain0,myfont,10,380)
        draw.rec(screen,400,(data['ydis'][0]-ydisRange[0])/ydisRange[1]*200)
        
        thresh0='yThresh 0 = %.4f'%(data['yth'][0])
        draw.text(screen,thresh0,myfont,10,430)
        draw.rec(screen,450,200*(data['yth'][0]-ythRange[0])/ythRange[1])

        touch='Touch Range %.4f'%(data['touch'])
        draw.text(screen,touch,myfont,10,480)
        draw.rec(screen,500,100.0*(data['touch']-touchRange[0])/touchRange[1])
        
        step='Step %.4f'%(data['step'])
        draw.text(screen,step,myfont,10,530)
        draw.rec(screen,550,200*(data['step']-stepRange[0])/stepRange[1])

        alpha='alpha = %.4f'%(data['alpha'])
        draw.text(screen,alpha,myfont,10,630)
        draw.rec(screen,650,(data['alpha']-alphaRange[0])/alphaRange[1]*200)
                
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type ==  MOUSEBUTTONDOWN:
                pressed_array = pygame.mouse.get_pressed()
                for index in range(len(pressed_array)):
                    if pressed_array[index]:
                        if index == 0:
                            pos = pygame.mouse.get_pos()
                            if pos[1]>100 and pos[1]<120:
                                data['gain']= [gainRange[0]+gainRange[1]*(pos[0]-10)/200.0, data['gain'][1]]
                                data['gainChange']=True
                            elif pos[1]>150 and pos[1]<170:
                                data['gain']= [data['gain'][0], gainRange[0]+gainRange[1]*(pos[0]-10)/200.0]
                                data['gainChange']=True
                            elif pos[1]>200 and pos[1]<220:
                                if data['step']==1:
                                    data['sbsThreshL']= [threshRangeL[0]+threshRangeL[1]*(pos[0]-10)/200.0, data['sbsThreshL'][1]]
                                else:
                                    data['sbsThreshH']= [threshRangeH[0]+threshRangeH[1]*(pos[0]-10)/200.0, data['sbsThreshH'][1]]
                            elif pos[1]>250 and pos[1]<270:
                                if data['step']==1:
                                    data['sbsThreshL']= [data['sbsThreshL'][1], threshRangeL[0]+threshRangeL[1]*(pos[0]-10)/200.0]
                                else:
                                    data['sbsThreshH']= [data['sbsThreshH'][1], threshRangeH[0]+threshRangeH[1]*(pos[0]-10)/200.0]
                            elif pos[1]>300 and pos[1]<320:
                                data['sbsGause']= [(gauseRange[0]+gauseRange[1]*(pos[0]-10)/200)/2*2+1, data['sbsGause'][1]]
                                data['threshChange']=True
                            elif pos[1]>350 and pos[1]<370:
                                data['sbsGause']= [data['sbsGause'][0], (gauseRange[0]+gauseRange[1]*(pos[0]-10)/200)/2*2+1]
                                data['threshChange']=True
                            elif pos[1]>400 and pos[1]<420:
                                data['ydis']= [ydisRange[0]+ydisRange[1]*(pos[0]-10)/200.0, data['ydis'][1]]
                            elif pos[1]>450 and pos[1]<470:
                                data['yth']= [ythRange[0]+ythRange[1]*(pos[0]-10)/200.0, data['yth'][1]]
                            elif pos[1]>500 and pos[1]<520:
                                data['touch']= touchRange[0]+touchRange[1]*(pos[0]-10)/200.0
                            elif pos[1]>550 and pos[1]<570:
                                data['step']= stepRange[0]+stepRange[1]*(pos[0]-10)/200+1
                            elif pos[1]>600 and pos[1]<620:
                                pass
                            elif pos[1]>650 and pos[1]<670:
                                data['alpha']= alphaRange[0]+alphaRange[1]*(pos[0]-10)/200.0
        pygame.display.update()
        msElapsed=clock.tick(30)
