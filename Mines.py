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
SIZE_X = 12
SIZE_Y = 12
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
MINE_PENALTY = 20
DISCOVERED_PENALTY = 2
PROGRESS_REWARD = 5
WIN_REWARD = 100

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
            textsurface = myfont.render(str(self.number), False, NUMBER_COLOR)
            
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
        self.show_end = False
        self.myfont = pygame.font.Font("SimplySquare.ttf",BLOCK_SIDE-int(BLOCK_SIDE*0.2))
        self.screen = pygame.display.set_mode([RESOLUTION_X,RESOLUTION_Y])        
        self.running = False
        self.points = 0
        self.board = []
        self.lost = False
        self.win = False
        self.was_mine = False
        self.was_discovered = False
        
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
        reward = 0
        for y in range(top,bot):
            for x in range(left,right):
                if y < SIZE_Y and x < SIZE_X and y>0 and x>0:
                    if self.board[y,x].state == NORMAL_STATE and not self.board[y,x].ismine:
                        self.board[y,x].state = CLICKED_STATE
                        if self.board[y,x].number == 0:
                            self.clearMines(self.board[y,x])
                        self.points+=5
                        reward += PROGRESS_REWARD
                    elif not self.board[y,x].ismine:
                        reward -= DISCOVERED_PENALTY
                    else:
                        if self.board[y,x].state == NORMAL_STATE and self.board[y,x].ismine:
                            reward -= MINE_PENALTY
                        else:
                            reward -= MINE_PENALTY
                    
        return reward
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
        
        
        if not self.show_end:
            self.screen.fill(BACKGROUND_COLOR)
            pygame.draw.rect(self.screen,UI_COLOR,pygame.Rect(BORDER_SIZE,BORDER_SIZE,RESOLUTION_X-BORDER_SIZE*2,TOPBAR_SIZE-BORDER_SIZE))
            
            pygame.draw.rect(self.screen,UI_COLOR,pygame.Rect(BORDER_SIZE,TOPBAR_SIZE+BORDER_SIZE,RESOLUTION_X-BORDER_SIZE*2,RESOLUTION_Y-(TOPBAR_SIZE+BORDER_SIZE*2)))
            
            pygame.draw.rect(self.screen,POINTS_COLOR,pygame.Rect(BORDER_SIZE*2,BORDER_SIZE*2,POINTS_SIZE,TOPBAR_SIZE-BORDER_SIZE*3))
            
            textsurface = self.myfont.render(str(self.points).zfill(4), False, NUMBER_COLOR)
            
            self.screen.blit(textsurface,(BORDER_SIZE*2*2,BORDER_SIZE*2*2))
            
            for i in range(SIZE_Y):
                for j in range(SIZE_X): 
                    self.board[i,j].drawMine(self.screen,BORDER_SIZE*2+(BLOCK_SIDE+BORDER_SIZE)*j,TOPBAR_SIZE+BORDER_SIZE*2+(BLOCK_SIDE+BORDER_SIZE)*i,self.myfont)
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

    def updateBoard(self):
        clicked = False
        r_clicked = False
        restart = False
        reward = 0
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
                    reward += self.clearMines(self.board[i,j])
                elif self.board[i,j].number != 0 and aux>0:
                    reward += PROGRESS_REWARD
                elif aux == -1:
                    
                    self.lost= True
                
                self.points += aux
        self.win = self.checkwin()
        return reward
    def startGame(self):
        self.running = True

class env():
    
    def restart(self):
        self.__init__()
    
    def get_state(self):
        b = self.board.board
        board = []
        primrow = [self.current_x,self.current_y]
        for i in range(self.SIZE-2):
            primrow.append(0)
        board.append(primrow)
        for i in range(self.SIZE):
            row = []
            for j in range(self.SIZE):
                if b[i,j].state == CLICKED_STATE:
                    row.append(b[i,j].number)
                else:
                    row.append(-2)
            board.append(row)
        return np.array(board)
    
    def screenshot(self,window_title=None):
        if window_title:
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd:
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys('%')
                win32gui.SetForegroundWindow(hwnd)
                x, y, x1, y1 = win32gui.GetClientRect(hwnd)
                x, y = win32gui.ClientToScreen(hwnd, (x, y))
                x1, y1 = win32gui.ClientToScreen(hwnd, (x1 - x, y1 - y))
                im = pyautogui.screenshot(region=(x, y, x1, y1))
                return im,x,y,x1,y1
            else:
                print('Window not found!')
        else:
            im = pyautogui.screenshot()
            return im,x,y,x1,y1
        
    def __init__(self):
        self.actions = ['left','right','up','down','click']
        self.board = MineBoard()
        self.board.startGame()
        
        self.current_im,x_w,y_w,x1_w,y1_w = self.screenshot('pygame window')
        self.origin_x = x_w+BLOCK_SIDE//2
        self.origin_y = y_w+int(BLOCK_SIDE*1.5)
        self.current_x = 0
        self.current_y = 0
        self.SIZE = SIZE_X
        
        
    def update_cursor_pos(self):
        flags, hcursor, (self.cursor_x,self.cursor_y) = win32gui.GetCursorInfo()
    def render(self):
        self.board.drawBoard()
    def step(self,action):
        reward = 0
        
        self.update_cursor_pos()
        if action == 'left':
            self.current_x -= 1
            if self.current_x < 0:
                self.current_x = 0
        elif action == 'right':
            self.current_x += 1
            if self.current_x >= self.SIZE:
                self.current_x = self.SIZE-1
        elif action == 'up':
            self.current_y -= 1
            if self.current_y < 0:
                self.current_y = 0
        elif action == 'down':
            self.current_y += 1
            if self.current_y >= self.SIZE:
                self.current_y = self.SIZE-1
        else:
            if self.board.board[self.current_y,self.current_x].state == CLICKED_STATE:
                reward -= DISCOVERED_PENALTY 
            pyautogui.click(self.origin_x+self.current_x*BLOCK_SIDE,self.origin_y+self.current_y*BLOCK_SIDE)
        win32api.SetCursorPos((self.origin_x+self.current_x*BLOCK_SIDE,self.origin_y+self.current_y*BLOCK_SIDE))
        
        rewardd = self.board.updateBoard() 
        reward += rewardd
        if self.board.lost:
            reward -= MINE_PENALTY
        elif self.board.win:
            reward += WIN_REWARD
            
        return reward,self.board.lost,self.board.win
        
        
        
