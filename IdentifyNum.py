# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 10:54:55 2020

@author: HP
"""
import os
import cv2
import numpy as np
from auxiliary_func import get_folder_from_file
import time

def find_point(img):
    img_temp = img.copy()

    start_1, end_1 = 0, 0
    start_2, end_2 = 0, 0
    
    bk = np.zeros(img_temp.shape[1])
    gray = np.zeros(img_temp.shape[1])
    for j in range(img_temp.shape[1]):
        for i in range(img_temp.shape[0]):
            if (img_temp[i,j] == [240, 240, 240]).all():
                bk[j] += 1
            elif (i == 10 or i == 11) and (img_temp[i,j] == [160, 160, 160]).all():
                gray[j] += 1
                
        if bk[j] != 16 and j >1 and bk[j-1] == 16:
            start_1 = j
        elif bk[j] == 16 and j > 1 and bk[j-1] != 16:
            end_2 = j
        elif bk[j] == 13 and gray[j] == 2:
            end_1 = j - 1
            start_2 = j+2
            
    return start_1, end_1, start_2, end_2


def load_known():
    #global afp_dir, afp, bfp_dir, bfp
    current_dir = os.path.abspath(__file__).replace('\\','/')
    current_dir = get_folder_from_file(current_dir)
    
    afp_folder = current_dir + 'support_files/afp/'
    bfp_folder = current_dir + 'support_files/bfp/'
    
    afp_dir = os.listdir(afp_folder)
    bfp_dir = os.listdir(bfp_folder)
    
    afp = []
    for file in afp_dir:
        img_temp = cv2.imread(afp_folder+file)
        afp.append(img_temp)
        #print(file)
        
    bfp = []
    for file in bfp_dir:
        img_temp = cv2.imread(bfp_folder+file)
        bfp.append(img_temp)
    return afp_dir, afp, bfp_dir, bfp


def identify_num(img, afp_dir, afp, bfp_dir, bfp):
    start_1, end_1, start_2, end_2 = find_point(img)
    seg_1 = img[:,start_1:end_1]
    unit, decimal = '0', '0'
    for j in range(len(bfp)):
        if seg_1.shape == bfp[j].shape:
            if (seg_1 == bfp[j]).all():
                unit = bfp_dir[j][:-4]
                break
    seg_2 = img[:,start_2:end_2]
    for j in range(len(afp)):
        if seg_2.shape == afp[j].shape:
            if (seg_2 == afp[j]).all():
                decimal = afp_dir[j][:-4]
                break
            
    if decimal != '0':
        return True, unit + decimal
    else:
        return False, unit + decimal
    
if __name__ == '__main__':
    #filepath = 'F:/Desktop2020.1.17/pictures/'
    #img_temp = cv2.imread('F:/Desktop2020.1.17/pictures/-29999.bmp')
    load_known()
    time_start = time.time()
    #ret, num = identify_num(img_temp)
    time_end = time.time()
    print(time_end - time_start)
    
