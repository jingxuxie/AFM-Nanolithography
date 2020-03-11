# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 13:59:28 2020

@author: HP
"""
import numpy as np
from numba import jit
import cv2


def find_region(img0):
    img = img0.copy()
    r, g, b = cv2.split(img)
    
    ret,thresh_r = cv2.threshold(r,254,255,cv2.THRESH_BINARY)
    ret,thresh_g = cv2.threshold(g,0,255,cv2.THRESH_BINARY_INV)
    ret,thresh_b = cv2.threshold(b,0,255,cv2.THRESH_BINARY_INV)
    
    temp = cv2.bitwise_and(thresh_r,thresh_g)#,mask = thresh_g)
    img = cv2.bitwise_and(temp, thresh_b)
    
    return calculate_region(img)

@jit
def calculate_region(img):
    row = img.shape[0]
    column = img.shape[1]
    
    left, top = 0, 0
    right, bottom = row-1, column-1
    #找top
    for i in range(row):
        count = 0
        for j in range(column):
            if img[i,j] == 255:
                count += 1
        if count == 4:
            top = i
            break
    #找bottom
    for i in range(row):
        count = 0
        for j in range(column):
            if img[row-1-i, j] == 255:
                count += 1
        if count == 4:
            bottom = row-i
            break
    #找left
    for i in range(column):
        count = 0
        for j in range(row):
            if img[j, i] == 255:
                count += 1
        if count == 4:
            left = i
            break
        
    #找right
    for i in range(column):
        count = 0
        for j in range(row):
            if img[j, column-1-i] == 255:
                count += 1
        if count == 4:
            right = column-i
            break
    right = bottom - top + left    
    print(left, top, right, bottom)

    return left, top, right, bottom


if __name__ == '__main__':
    screenshot = cv2.imread('F:/Desktop2020.1.17/AutoCut/screenshot2.bmp')
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
    left, top, right, bottom = find_region(screenshot)
    
    
    
