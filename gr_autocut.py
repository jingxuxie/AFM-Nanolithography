# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 22:16:23 2020

@author: HP
"""
from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QHBoxLayout, \
    QLabel, QApplication, QGridLayout, QPushButton, QCheckBox, QAction, \
    QFileDialog, QMainWindow, QDesktopWidget, QToolButton, QComboBox,\
    QMessageBox, QProgressBar, QSplashScreen, QLineEdit, QShortcut, QMenu,\
    QColorDialog, qApp
from PyQt5.QtCore import Qt, QThread, QTimer, QObject, pyqtSignal, QBasicTimer, \
    QEvent
from PyQt5.QtGui import QPixmap, QImage, QIcon
import pyqtgraph as pg
import sys
import cv2
import os
import time
#from BresenhamAlgorithm import Pos_of_Line, Pos_of_Circle, Pos_in_Circle, \
#    Pos_of_Rec 
import copy
from numba import jit
#from drawing import Line, Rectangle, Circle, Eraser, Clear_All
import win32gui
import win32api
import win32con
import pyautogui
import numpy as np
from BresenhamAlgorithm import Pos_of_Line, Pos_of_Circle, Pos_in_Circle, \
    Pos_of_Rec 
from drawing import Line, Rectangle, Circle, Eraser, Clear_All
from auxiliary_func import go_fast, background_divide, get_folder_from_file,\
    matrix_divide, float2uint8, calculate_contrast, record_draw_shape,\
    calculate_angle
from crop import find_region
    
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        
        self.current_dir = 'F:/Desktop2020.1.17/AutoCut/'
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
        self.mouse_pos_initial()
        
        exitAct = QAction(QIcon('quit.jpg'), '&Quit', self)        
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(qApp.quit)
        
        help_contact = QAction('Contact', self)
        help_contact.triggered.connect(self.contact)
        
        self.menubar = self.menuBar()
        
        FileMenu = self.menubar.addMenu('&File')
        FileMenu.addAction(exitAct)
        
        HelpMenu = self.menubar.addMenu('&Help')
        HelpMenu.addAction(help_contact)
        
        
        self.read_button = QToolButton()
        self.read_button.setIcon(QIcon(self.current_dir + 'read.png'))
        self.read_button.setToolTip('Read Ctrl+R')
        self.read_button.clicked.connect(self.read)
        self.read_button.setShortcut('Ctrl+R')
        
        self.draw_shape_action_list = []
        self.draw_shape_list = []
        self.draw_shape_action_list_for_redo = []
        self.draw_shape_count = 1
        
        self.line_button = QToolButton()
        self.line_button.setIcon(QIcon(self.current_dir+'line.png'))
        self.line_button.setToolTip('Draw line')
        self.line_button.clicked.connect(self.draw_line)
        self.line_button.setCheckable(True)
        self.draw_shape_line = False
        self.drawing_shape_line = False
        self.show_distance = False
        
#        line = Line(0,0,100,100)
        
        self.eraser_button = QToolButton()
        self.eraser_button.setIcon(QIcon(self.current_dir+'eraser.png'))
        self.eraser_button.setToolTip('eraser')
        self.eraser_button.clicked.connect(self.erase_shape)
        self.eraser_button.setCheckable(True)
        self.erase = False
        self.drawing_eraser = False
        
        self.undo_button = QToolButton()
        self.undo_button.setIcon(QIcon(self.current_dir+'undo_gray_opacity.png'))
        self.undo_button.setToolTip('undo  Ctrl+Z')
        self.undo_button.clicked.connect(self.undo_draw)
        self.undo_button.setShortcut('Ctrl+Z')
        
        self.redo_button = QToolButton()
        self.redo_button.setIcon(QIcon(self.current_dir+'redo_gray_opacity.png'))
        self.redo_button.setToolTip('redo  Ctrl+Y')
        self.redo_button.clicked.connect(self.redo_draw)
        self.redo_button.setShortcut('Ctrl+Y')
        
        self.clear_button = QToolButton()
        self.clear_button.setIcon(QIcon(self.current_dir+'clear.png'))
        self.clear_button.setToolTip('clear drawing')
        self.clear_button.clicked.connect(self.clear_draw)
        
        self.run_button = QToolButton()
        self.run_button.setIcon(QIcon(self.current_dir + 'run.png'))
        self.run_button.setToolTip('Run F5')
        self.run_button.clicked.connect(self.run_cut)
        self.run_button.setShortcut('F5')
        
        self.repeat_button = QToolButton()
        self.repeat_button.setIcon(QIcon(self.current_dir + 'repeat.png'))
        self.repeat_button.setToolTip('Repeat')
        self.repeat_button.clicked.connect(self.repeat_cut)
        
        
        self.toolbar1 = self.addToolBar('Read')
        self.toolbar1.addWidget(self.read_button)
        
        self.toolbar2 = self.addToolBar('draw')
        self.toolbar2.addWidget(self.line_button)
        self.toolbar2.addWidget(self.undo_button)
        self.toolbar2.addWidget(self.redo_button)
        self.toolbar2.addWidget(self.eraser_button)
        self.toolbar2.addWidget(self.clear_button)
        
        self.toolbar3 = self.addToolBar('run')
        self.toolbar3.addWidget(self.run_button)
        self.toolbar3.addWidget(self.repeat_button)
        
        self.toolbar = self.addToolBar(' ')
        
        self.pixmap = QPixmap()
        self.lbl_main = QLabel(self)
        self.lbl_main.setAlignment(Qt.AlignTop)
#        self.lbl_main.setAlignment(Qt.AlignCenter)
        self.lbl_main.setPixmap(self.pixmap)
        
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.lbl_main)
        
        self.central_widget = QWidget()
       
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)
        self.layout.addLayout(self.vbox)
        
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_show)
        
        self.setWindowTitle('Auto Cut')
        self.show()
        
        
    def read(self):
        window_name = 'Scanning control'
        
        self.scan_control_hwnd = win32gui.FindWindow(None, window_name)
        if self.scan_control_hwnd == 0:
            window_name = 'Scanning control ( Lift Mode )'
            self.scan_control_hwnd = win32gui.FindWindow(None, window_name)
#        win32gui.ShowWindow(scan_control_hwnd, win32con.SW_MAXIMIZE)
        
        win32gui.SendMessage(self.scan_control_hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
        win32gui.SetForegroundWindow(self.scan_control_hwnd)
        time.sleep(0.5)
        hwnd = self.scan_control_hwnd
        hwndChildList = []
        win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
        for hwnd_child in hwndChildList:
            name = win32gui.GetWindowText(hwnd_child)
            if 'Scan Area' in name:
                self.frame_hwnd = hwnd_child
                break
#        run_hwnd = hwndChildList[3]
#        self.frame_hwnd = hwndChildList[54]
        
#        self.frame_hwnd = self.scan_control_hwnd
        
        self.left, self.top, self.right, self.bottom = win32gui.GetWindowRect(self.frame_hwnd)
        print(self.left, self.top, self.right, self.bottom)
        self.screenshot = pyautogui.screenshot(region=[self.left,self.top,\
                                                       self.right-self.left,\
                                                       self.bottom-self.top])
        self.screenshot = np.asarray(self.screenshot)
        #self.screenshot = cv2.imread('F:/Desktop2020.1.17/AutoCut/screenshot2.bmp')
        #self.screenshot = cv2.cvtColor(self.screenshot, cv2.COLOR_BGR2RGB)
        self.crop_left, self.crop_top, self.crop_right, self.crop_bottom = find_region(self.screenshot)
        self.screenshot = self.screenshot[self.crop_top: self.crop_bottom, \
                                          self.crop_left: self.crop_right]
#        self.img = cv2.cvtColor(np.asarray(self.img),cv2.COLOR_RGB2BGR)
        
        self.start_refresh()
        
        print('Read')

    def contact(self):
        print('contact')
        
    
    def mouse_pos_initial(self):
        self.mouse_x1, self.mouse_y1 = 0,0
        self.mouse_x2, self.mouse_y2 = 0,0    
    
    def mousePressEvent(self, event):
        self.mouse_x1_raw = max(0, event.pos().x())
        self.mouse_y1_raw = max(0, event.pos().y())
        self.mouse_x2_raw, self.mouse_y2_raw = self.mouse_x1_raw, self.mouse_y1_raw
        self.mouse_pos_correct()
        if event.buttons() == Qt.LeftButton and self.draw_shape_line:
            
            self.draw_shape_action_list.append(Line(self.mouse_x1, self.mouse_y1, \
                                                    self.mouse_x2, self.mouse_y2, \
                                                    color = (0,255,0),\
                                                    num = self.draw_shape_count,\
                                                    show_distance = self.show_distance))
            self.draw_shape_count += 1
            self.drawing_shape_line = True
            self.undo_redo_setting()
        elif event.buttons() == Qt.LeftButton and self.erase:
            self.draw_shape_action_list.append(Eraser(self.mouse_x1, \
                                                      self.mouse_y1, num = [0]))
            self.drawing_eraser = True
            
            print(self.mouse_x1, self.mouse_y1)
        
    def mouseMoveEvent(self, event):
        self.mouse_x2_raw = max(0, event.pos().x())
        self.mouse_y2_raw = max(0, event.pos().y())
        self.mouse_pos_correct()
        if self.drawing_shape_line:
            
            self.draw_shape_action_list[-1].x2 = self.mouse_x2
            self.draw_shape_action_list[-1].y2 = self.mouse_y2
            self.draw_shape_action_list[-1].pos_refresh()
        if self.drawing_eraser:
                self.draw_shape_action_list[-1].x1 = self.mouse_x2
                self.draw_shape_action_list[-1].y1 = self.mouse_y2
                self.draw_shape_action_list[-1].pos_refresh()
     
    def mouseReleaseEvent(self, event):
        if self.mouse_x1_raw == self.mouse_x2_raw and self.mouse_y1_raw == self.mouse_y2_raw:
            if self.drawing_shape_line:
                self.draw_shape_action_list.pop()
        if event.button() == Qt.LeftButton and self.drawing_eraser:
            self.drawing_eraser = False
            if len(self.draw_shape_action_list[-1].num) == 1:
                self.draw_shape_action_list.pop()
        
    def mouse_pos_correct(self):
        lbl_main_x = self.lbl_main.pos().x()
        lbl_main_y = self.lbl_main.pos().y() + self.menubar.height() + self.toolbar.height()
        
        self.mouse_x1 =  self.mouse_x1_raw - lbl_main_x
        self.mouse_x2 =  self.mouse_x2_raw - lbl_main_x
        
        self.mouse_y1 =  self.mouse_y1_raw - lbl_main_y
        self.mouse_y2 =  self.mouse_y2_raw - lbl_main_y
        
    def refresh_show(self):
        self.img = self.screenshot.copy()
        if len(self.draw_shape_action_list) > 0:
            self.generate_draw_shape_list()
            self.draw_shape_canvas()
        if self.drawing_eraser:
            eraser_temp = self.draw_shape_action_list[-1]
            cv2.circle(self.img, *eraser_temp.pos, eraser_temp.size, \
                       eraser_temp.color, eraser_temp.width)
            cv2.circle(self.img, *eraser_temp.pos, eraser_temp.size, \
                       (0,0,0), 1)
#            self.find_eraser_num()
        self.show_on_screen()
        
        
    def generate_draw_shape_list(self):
        self.draw_shape_list = []
        for action in self.draw_shape_action_list:
            if action.prop != 'eraser' and action.prop != 'clear':
                self.draw_shape_list.append(action)
            elif action.prop == 'eraser':
                i = 0
                while i < len(self.draw_shape_list):
                    if self.draw_shape_list[i].num in action.num:
                        #print(action.num)
                        self.draw_shape_list.pop(i)
                        i -= 1
                    i += 1
                    if i == len(self.draw_shape_list):
                        break
            elif action.prop == 'clear':
                self.draw_shape_list = []    
        
    def draw_shape_canvas(self):
        #目前canvas还没什么用，均可用img_show代替，但也可以先留着
        self.canvas = np.zeros(self.img.shape, dtype = np.uint8)
        self.canvas_blank = np.zeros((self.img.shape[0], self.img.shape[1]), dtype = int)
        count = 1
        if len(self.draw_shape_list) == 0:
            pass
        for shape in self.draw_shape_list:
#            shape.x1, shape.y1 = self.mouse_pos_ratio_change_line(shape.x1, shape.y1)
#            shape.x2, shape.y2 = self.mouse_pos_ratio_change_line(shape.x2, shape.y2)
#            shape.pos_refresh()
            if shape.prop == 'line' or shape.prop == 'base line':
                x_temp, y_temp = Pos_of_Line(*list(shape.pos[0]), *list(shape.pos[1]))
                self.canvas_blank = record_draw_shape(self.canvas_blank, \
                                                      np.array(x_temp), np.array(y_temp), \
                                                      shape.num)
                cv2.circle(self.img, shape.pos[0], 5, shape.color,1)
                cv2.line(self.img, *shape.pos, shape.color, shape.width)
                cv2.putText(self.img, str(count), shape.pos[1], self.font, 0.7, \
                            shape.color, 1, cv2.LINE_AA)
                count += 1
                if shape.show_distance:
                    distance = self.calculate_distance(shape.x1, shape.y1, shape.x2, shape.y2)
                    pos = (round((shape.x1 + shape.x2)/2), round((shape.y1 + shape.y2)/2))
                    cv2.putText(self.img, str(round(distance, 2)), pos, \
                                self.font, 0.7, (255,0,0), 1, cv2.LINE_AA)
                    
                
            
    def start_refresh(self):
        self.refresh_timer.start(30)
    
    def show_on_screen(self):
        self.img_qi = QImage(self.img[:], self.img.shape[1], self.img.shape[0],\
                          self.img.shape[1] * 3, QImage.Format_RGB888)
        self.pixmap = QPixmap(self.img_qi)
        self.lbl_main.setPixmap(self.pixmap)
        
    def draw_line(self):
        if self.line_button.isChecked():
            self.draw_shape_initial()
            self.draw_shape_line = True
            self.line_button.setChecked(True)
        else:
            self.draw_shape_line = False
            self.drawing_shape_line = False
            self.line_button.setChecked(False)
        print('draw line')
        
    def erase_shape(self):
        if self.eraser_button.isChecked():
            self.draw_shape_initial()
            self.erase = True
            self.eraser_button.setChecked(True)
        else:
            self.erase = False
            self.eraser_button.setChecked(False)
    
    def undo_redo_setting(self):
        self.undo_button.setIcon(QIcon(self.current_dir+'undo.png'))
        self.draw_shape_action_list_for_redo = []
        self.redo_button.setIcon(QIcon(self.current_dir+'redo_gray_opacity.png')) 
    
    def undo_draw(self):
        if len(self.draw_shape_action_list) > 0:
            self.draw_shape_action_list_for_redo.append(self.draw_shape_action_list[-1])
            self.redo_button.setIcon(QIcon(self.current_dir+'redo.png'))
            self.draw_shape_action_list.pop()
            if len(self.draw_shape_action_list) == 0:
                self.undo_button.setIcon(QIcon(self.current_dir+'undo_gray_opacity.png'))
        
    def redo_draw(self):
        if len(self.draw_shape_action_list_for_redo) > 0:
            self.draw_shape_action_list.append(self.draw_shape_action_list_for_redo[-1])
            self.undo_button.setIcon(QIcon(self.current_dir+'undo.png'))
            self.draw_shape_action_list_for_redo.pop()
            if len(self.draw_shape_action_list_for_redo) == 0:
                self.redo_button.setIcon(QIcon(self.current_dir+'redo_gray_opacity.png'))
        
    def clear_draw(self):
        self.draw_shape_initial()
        self.draw_shape_action_list.append(Clear_All())
    
    def draw_shape_initial(self):
        self.line_button.setChecked(False)
        self.draw_shape_line = False
        self.drawing_shape_line = False
        
        self.eraser_button.setChecked(False)
        self.erase = False
        self.drawing_eraser = False
    
    def run_cut(self):
        if len(self.draw_shape_list) > 0:
            win32gui.SetForegroundWindow(self.scan_control_hwnd)
            #self.left, self.top, self.right, self.bottom = win32gui.GetWindowRect(self.frame_hwnd)
            #screenshot_temp = pyautogui.screenshot(region=[self.left,self.top,\
            #                                           self.right-self.left,\
            #                                           self.bottom-self.top])
            #screenshot_temp  = np.asarray(screenshot_temp)
            #self.crop_left, self.crop_top, self.crop_right, self.crop_bottom = find_region(screenshot_temp)
            a = pyautogui.locateCenterOnScreen('G:/1.png')
            for shape in self.draw_shape_list:
                pyautogui.moveTo(self.left + self.crop_left, self.top + self.crop_top)
                pyautogui.moveRel(list(shape.pos[0])[0], list(shape.pos[0])[1])
                pyautogui.dragRel(list(shape.pos[1])[0] - list(shape.pos[0])[0], \
                                  list(shape.pos[1])[1] - list(shape.pos[0])[1], duration=0.25)
                try:
                    pyautogui.moveTo(a[0], a[1])
                except:
                    a = pyautogui.locateCenterOnScreen('G:/1.png')
                    time.sleep(0.5)
                    pyautogui.moveTo(a[0], a[1])
                pyautogui.click()
                time.sleep(1)
                pyautogui.moveRel(300, 300)
                self.wait_cut()
                #time.sleep(15)

    def wait_cut(self):
        for i in range(30):
            a = pyautogui.locateCenterOnScreen('G:/1.png')
            if a == None:
                time.sleep(1)
            else:
                break
            
              
    def repeat_cut(self):
        print('repeat cut')
        
        

if __name__ == '__main__':
    #os.environ["CUDA_VISIBLE_DEVICES"] = "1"
    app = QApplication(sys.argv)
    
    window = MainWindow()
    sys.exit(app.exec_())




    
