# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 14:57:19 2021

@author: mique
"""

import time
import pyautogui
import win32gui,win32com.client

        
def screenshot(window_title=None):
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
            return im
        else:
            print('Window not found!')
    else:
        im = pyautogui.screenshot()
        return im
    

while(True):
    last_time = time.time()
    im = screenshot('pygame window')
    print('loop took {} seconds'.format(time.time()-last_time))
    
