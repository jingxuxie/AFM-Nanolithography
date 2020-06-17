# -*- coding: utf-8 -*-
"""
Created on Sat Jan 25 20:27:44 2020

@author: HP
"""

import numpy as np
import cv2


class Shape:
    def get_pos(self):
        return self.pos

    def get_width(self):
        return self.width
    
    def get_color(self):
        return self.color


class Line(Shape):
    def __init__(self, x1 = 0, y1 = 0, x2 = 0, y2 = 0, color = (255, 0, 0), \
                 width = 1, num = 0, show_distance = False):
        self.x1 = x1
        self.y1 = y1
        
        self.x2 = x2
        self.y2 = y2
        
        self.pos_refresh()
        
        self.width = width
        self.color = color
        self.num = num
        self.show_distance = show_distance
        
        #用来标记是哪种形状
        self.prop = 'line'
        
        
    def pos_refresh(self):
        self.pos1 = (self.x1, self.y1)
        self.pos2 = (self.x2, self.y2)
        self.pos = [self.pos1, self.pos2]
        
        
class Rectangle(Shape):
    def __init__(self, x1 = 0, y1 = 0, x2 = 0, y2 = 0, color = (255, 0, 0), \
                 width = 1, num = 0, show_side_length = False):
        self.x1 = min(x1, x2)
        self.x2 = max(x1, x2)
        
        self.y1 = min(y1, y2)
        self.y2 = max(y1, y2)

        self.pos_refresh()
        
        self.width = width
        self.color = color
        self.num = num
        self.show_side_length = show_side_length
        
        self.prop = 'rec'
        
    def pos_refresh(self):
        x1_temp, x2_temp = self.x1, self.x2
        y1_temp, y2_temp = self.y1, self.y2
        
        self.x1 = min(x1_temp, x2_temp)
        self.x2 = max(x1_temp, x2_temp)
        
        self.y1 = min(y1_temp, y2_temp)
        self.y2 = max(y1_temp, y2_temp)
        
        self.pos1 = (self.x1, self.y1)
        self.pos2 = (self.x2, self.y2)
        self.pos = [self.pos1, self.pos2]
        
        
        
class Circle(Shape):
    def __init__(self, x1 = 0, y1 = 0, x2 = 0, y2 = 0, color = (255, 0, 0), \
                 width = 1, num = 0, show_radius = False):
        self.x1 = x1
        self.y1 = y1
        
        self.x2 = x2
        self.y2 = y2
        
        self.pos_refresh()

        self.width = width
        self.color = color
        self.num = num
        self.show_radius = show_radius   
        
        self.prop = 'circle'
    
    def pos_refresh(self):
        self.center_x = round((self.x1 + self.x2)/2)
        self.center_y = round((self.y1 + self.y2)/2)
        self.pos = [(self.center_x, self.center_y)]
        
        radius = np.sqrt((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2)
        self.radius = round(radius/2).astype(int)


class Grating(Shape):
    def __init__(self, x1 = 0, y1 = 0, x2 = 0, y2 = 0, total_width = 0, total_height = 0, \
                 standard_distance = 0,color = (255, 0, 0), width = 1, lines = 2, num = 0, \
                 z_like = False, direction = 'up2down'):
        self.x1 = x1
        self.y1 = y1
        
        self.x2 = x2
        self.y2 = y2
        
        self.pos = [(x1,y1), (x2,y2)]
        
        self.total_width = total_width
        self.total_height = total_height
        self.standard_distance = standard_distance
        
        self.color = color
        self.width = width
        self.lines = lines
        self.num = num
        self.interval = self.total_width/max(1, self.lines-1)*standard_distance
        self.z_like = z_like
        self.direction = direction
        
        self.prop = 'grating'
        
        self.generate_grating()
    
    def generate_grating(self):
        self.grating_list = []
        for i in range(self.lines):
            self.grating_list.append(Line(int(self.x1 + i*self.interval), self.y1, \
                                          int(self.x1 + i*self.interval), self.y2, \
                                          color = self.color, num = self.num))
#        if self.z_like:
#            for i in range(self.lines):
#                self.grating_shape[i]
        


class Eraser(Shape):
    def __init__(self, x1 = 0, y1 = 0, size = 10, color = (220,220,220), width = -1, num = [0]):
        self.x1 = x1
        self.y1 = y1
        
        self.pos_refresh()
        
        self.size = size
        self.color = color
        self.num = num
        self.width = width
        
        self.prop = 'eraser'
        
    def pos_refresh(self):
        self.pos = [(self.x1, self.y1)]
        
        
class Clear_All():
    def __init__(self):
        self.prop = 'clear'
        
        
if __name__ == '__main__':

    img = np.zeros((512,512,3), np.uint8)
    shape = []
    shape.append(Line(1,2,3,4,[0,255,0],3))
    shape.append(Line(3,4,5,6))
    shape.append(Rectangle(6,9,11,-1))
    shape.append(Circle(10,10,10, width = 1))
    shape.append(Eraser(200,200, size = 10))
    shape.append(Clear_All())
    
    print(shape[0].get_pos())
    print(shape[1].get_pos())       
    print(shape[2].pos1) 
    #print(shape[3].center)
    cv2.circle(img,*shape[4].pos, shape[4].size,shape[4].color, shape[4].width)
    cv2.imshow('1',img)