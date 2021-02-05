# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 14:57:19 2021

@author: mique
"""

import time
import pyautogui
import numpy as np
import win32gui,win32com,win32api

MINE_PENALTY = -200
MOVE_PENALTY = -2
NORMAL_REWARD = 10
WIN_REWARD = 100
BLOCK_SIDE = 52
class env():
    actions = ['left','right','up','down','click']
    def __init__(self):
        self.current_im,x_w,y_w,x1_w,y1_w = self.screenshot('pygame window')
        flags, hcursor, (self.cursor_x,self.cursor_y) = win32gui.GetCursorInfo()
        self.origin_x = x_w+BLOCK_SIDE//2
        self.origin_y = y_w+int(BLOCK_SIDE*1.5)
        
        self.SIZE = 12
        self.current_x = 0
        self.current_y = 0
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
    
    
    def update_cursor_pos(self):
        flags, hcursor, (self.cursor_x,self.cursor_y) = win32gui.GetCursorInfo()
    def update_im(self):
        self.current_im,x_w,y_w,x1_w,y1_w = self.screenshot('pygame window')
        
    def step(self,action):
        last_time = time.time()
        
        
        
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
            pyautogui.click(self.origin_x+self.current_x*BLOCK_SIDE,self.origin_y+self.current_y*BLOCK_SIDE)
        win32api.SetCursorPos((self.origin_x+self.current_x*BLOCK_SIDE,self.origin_y+self.current_y*BLOCK_SIDE))
        print(self.current_x,self.current_y)
        print('loop took {} seconds'.format(time.time()-last_time))
        
        
        
minesw = env()
while(True):
    curr_action = env.actions[np.random.randint(0,len(env.actions))]
    minesw.step(curr_action)