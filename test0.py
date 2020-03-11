# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 11:24:45 2020

@author: HP
"""

import cv2
from numba import jit

img = cv2.imread('F:/Desktop2020.1.17/AutoCut/screenshot3.bmp')
b,g,r = cv2.split(img)
ret,thresh_b = cv2.threshold(b,0,255,cv2.THRESH_BINARY_INV)
ret,thresh_g = cv2.threshold(g,0,255,cv2.THRESH_BINARY_INV)
ret,thresh_r = cv2.threshold(r,254,255,cv2.THRESH_BINARY)

temp_rg = cv2.bitwise_and(thresh_r,thresh_g)#,mask = thresh_g)
temp_rgb = cv2.bitwise_and(temp_rg, thresh_b)

#cv2.imshow('1',thresh_b)
cv2.imshow('2', temp_rgb)

@jit
def find_region(img):
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
        if count > 1:
            top = i
            break
    #找bottom
    for i in range(row):
        count = 0
        for j in range(column):
            if img[row-1-i, j] == 255:
                count += 1
        if count > 1:
            bottom = row-i
            break
    #找left
    for i in range(column):
        count = 0
        for j in range(row):
            if img[j, i] == 255:
                count += 1
        if count > 1:
            left = i
            break
        
    #找right
    for i in range(column):
        count = 0
        for j in range(row):
            if img[j, column-1-i] == 255:
                count += 1
        if count > 1:
            right = column-i
            break
        
    print(top, bottom, left, right)

    return left, top, right, bottom
    
left, top, right, bottom = find_region(temp_rgb)
img = img[top:bottom, left:right]
cv2.imshow('2', img)
