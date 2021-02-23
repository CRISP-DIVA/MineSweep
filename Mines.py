# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 10:09:41 2021

@author: mique
"""
import pygame
from pygame.locals import *
import numpy as np
import os
import pyautogui
import time
import win32gui
import win32com.client
import win32api

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,100)
SIZE_X = 8
SIZE_Y = 8
BLOCK_SIDE = 50
diff = 0.1
mine_number = int((SIZE_X*SIZE_Y)*diff)

BORDER_SIZE = int(BLOCK_SIDE *0.05)
RESOLUTION_Y = int((SIZE_Y+1)*BLOCK_SIDE+(3+(SIZE_Y))*BORDER_SIZE)
RESOLUTION_X = int(SIZE_X*BLOCK_SIDE+(4+(SIZE_X-1))*BORDER_SIZE)
print(BORDER_SIZE)
print(RESOLUTION_X,RESOLUTION_Y)

TOPBAR_SIZE = BLOCK_SIDE

POINTS_SIZE = 0.2 * RESOLUTION_X
BACKGROUND_COLOR = (0,0,0)
UI_COLOR = (0,0,0)
NUMBER_COLOR = (255,255,255)
POINTS_COLOR = (0,0,0)


NORMAL_STATE = 0
NORMAL_COLOR = (255,255,255)
CLICKED_STATE = 1
CLICKED_COLOR = (0,0,255)
MINE_STATE = 2
MINE_COLOR = (255,0,0)
FLAGGED_STATE = 3
FLAGGED_COLOR = (255,255,0)
MINE_PENALTY = 100
DISCOVERED_PENALTY = 5
OUTSIDE_PENALTY = 10
PROGRESS_REWARD = 2
WIN_REWARD = 100



class MineBoardEnv():
    
    def __init__(self):
        pygame.init()
        pygame.font.init() # you have to call this at the start, 
        
        self.board_states = np.full((SIZE_X,SIZE_Y),NORMAL_STATE)
        self.board_numbers = np.full((SIZE_X,SIZE_Y),-2)
        board_mines_x = np.random.randint(0,SIZE_X,size=mine_number)
        board_mines_y = np.random.randint(0,SIZE_Y,size=mine_number)
        
        for x,y in zip(board_mines_x,board_mines_y):
            self.board_numbers[x,y] = -1
        
        self.show_end = False
        self.myfont = pygame.font.Font("SimplySquare.ttf",BLOCK_SIDE-int(BLOCK_SIDE*0.2))
        self.screen = pygame.display.set_mode([RESOLUTION_X,RESOLUTION_Y])        
        self.running = False
        self.points = 0
        self.lost = False
        self.win = False
        self.calcMines()
        self.cursor_x = 0
        self.cursor_y = 0
        self.last_action = ""
        
    
    def clickMine(self,curr_x,curr_y):
        
        
        reward = 0
        
        if self.board_states[curr_x,curr_y] == NORMAL_STATE:
            
            self.board_states[curr_x,curr_y] = CLICKED_STATE
            reward += PROGRESS_REWARD
            if self.board_numbers[curr_x,curr_y] == -1:
                reward -= MINE_PENALTY
                self.lost = True
            elif self.board_numbers[curr_x,curr_y] == 0:
        
                top = curr_y-1
                bot = curr_y+2
                
                left = curr_x-1
                right = curr_x+2
                
                
                for x in range(left,right):
                    for y in range(top,bot):
                        if y < SIZE_Y and x < SIZE_X and y>0 and x>0:

                            if self.board_states[x,y] == NORMAL_STATE: 
                                if not self.board_numbers[x,y] == -1:
                                
                                    self.clickMine(x,y)
                                    
                                    self.points+=5                    
                                    reward += PROGRESS_REWARD
        else:
            reward -=DISCOVERED_PENALTY
                        
                    
                    
        return reward
    def checkwin(self):
        win = True
        for i in range(SIZE_X):
            for j in range(SIZE_Y):
                if self.board_states[i,j] != CLICKED_STATE and self.board_states[i,j] != FLAGGED_STATE:
                    if not (self.board_states[i,j] == NORMAL_STATE and self.board_numbers[i,j] == -1): 
                        win = False
        return win
    
   
            
    def calcMines(self):
        for i in range(SIZE_X):
            for j in range(SIZE_Y):
                n = 0
                
                top = j-1
                bot = j+2
            
                left = i-1
                right = i+2
                
                if self.board_numbers[i,j] != -1:
                    for x in range(left,right):
                        for y in range(top,bot):
                            if y < SIZE_Y and x < SIZE_X and y>=0 and x>=0:
                                if self.board_numbers[x,y] == -1:
                                    n += 1
                    self.board_numbers[i,j] = n
    
    def restart(self):
        self.board_states = np.full((SIZE_X,SIZE_Y),NORMAL_STATE)
        self.board_numbers = np.full((SIZE_X,SIZE_Y),-2)
        board_mines_x = np.random.randint(0,SIZE_X,size=mine_number)
        board_mines_y = np.random.randint(0,SIZE_Y,size=mine_number)
        
        for x,y in zip(board_mines_x,board_mines_y):
            self.board_numbers[x,y] = -1
        
        self.show_end = False
        self.myfont = pygame.font.Font("SimplySquare.ttf",BLOCK_SIDE-int(BLOCK_SIDE*0.2))
        self.screen = pygame.display.set_mode([RESOLUTION_X,RESOLUTION_Y])        
        self.running = False
        self.points = 0
        self.lost = False
        self.win = False
        self.calcMines()
        self.cursor_x = 0
        self.cursor_y = 0
                           
    def render(self,delay):
        
        
        if not self.show_end:
            self.screen.fill(BACKGROUND_COLOR)
            pygame.draw.rect(self.screen,UI_COLOR,pygame.Rect(BORDER_SIZE,BORDER_SIZE,RESOLUTION_X-BORDER_SIZE*2,TOPBAR_SIZE-BORDER_SIZE))
            
            pygame.draw.rect(self.screen,UI_COLOR,pygame.Rect(BORDER_SIZE,TOPBAR_SIZE+BORDER_SIZE,RESOLUTION_X-BORDER_SIZE*2,RESOLUTION_Y-(TOPBAR_SIZE+BORDER_SIZE*2)))
            
            pygame.draw.rect(self.screen,POINTS_COLOR,pygame.Rect(BORDER_SIZE*2,BORDER_SIZE*2,POINTS_SIZE,TOPBAR_SIZE-BORDER_SIZE*3))
            
            textsurface = self.myfont.render(str(self.points).zfill(4), False, NUMBER_COLOR)
            
            self.screen.blit(textsurface,(BORDER_SIZE*2*2,BORDER_SIZE*2*2))
            
            textsurface = self.myfont.render(self.last_action, False, NUMBER_COLOR)
            
            self.screen.blit(textsurface,(BORDER_SIZE*2*2+BLOCK_SIDE*10,BORDER_SIZE*2*2))
            
            for i in range(SIZE_X):
                for j in range(SIZE_Y): 
                    left = BORDER_SIZE*2+(BLOCK_SIDE+BORDER_SIZE)*i
                    top = TOPBAR_SIZE+BORDER_SIZE*2+(BLOCK_SIDE+BORDER_SIZE)*j
                    curr_color = NORMAL_COLOR
                    if self.board_states[i,j] == CLICKED_STATE:
                        curr_color = CLICKED_COLOR
                    elif self.board_states[i,j] == MINE_STATE:
                        curr_color = MINE_COLOR
                    elif self.board_states[i,j] == FLAGGED_STATE:
                        curr_color = FLAGGED_COLOR
                    pygame.draw.rect(self.screen,curr_color,pygame.Rect(left,top,BLOCK_SIDE,BLOCK_SIDE))  
                    
                    if self.board_states[i,j] == CLICKED_STATE and self.board_numbers[i,j] != 0:
                        textsurface = self.myfont.render(str(self.board_numbers[i,j]), False, NUMBER_COLOR)
                        
                        self.screen.blit(textsurface,(BORDER_SIZE*2+(BORDER_SIZE*2+(BLOCK_SIDE+BORDER_SIZE)*i),BORDER_SIZE*2+(TOPBAR_SIZE+BORDER_SIZE*2+(BLOCK_SIDE+BORDER_SIZE)*j)))
                    
            pygame.draw.circle(self.screen,(255,0,0), (BORDER_SIZE*2+(BLOCK_SIDE+BORDER_SIZE)*self.cursor_x+BLOCK_SIDE//2,TOPBAR_SIZE+BORDER_SIZE*2+(BLOCK_SIDE+BORDER_SIZE)*self.cursor_y+BLOCK_SIDE//2),10)
            
            pygame.display.flip()
        
        if self.lost:
            
            pygame.time.wait(600)
            self.screen.fill(BACKGROUND_COLOR)
            textsurface = self.myfont.render("YOU LOOOOOOOST", False, (255,255, 255))
            
            self.screen.blit(textsurface,(RESOLUTION_X//2,RESOLUTION_Y//2))
            pygame.display.flip()
            self.show_end = True
        elif self.win:
            pygame.time.wait(600)
            self.screen.fill(BACKGROUND_COLOR)
            textsurface = self.myfont.render("YOU WIIIIIIIN", False, (255, 255, 255))
            
            self.screen.blit(textsurface,(RESOLUTION_X//2,RESOLUTION_Y//2))
            pygame.display.flip()
            self.show_end = True
        
        pygame.display.flip()
        pygame.time.wait(int(delay*1000))
        
    def get_state(self):
        
        visible_board = np.full((SIZE_X,SIZE_Y),-2)
        
        for i in range(SIZE_X):
            for j in range(SIZE_Y):
                if self.board_states[i,j] == CLICKED_STATE:
                    visible_board[i,j] = self.board_numbers[i,j]
        position_vector = np.full((SIZE_Y),-2)
        position_vector[0] = self.cursor_x
        position_vector[1] = self.cursor_y
        visible_board = np.vstack((visible_board,position_vector))
        return visible_board
    
    def step(self,action):
        
        reward = 0
        self.last_action = action
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.running=False
        
        if action=='right':
            self.cursor_x += 1
            if self.cursor_x >= SIZE_X:
                self.cursor_x = SIZE_X-1
                reward -= OUTSIDE_PENALTY
            
        elif action=='left':
            self.cursor_x -= 1
            if self.cursor_x < 0:
                self.cursor_x = 0
                reward -= OUTSIDE_PENALTY
            
        elif action == 'up':
            self.cursor_y -= 1
            if self.cursor_y < 0:
                self.cursor_y = 0
                reward -= OUTSIDE_PENALTY
        elif action == 'down':
            self.cursor_y += 1
            if self.cursor_y >= SIZE_Y:
                self.cursor_y = SIZE_Y-1
                reward -= OUTSIDE_PENALTY
        elif action == 'click':
            reward += self.clickMine(self.cursor_x,self.cursor_y)
        
        
        self.win = self.checkwin()
        if self.win:
            reward += WIN_REWARD
        
        done = self.win or self.lost
        return self.get_state(),reward,done
    def startGame(self):
        self.running = True

    def quit_game(self):
        pygame.quit()





