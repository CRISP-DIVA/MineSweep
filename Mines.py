# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 10:09:41 2021

@author: mique
"""
import pygame
from pygame.locals import *
import numpy as np
import os

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,100)
SIZE_X = 24
SIZE_Y = 24
BLOCK_SIDE = 50
diff = 0.5
mine_limit = int((SIZE_X*SIZE_Y)*diff)

BORDER_SIZE = int(BLOCK_SIDE *0.05)
RESOLUTION_Y = int((SIZE_Y+1)*BLOCK_SIDE+(3+(SIZE_Y))*BORDER_SIZE)
RESOLUTION_X = int(SIZE_X*BLOCK_SIDE+(4+(SIZE_X-1))*BORDER_SIZE)
print(BORDER_SIZE)
print(RESOLUTION_X,RESOLUTION_Y)

TOPBAR_SIZE = BLOCK_SIDE

POINTS_SIZE = 0.2 * RESOLUTION_X
BACKGROUND_COLOR = (255,255,255)
UI_COLOR = (220,185,255)
POINTS_COLOR = (150,185,255)


NORMAL_STATE = 0
NORMAL_COLOR = (100,100,100)
CLICKED_STATE = 1
CLICKED_COLOR = (200,200,200)
MINE_STATE = 2
MINE_COLOR = (255,10,10)
FLAGGED_STATE = 3
FLAGGED_COLOR = (30,240,21)


class Mine():
    def __init__(self,x,realX,y,realY,ismine):
        self.state = NORMAL_STATE
        self.number = 0
        self.ismine = ismine
        self.x = x
        self.realX = realX
        self.y = y
        self.realY = realY
        self.done = False
    def drawMine(self,screen,left,top,myfont):
        curr_color = NORMAL_COLOR
        if self.state == CLICKED_STATE:
            curr_color = CLICKED_COLOR
        elif self.state == MINE_STATE:
            curr_color = MINE_COLOR
        elif self.state == FLAGGED_STATE:
            curr_color = FLAGGED_COLOR
        pygame.draw.rect(screen,curr_color,pygame.Rect(left,top,BLOCK_SIDE,BLOCK_SIDE))  
        
        if self.state == CLICKED_STATE and self.number != 0:
            textsurface = myfont.render(str(self.number), False, (0, 0, 0))
            
            screen.blit(textsurface,(BORDER_SIZE*2+self.realX,BORDER_SIZE*2+self.realY))
        
    def update(self,clicked,r_clicked):
        mouse = pygame.mouse.get_pos()
        points = 0
        if mouse[0] >= self.realX and mouse[0] <= self.realX+BLOCK_SIDE and mouse[1]>= self.realY and mouse[1] <= self.realY+BLOCK_SIDE:
            if clicked:
                self.state = CLICKED_STATE
                if self.ismine:
                    self.state = MINE_STATE
                    points = -1
                else:
                    if not self.done:
                        points = 10
                    self.done = True
                    
            elif r_clicked and self.state != MINE_STATE:
                if self.state == FLAGGED_STATE:
                    self.state = NORMAL_STATE
                else:
                    self.state = FLAGGED_STATE
        return points


class MineBoard():
    
    def __init__(self):
        pygame.init()
        pygame.font.init() # you have to call this at the start, 
        self.n_mines = 0
        self.myfont = pygame.font.Font("SimplySquare.ttf",BLOCK_SIDE-int(BLOCK_SIDE*0.2))
        self.screen = pygame.display.set_mode([RESOLUTION_X,RESOLUTION_Y])        
        self.running = False
        self.points = 0
        self.board = []
        self.lost = False
        self.win = False
        lastmine = 0
        for i in range(SIZE_Y):
            row = []
            for j in range(SIZE_X):        
                mine = np.random.randint(0,5)
                if self.n_mines < mine_limit and mine==1 and lastmine==0:
                    ismine = True
                    self.n_mines +=1
                    lastmine=3
                else:
                    lastmine -=1
                    if lastmine <0:
                        lastmine = 0
                    ismine = False
                row.append(Mine(j,BORDER_SIZE*2+(BLOCK_SIDE+BORDER_SIZE)*j,i,TOPBAR_SIZE+BORDER_SIZE*2+(BLOCK_SIDE+BORDER_SIZE)*i,ismine))
            self.board.append(row)
        self.board = np.array(self.board)
        self.calcMines()
        
    
    def clearMines(self,mine):
        n = 0
                
        
        top = mine.y-1
        bot = mine.y+2
        
        left = mine.x-1
        right = mine.x+2
        
        for y in range(top,bot):
            for x in range(left,right):
                if y < SIZE_Y and x < SIZE_X and y>0 and x>0:
                    if self.board[y,x].state == NORMAL_STATE and not self.board[y,x].ismine:
                        self.board[y,x].state = CLICKED_STATE
                        if self.board[y,x].number == 0:
                            self.clearMines(self.board[y,x])
                        self.points+=5
                    
                  
    def checkwin(self):
        win = True
        for i in range(SIZE_Y):
            for j in range(SIZE_X):
                if self.board[i,j].state != CLICKED_STATE and self.board[i,j].state != FLAGGED_STATE:
                    if not (self.board[i,j].state == NORMAL_STATE and self.board[i,j].ismine): 
                        win = False
        return win
    
    def calcMines(self):
        for i in range(SIZE_Y):
            for j in range(SIZE_X):
                mine = self.board[i,j]
                n = 0
                
                
                top = mine.y-1
                bot = mine.y+2
            
                left = mine.x-1
                right = mine.x+2
                
                
                for y in range(top,bot):
                    for x in range(left,right):
                        if y < SIZE_Y and x < SIZE_X and y>=0 and x>=0:
                            if self.board[y,x].ismine:
                                n += 1
                self.board[i,j].number = n
                
                           
    def drawBoard(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        if not self.lost and not self.win:
            pygame.draw.rect(self.screen,UI_COLOR,pygame.Rect(BORDER_SIZE,BORDER_SIZE,RESOLUTION_X-BORDER_SIZE*2,TOPBAR_SIZE-BORDER_SIZE))
            
            pygame.draw.rect(self.screen,UI_COLOR,pygame.Rect(BORDER_SIZE,TOPBAR_SIZE+BORDER_SIZE,RESOLUTION_X-BORDER_SIZE*2,RESOLUTION_Y-(TOPBAR_SIZE+BORDER_SIZE*2)))
            
            pygame.draw.rect(self.screen,POINTS_COLOR,pygame.Rect(BORDER_SIZE*2,BORDER_SIZE*2,POINTS_SIZE,TOPBAR_SIZE-BORDER_SIZE*3))
            
            textsurface = self.myfont.render(str(self.points).zfill(4), False, (0, 0, 0))
            
            self.screen.blit(textsurface,(BORDER_SIZE*2*2,BORDER_SIZE*2*2))
            
            for i in range(SIZE_Y):
                for j in range(SIZE_X): 
                    self.board[i,j].drawMine(self.screen,BORDER_SIZE*2+(BLOCK_SIDE+BORDER_SIZE)*j,TOPBAR_SIZE+BORDER_SIZE*2+(BLOCK_SIDE+BORDER_SIZE)*i,self.myfont)
        
        elif self.lost:
            textsurface = self.myfont.render("YOU LOOOOOOOST", False, (0, 0, 0))
            
            self.screen.blit(textsurface,(RESOLUTION_X//2,RESOLUTION_Y//2))
        else:
            textsurface = self.myfont.render("YOU WIIIIIIIN", False, (0, 0, 0))
            
            self.screen.blit(textsurface,(RESOLUTION_X//2,RESOLUTION_Y//2))
        
        pygame.display.flip()

    def updateBoard(self):
        clicked = False
        r_clicked = False
        restart = False
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.running=False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = True
                if event.button == 3:
                    r_clicked = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart = True
        for i in range(SIZE_Y):
            for j in range(SIZE_X):
                aux = self.board[i,j].update(clicked,r_clicked)
                
                if aux>0 and self.board[i,j].number == 0:
                    self.clearMines(self.board[i,j])
                elif aux == -1:
                    
                    self.lost= True
                
                self.points += aux
        self.win = self.checkwin()
        return restart
    def startGame(self):
        self.running = True


board = MineBoard()

board.startGame()
restart = False
while board.running:
    if restart:
        board = MineBoard()
        board.startGame()
        
    board.drawBoard()
    restart = board.updateBoard()
    
 
pygame.quit()