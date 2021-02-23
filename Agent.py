# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 10:58:47 2021

@author: mique
"""

from Mines import MineBoardEnv
import numpy as np
class Agent():
    
    def __init__(self,algorithm):
        self.env = MineBoardEnv()
        self.state = self.env.get_state()
        self.blocks = self.state[:-1]
        self.pos_x = self.state[-1,0]
        self.pos_y = self.state[-1,1]
        self.n_mines = int(self.blocks.shape[0]*self.blocks.shape[0]*0.2)
        self.done = False
        
    def make_action(self,action):
        self.state, _ ,self.done = self.env.step(action)
        self.blocks = self.state[:-1]
        self.pos_x = self.state[-1,0]
        self.pos_y = self.state[-1,1]
        self.env.render(2)
    def pick_block(self):

        block_points = np.full(self.blocks.shape,200.0)
        
        blocks = self.blocks
        if np.any(self.blocks != -1):
            for y in range(self.blocks.shape[0]):
                for x in range(self.blocks.shape[1]):
                        
                    if self.blocks[y,x] == -2:
                        if not (self.pos_x == x and self.pos_y == y):
                            block_points[y,x] = 0
                            y_min_safe = y - 1
                            if y_min_safe < 0:
                                y_min_safe = 0
                            x_min_safe = x - 1
                            if x_min_safe < 0:
                                x_min_safe = 0
                            
                            y_max_safe = y_min_safe+3
                            if y_max_safe > self.blocks.shape[0]-1:
                                y_max_safe = self.blocks.shape[0]-1
                            x_max_safe = x_min_safe+3
                            if x_max_safe > self.blocks.shape[0]-1:
                                x_max_safe = self.blocks.shape[0]-1
                            
                            sum_prob = 0
                            number_sum = 0
                            for y2 in range(y_min_safe,y_max_safe):
                                for x2 in range(x_min_safe,x_max_safe):
                                    if self.blocks[y2,x2] != -2 and self.blocks[y2,x2] != 0:
                                        
                                            
                                            number = self.blocks[y2,x2]
                                            number_sum += number
                                            y_min_safe2 = y2 - 1
                                            if y_min_safe2 < 0:
                                                y_min_safe2 = 0
                                            x_min_safe2 = x2 - 1
                                            if x_min_safe2 < 0:
                                                x_min_safe2 = 0
                                                
                                            y_max_safe2 = y_min_safe2+3
                                            if y_max_safe2 > self.blocks.shape[0]-1:
                                                y_max_safe2 = self.blocks.shape[0]-1
                                            x_max_safe2 = x_min_safe2+3
                                            if x_max_safe2 > self.blocks.shape[0]-1:
                                                x_max_safe2 = self.blocks.shape[0]-1
                                            
                                            _,count = np.where(self.blocks[y_min_safe2:y_max_safe2, x_min_safe2:x_max_safe2] == -2)
                                            sum_prob += number/len(count)
                            block_points[y,x] = sum_prob + ((self.n_mines-number_sum) / self.blocks.shape[0]**2)
                        else:
                            block_points[y,x] = 200
        block = np.argmin(block_points)
        y = int(block/self.blocks.shape[0])
        x = block-y
        if x > self.blocks.shape[0]:
            x -= self.blocks.shape[0]
        print(block)
        print(x,y)
        print(np.min(block_points))
        print(block_points)
        
        return x,y

    def get_route(self,x,y):
        if y > self.pos_y:
            for i in range(abs(y-self.pos_y)):
                self.make_action('down')
        else:
            for i in range(abs(y-self.pos_y)):
                self.make_action('up')
        if x > self.pos_x:
            for i in range(abs(x-self.pos_x)):
                self.make_action('right')
        else:
            for i in range(abs(x-self.pos_x)):
                self.make_action('left')
        
                                        
                

a = Agent('')

while not a.done:
    x,y = a.pick_block()
    a.get_route(x,y)
    a.make_action('click')