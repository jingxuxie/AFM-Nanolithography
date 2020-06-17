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
from drawing import Line, Rectangle, Circle, Grating, Eraser, Clear_All
from auxiliary_func import go_fast, background_divide, get_folder_from_file,\
    matrix_divide, float2uint8, calculate_contrast, record_draw_shape,\
    calculate_angle
from auxiliary_class import GratingProperty
from crop import find_region
from IdentifyNum import load_known, identify_num
from pywinauto.controls.win32_controls import EditWrapper, ButtonWrapper
    
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        
        self.current_dir = os.path.abspath(__file__).replace('\\','/')
        self.current_dir = get_folder_from_file(self.current_dir)
        self.current_dir += 'support_files/'
        
        #self.afp_dir, self.afp, self.bfp_dir, self.bfp = load_known()
        print(self.current_dir)
        self.get_hwnd()
        self.scan_speed = 1
        self.total_range = 20
        
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
        self.mouse_pos_initial()
        
        self.canvas_blank = np.zeros((512,512),dtype = np.int8)
        
        exitAct = QAction(QIcon(self.current_dir + 'quit.png'), '&Quit', self)        
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(qApp.quit)
        
        help_contact = QAction(QIcon(self.current_dir + 'email.png'), 'Contact', self)
        help_contact.triggered.connect(self.contact)
        
        help_about = QAction('About', self)
        help_about.triggered.connect(self.about)
        
        self.menubar = self.menuBar()
        
        FileMenu = self.menubar.addMenu('&File')
        FileMenu.addAction(exitAct)
        
        HelpMenu = self.menubar.addMenu('&Help')
        HelpMenu.addAction(help_contact)
        HelpMenu.addAction(help_about)
        
        self.read_button = QToolButton()
        self.read_button.setIcon(QIcon(self.current_dir + 'read.png'))
        self.read_button.setToolTip('Read Ctrl+R')
        self.read_button.clicked.connect(self.read)
        self.read_button.setShortcut('Ctrl+R')
        
        self.select_button = QToolButton()
        self.select_button.setIcon(QIcon(self.current_dir + 'select.png'))
        self.select_button.setToolTip('Select')
        self.select_button.clicked.connect(self.select_move_shape)
        self.select_button.setCheckable(True)
        self.select = False
        self.selecting = False
        self.select_rec = Rectangle()
        self.cursor_on_select = False
        self.moving = False
        self.move_start = [0,0]
        self.move_end = [0,0]
        
        self.drag_button = QToolButton()
        self.drag_button.setIcon(QIcon(self.current_dir + 'drag.png'))
        self.drag_button.setToolTip('Move')
        self.drag_button.clicked.connect(self.drag_shape)
        
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
        
        self.grating_button = QToolButton()
        self.grating_button.setIcon(QIcon(self.current_dir+'grating.png'))
        self.grating_button.setToolTip('Grating')
        self.grating_button.clicked.connect(self.draw_grating)
        
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
        
        self.stop_button = QToolButton()
        self.stop_button.setIcon(QIcon(self.current_dir + 'stop.png'))
        self.stop_button.setToolTip('Stop')
        self.stop_button.clicked.connect(self.stop_cut)
        
        
        self.toolbar1 = self.addToolBar('Read')
        self.toolbar1.addWidget(self.read_button)
        
        self.toolbar2 = self.addToolBar('Select')
        self.toolbar2.addWidget(self.select_button)
        self.toolbar2.addWidget(self.drag_button)
        
        self.toolbar3 = self.addToolBar('Draw')
        self.toolbar3.addWidget(self.line_button)
        self.toolbar3.addWidget(self.grating_button)
        self.toolbar3.addWidget(self.undo_button)
        self.toolbar3.addWidget(self.redo_button)
        self.toolbar3.addWidget(self.eraser_button)
        self.toolbar3.addWidget(self.clear_button)
        
        self.toolbar4 = self.addToolBar('Run')
        self.toolbar4.addWidget(self.run_button)
        self.toolbar4.addWidget(self.repeat_button)
        self.toolbar4.addWidget(self.stop_button)
        
        self.toolbar = self.addToolBar(' ')
        
        self.pixmap = QPixmap()
        self.lbl_main = QLabel(self)
        self.lbl_main.setAlignment(Qt.AlignTop)
#        self.lbl_main.setAlignment(Qt.AlignCenter)
        self.lbl_main.setPixmap(self.pixmap)
        self.lbl_main.setMouseTracking(True)
        
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.lbl_main)
        
        self.central_widget = QWidget()
        self.central_widget.setMouseTracking(True)
       
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)
        self.layout.addLayout(self.vbox)
        
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_show)
        
        self.setMouseTracking(True)
        self.setWindowTitle('Auto Cut')
        self.show()
        
        
    def read(self):
        window_name = 'Scanning control'
        
        self.scan_control_hwnd = win32gui.FindWindow(None, window_name)
        if self.scan_control_hwnd == 0:
            window_name = 'Scanning control ( Lift Mode )'
            self.scan_control_hwnd = win32gui.FindWindow(None, window_name)
#        win32gui.ShowWindow(scan_control_hwnd, win32con.SW_MAXIMIZE)
        try:
            win32gui.SendMessage(self.scan_control_hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
            win32gui.SetForegroundWindow(self.scan_control_hwnd)
        except:
            print('Can not set foreground window ')
        time.sleep(0.5)
        hwnd = self.scan_control_hwnd
        hwndChildList = []
        win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
        self.frame_hwnd = 0
        probe_position_hwnd = 0
        for hwnd_child in hwndChildList:
            name = win32gui.GetWindowText(hwnd_child)
            if 'Scan Area' in name:
                self.frame_hwnd = hwnd_child
                self.total_range = float(name[11:-3])
                print(self.total_range)
            elif name == 'probe_position':
                probe_position_hwnd = hwnd_child

        hwnd = probe_position_hwnd
        hwndChildList = []
        win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
        self.move_time_hwnd = hwndChildList[0]
        self.new_x_hwnd = hwndChildList[3]
        self.new_y_hwnd = hwndChildList[2]

        self.move_time_Edit = EditWrapper(self.move_time_hwnd)
        self.x_Edit = EditWrapper(self.new_x_hwnd)
        self.y_Edit = EditWrapper(self.new_y_hwnd)
        
#        run_hwnd = hwndChildList[3]
#        self.frame_hwnd = hwndChildList[54]
        
#        self.frame_hwnd = self.scan_control_hwnd
        '''
        self.left, self.top, self.right, self.bottom = win32gui.GetWindowRect(self.frame_hwnd)
        print(self.left, self.top, self.right, self.bottom)
        self.screenshot = pyautogui.screenshot(region=[self.left,self.top,\
                                                       self.right-self.left,\
                                                       self.bottom-self.top])
        self.screenshot = np.asarray(self.screenshot)
        '''
        self.screenshot = cv2.imread('F:/Desktop2020.1.17/AutoCut/screenshot2.bmp')
        self.screenshot = cv2.cvtColor(self.screenshot, cv2.COLOR_BGR2RGB)
        self.crop_left, self.crop_top, self.crop_right, self.crop_bottom = find_region(self.screenshot)
        self.screenshot = self.screenshot[self.crop_top: self.crop_bottom, \
                                          self.crop_left: self.crop_right]
        
#        self.img = cv2.cvtColor(np.asarray(self.img),cv2.COLOR_RGB2BGR)
        #self.read_z_pos()
        
        
        
        self.start_refresh()
        
        print('Read')

    def contact(self):
        QMessageBox.information(self, 'contact','Please contact jingxuxie@berkeley.edu '+\
                                'for support. Thanks!')
        
    def about(self):
        QMessageBox.information(self, 'About', 'AFM Auto Cut v1.0. '+ \
                                'Proudly designed and created by Jingxu Xie(谢京旭).\n \n'
                                'Copyright © 2020 Jingxu Xie. All Rights Reserved.')
        
        
    def draw_shape_initial(self):
        self.line_button.setChecked(False)
        self.draw_shape_line = False
        self.drawing_shape_line = False
        
        self.select_button.setChecked(False)
        self.select = False
        self.selecting = False
        self.select_rec = Rectangle()
        self.cursor_on_select = False
        self.moving = False
        
        self.eraser_button.setChecked(False)
        self.erase = False
        self.drawing_eraser = False
        
        
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
        
    def select_move_shape(self):
        if self.select_button.isChecked():
            self.draw_shape_initial()
            self.select = True
            self.select_button.setChecked(True)
        else:
            self.draw_shape_line = False
            self.select = False
            self.select_button.setChecked(False)
        print('select')
    
    def drag_shape(self):
        print('drag')
        
    def draw_grating(self):
        self.grating_property_widget = GratingProperty()
        self.grating_property_widget.confirmed.connect(self.creat_grating)
        self.grating_property_widget.show()
        print('grating')
    
    def creat_grating(self, s):
        if s == 'confirmed':
            total_width = float(self.grating_property_widget.total_width)
            total_height = float(self.grating_property_widget.total_height)
            lines = int(self.grating_property_widget.lines)
            
            standard_distance = self.img.shape[0]/self.total_range
            
            x1 = int((self.total_range - total_width)/2*standard_distance)
            y1 = int((self.total_range - total_height)/2*standard_distance)
            x2 = x1 + int(total_width/self.total_range*self.img.shape[0])
            y2 = y1 + int(total_height/self.total_range*self.img.shape[1])
            
            grating_temp = Grating(x1, y1, x2, y2, total_width = total_width, \
                                   total_height = total_height, \
                                   standard_distance = standard_distance,\
                                   lines = lines, color = (0,255,0),\
                                   num = self.draw_shape_count)
            self.draw_shape_count += 1
            self.draw_shape_action_list.append(grating_temp)
            print('confirmed')
            self.grating_property_widget.close()
        
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
    
    
        
    
    def mouse_pos_initial(self):
        self.mouse_x1, self.mouse_y1 = 0,0
        self.mouse_x2, self.mouse_y2 = 0,0
        self.mouse_x1_raw, self.mouse_y1_raw = 0, 0
        self.mouse_x2_raw, self.mouse_y2_raw = 0, 0
        self.mouse_pos_right = True
    
    def mousePressEvent(self, event):
        self.mouse_x1_raw = max(0, event.pos().x())
        self.mouse_y1_raw = max(0, event.pos().y())
        self.mouse_x2_raw, self.mouse_y2_raw = self.mouse_x1_raw, self.mouse_y1_raw
        self.mouse_pos_correct()
        if event.buttons() == Qt.LeftButton and self.draw_shape_line:
            if self.check_mouse_valid():
                self.draw_shape_action_list.append(Line(self.mouse_x1, self.mouse_y1, \
                                                        self.mouse_x2, self.mouse_y2, \
                                                        color = (0,255,0),\
                                                        num = self.draw_shape_count,\
                                                        show_distance = self.show_distance))
                self.draw_shape_count += 1
                self.drawing_shape_line = True
                self.undo_redo_setting()
        elif event.buttons() == Qt.LeftButton and self.erase:
            if self.check_mouse_valid():
                self.draw_shape_action_list.append(Eraser(self.mouse_x1, \
                                                          self.mouse_y1, num = [0]))
                self.drawing_eraser = True
        elif event.buttons() == Qt.LeftButton and self.select and not self.cursor_on_select:
            if self.check_mouse_valid():
                self.select_rec = Rectangle(self.mouse_x1, self.mouse_y1,\
                                            self.mouse_x2, self.mouse_y2,\
                                            num = -1, color = (0,0,0), width = 2)
                self.selecting = True
        elif event.buttons() == Qt.LeftButton and self.cursor_on_select:
            self.move_start = [self.mouse_x1, self.mouse_y1]
            self.moving = True
            
            print(self.mouse_x1, self.mouse_y1)
        #print(self.get_pos_on_screen(769, 769))
        
    def mouseMoveEvent(self, event):
        self.mouse_x2_raw = max(0, event.pos().x())
        self.mouse_y2_raw = max(0, event.pos().y())
        self.mouse_pos_correct()
        if self.drawing_shape_line and len(self.draw_shape_action_list) > 0:
            if self.check_mouse_valid():
                self.draw_shape_action_list[-1].x2 = self.mouse_x2
                self.draw_shape_action_list[-1].y2 = self.mouse_y2
                self.draw_shape_action_list[-1].pos_refresh()
        elif self.drawing_eraser and len(self.draw_shape_action_list) > 0:
            if self.check_mouse_valid():
                self.draw_shape_action_list[-1].x1 = self.mouse_x2
                self.draw_shape_action_list[-1].y1 = self.mouse_y2
                self.draw_shape_action_list[-1].pos_refresh()
        elif self.selecting:
            if self.check_mouse_valid():
                self.select_rec.x2 = self.mouse_x2
                self.select_rec.y2 = self.mouse_y2
                self.select_rec.pos_refresh()
        elif self.select and not self.moving:
            x_temp, y_temp = Pos_in_Circle(self.mouse_x2, self.mouse_y2, 20)
            self.cursor_on_select = False
            for i in range(len(x_temp)):
                if x_temp[i] < self.canvas_blank.shape[1] and y_temp[i] < self.canvas_blank.shape[0]:
                    num = self.canvas_blank[y_temp[i], x_temp[i]]
                    if num == -1:
                        self.setCursor(Qt.SizeAllCursor)
                        self.cursor_on_select = True
                        break
            if not self.cursor_on_select:
                self.setCursor(Qt.ArrowCursor)
        if self.moving:
            self.move_end = [self.mouse_x2, self.mouse_y2]
            move_x = self.move_end[0] - self.move_start[0]
            move_y = self.move_end[1] - self.move_start[1]
            self.select_rec.x1 += move_x
            self.select_rec.x2 += move_x
            self.select_rec.y1 += move_y
            self.select_rec.y2 += move_y
            self.select_rec.pos_refresh()
            self.move_start = [self.mouse_x2, self.mouse_y2]
     
    def mouseReleaseEvent(self, event):
#        if self.mouse_x1_raw == self.mouse_x2_raw and self.mouse_y1_raw == self.mouse_y2_raw:
#            if self.drawing_shape_line:
#                self.draw_shape_action_list.pop()
        if event.button() == Qt.RightButton and self.drawing_shape_line:
            self.drawing_shape_line = False
            if len(self.draw_shape_action_list) > 0:
                self.draw_shape_action_list.pop()
        if event.button() == Qt.LeftButton and self.drawing_eraser:
            self.drawing_eraser = False
            if len(self.draw_shape_action_list[-1].num) == 1:
                self.draw_shape_action_list.pop()
        if event.button() == Qt.LeftButton and self.selecting:
            self.selecting = False
        elif event.button() == Qt.LeftButton and self.moving:
            self.moving = False
        
    def mouse_pos_correct(self):
        lbl_main_x = self.lbl_main.pos().x()
        lbl_main_y = self.lbl_main.pos().y() + self.menubar.height() + self.toolbar.height()
        
        self.mouse_x1 =  self.mouse_x1_raw - lbl_main_x
        self.mouse_x2 =  self.mouse_x2_raw - lbl_main_x
        
        self.mouse_y1 =  self.mouse_y1_raw - lbl_main_y
        self.mouse_y2 =  self.mouse_y2_raw - lbl_main_y

    def check_mouse_valid(self):
        if 1 <= self.mouse_x2 < self.img.shape[1] - 1 and \
           1 <= self.mouse_x2 < self.img.shape[1] - 1 and \
           1 <= self.mouse_y2 < self.img.shape[0] - 1 and \
           1 <= self.mouse_y2 < self.img.shape[0] - 1:
            return True
        else:
            return False
        
    
    def refresh_show(self):
        self.img = self.screenshot.copy()
        #self.canvas_blank = np.zeros((self.img.shape[0], self.img.shape[1]), dtype = int)
        if self.drawing_eraser:
            eraser_temp = self.draw_shape_action_list[-1]
            cv2.circle(self.img, *eraser_temp.pos, eraser_temp.size, \
                       eraser_temp.color, eraser_temp.width)
            cv2.circle(self.img, *eraser_temp.pos, eraser_temp.size, \
                       (0,0,0), 1)
            self.find_eraser_num()
        if len(self.draw_shape_action_list) > 0:
            self.generate_draw_shape_list()
            self.draw_shape_canvas()
        if self.select:
            cv2.rectangle(self.img, *self.select_rec.pos,\
                          self.select_rec.color, self.select_rec.width)
            x_temp, y_temp = Pos_of_Rec(*list(self.select_rec.pos[0]), \
                                        *list(self.select_rec.pos[1]))
            self.canvas_blank = record_draw_shape(self.canvas_blank, \
                                                  np.array(x_temp), np.array(y_temp), \
                                                  self.select_rec.num)
            if not self.selecting:
                pass
#                x_temp, y_temp = Pos_in_Circle(self.mouse_x2, self.mouse_y2, 10)
#                on_rec = False
#                for i in range(len(x_temp)):
#                    if x_temp[i] < self.canvas_blank.shape[1] and y_temp[i] < self.canvas_blank.shape[0]:
#                        num = self.canvas_blank[y_temp[i], x_temp[i]]
#                        if num == -1:
#                            self.setCursor(Qt.SizeAllCursor)
#                            on_rec = True
#                            break
#                if not on_rec:
#                    self.setCursor(Qt.ArrowCursor)
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
                #print(self.get_distance(shape.pos[0][0], shape.pos[0][1],\
                #                        shape.pos[1][0], shape.pos[1][1]))
                
                count += 1
                if shape.show_distance:
                    distance = self.calculate_distance(shape.x1, shape.y1, shape.x2, shape.y2)
                    pos = (round((shape.x1 + shape.x2)/2), round((shape.y1 + shape.y2)/2))
                    cv2.putText(self.img, str(round(distance, 2)), pos, \
                                self.font, 0.7, (255,0,0), 1, cv2.LINE_AA)
            elif shape.prop == 'grating':
                cv2.putText(self.img, str(count), (shape.x2, shape.y2), self.font, 0.7, \
                            shape.color, 1, cv2.LINE_AA)
                count += 1
                for grating in shape.grating_list:
                    x_temp, y_temp = Pos_of_Line(*list(grating.pos[0]), *list(grating.pos[1]))
                    self.canvas_blank = record_draw_shape(self.canvas_blank, \
                                                          np.array(x_temp), np.array(y_temp), \
                                                          shape.num)
                    cv2.circle(self.img, grating.pos[0], 5, grating.color,1)
                    cv2.line(self.img, *grating.pos, grating.color, grating.width)
                    
    
    def find_eraser_num(self):
        x_temp, y_temp = Pos_in_Circle(*list(self.draw_shape_action_list[-1].pos[0]), \
                                       self.draw_shape_action_list[-1].size)
        for i in range(len(x_temp)):
            if x_temp[i] < self.canvas_blank.shape[1] and y_temp[i] < self.canvas_blank.shape[0]:
                num = self.canvas_blank[y_temp[i], x_temp[i]]
                if num != 0:
                    self.draw_shape_action_list[-1].num.append(num)
                    break                
                
            
    def start_refresh(self):
        self.refresh_timer.start(30)
    
    def show_on_screen(self):
        self.img_qi = QImage(self.img[:], self.img.shape[1], self.img.shape[0],\
                          self.img.shape[1] * 3, QImage.Format_RGB888)
        self.pixmap = QPixmap(self.img_qi)
        self.lbl_main.setPixmap(self.pixmap)
        
    
    
    def stop_cut(self):
        print('stop')

    def run_cut(self):
        draw_list_length = len(self.draw_shape_list)
        i = 0
        while i < draw_list_length:
            shape = self.draw_shape_list[i]
            if shape.prop == 'grating':
                for grating in shape:
                    shape_list = [shape]
                    self.cutting(shape_list)
            else:
                shape_list = [shape]
#            shape_points = self.get_read_list(shape.pos[0][0], shape.pos[0][1],\
#                                              shape.pos[1][0], shape.pos[1][1])
            
                for j in range(i, draw_list_length - 1):
                    shape_current = self.draw_shape_list[j]
                    shape_next = self.draw_shape_list[j + 1]
                    if shape_current.pos[1][0] == shape_next.pos[0][0] and \
                       shape_current.pos[1][1] == shape_next.pos[0][1]:
#                        shape_points += self.get_read_list(shape_next.pos[0][0], shape_next.pos[0][1],\
#                                                           shape_next.pos[1][0], shape_next.pos[1][1])
                        shape_list.append(shape_next)
                        i = j + 1
                    else:
                        break
            
            #z_pos_read = self.read_z_on_line(shape_points)
                self.cutting(shape_list)#, z_pos_read)
            i += 1
                
#                z_pos_read = self.read_z_on_line(shape.pos[0][0], shape.pos[0][1],\
#                                                 shape.pos[1][0], shape.pos[1][1])
#                
#                self.cutting(shape.pos[0][0], shape.pos[0][1],\
#                             shape.pos[1][0], shape.pos[1][1],\
#                             z_pos_read)
    
    def get_hwnd(self):
        window_name = 'NanoDrive Innova Tapping'
        innova_hwnd = win32gui.FindWindow(None, window_name)

        hwnd = innova_hwnd
        hwndChildList = []
        win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
        z_position_hwnd = 0
        z_offset_hwnd = 0
        for hwnd_child in hwndChildList:
            name = win32gui.GetWindowText(hwnd_child)
            if name == 'z_position':
                z_position_hwnd = hwnd_child
            elif name == 'z_offset':
                z_offset_hwnd = hwnd_child

        hwnd = z_position_hwnd
        hwndChildList = []
        win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
        self.z_position_hwnd = hwndChildList[3]

        hwnd = z_offset_hwnd
        hwndChildList = []
        win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
        self.z_offset_button_hwnd = hwndChildList[0]
        self.z_offset_text_hwnd = hwndChildList[2]
        
        self.z_offset_Button = ButtonWrapper(self.z_offset_button_hwnd)
        self.z_Edit = EditWrapper(self.z_offset_text_hwnd)

    def drag_prob(self, x, y):
        self.x_Edit.set_text(str(x))
        self.y_Edit.set_text(str(y))
        win32api.SendMessage(self.new_y_hwnd, win32con.WM_CHAR, 13, 0)
        

    def read_z_pos(self):
        left, top, right, bottom = win32gui.GetWindowRect(self.z_position_hwnd)
        for i in range(5):
            screenshot = pyautogui.screenshot(region=[left+1,top+1,\
                                                   right-left-2,\
                                                   bottom-top-2])
            screenshot = np.asarray(screenshot)
            ret, num = identify_num(screenshot, self.afp_dir, self.afp, self.bfp_dir, self.bfp)
            if ret:
                return True, num
    
        return False, num

    def set_offset(self, offset_number):
        self.z_Edit.set_text(str(round(offset_number, 4)))
        win32api.SendMessage(self.z_offset_text_hwnd, win32con.WM_CHAR, 13, 0)

    def cutting(self, shape_list, z_pos_read = []):
        self.move_time_Edit.set_text(str(0.5))
        win32api.SendMessage(self.move_time_hwnd, win32con.WM_CHAR, 13, 0)
        time.sleep(0.2)
        pos_x, pos_y  = self.get_pos_on_screen(shape_list[0].pos[0][0], \
                                               shape_list[0].pos[0][1])
        self.drag_prob(pos_x, pos_y)
        time.sleep(0.6)
        
        for i in range(10):
            try:
                self.z_offset_Button.click()
                break
            except:
                time.sleep(0.1)
        time.sleep(0.5)
        text = 0
        for i in range(26):
            text += 0.01
            self.set_offset(text)
            time.sleep(0.2)
        
#        points = self.get_read_list(x1, y1, x2, y2)
        for shape in shape_list:
            
            distance = self.get_distance(shape.pos[0][0], shape.pos[0][1],\
                                         shape.pos[1][0], shape.pos[1][1])
            time_cut = self.scan_speed*distance
            #time_interval = time_cut/len(z_pos_read)
            time_cut = round(time_cut, 3)
            self.move_time_Edit.set_text(str(time_cut))
            win32api.SendMessage(self.move_time_hwnd, win32con.WM_CHAR, 13, 0)
            #time.sleep(0.1)
            pos_x, pos_y  = self.get_pos_on_screen(shape.pos[1][0], shape.pos[1][1])
            self.drag_prob(pos_x, pos_y)
            #time.sleep(0.1)
            
            #self.z_offset_Button.click()
            #time.sleep(0.2)
            #time.sleep(time_cut-2)
        '''
        for i in range(1, len(z_pos_read) + 1):
            if i < len(z_pos_read):
                diff = (int(z_pos_read[-i + -1]) - int(z_pos_read[-i]))/10000
            else:
                diff = 0
            text += diff
            print(text)
            self.set_offset(text)
            time.sleep(round(time_interval - 0.05, 6))
        '''
        '''
        for i in range(1,len(points)+1):
            pos_x, pos_y = self.get_pos_on_screen(points[-i][0], points[-i][1])
            
            self.drag_prob(pos_x, pos_y)
            time.sleep(0.4)
            if i < len(points):
             #   if z_pos_read[i + 1] > z_pos_read[i]:
                diff = (int(z_pos_read[-i + -1]) - int(z_pos_read[-i]))/10000
            else:
                diff = 0
            text += diff
            print(text)
            #self.set_offset(text)
            #time.sleep(0.2)
        '''
        for i in range(10):
            try:
                self.z_offset_Button.click()
                break
            except:
                time.sleep(0.1)
        time.sleep(0.2)
        self.move_time_Edit.set_text(str(0.5))
        win32api.SendMessage(self.move_time_hwnd, win32con.WM_CHAR, 13, 0)
        time.sleep(0.5) 

    def read_z_on_line(self, points):
#        points = self.get_read_list(x1, y1, x2, y2)
        z_pos_read = []
        for point in points:
            pos_x, pos_y = self.get_pos_on_screen(point[0], point[1])
            self.drag_prob(pos_x, pos_y)
            time.sleep(0.6)
            ret, z_temp = self.read_z_pos()
            print(z_temp)
            if ret:
                z_pos_read.append(z_temp)
            else:
                if len(z_pos_read) > 0:
                    z_pos_read.append(z_pos_read[-1])
                    
        for i in range(len(points) -  len(z_pos_read)):
            z_pos_read.append(z_pos_read[-1])
        return z_pos_read
            

    def get_distance(self, x1, y1, x2, y2):
        total_pixel = self.img.shape[0]
        total_distance = self.total_range
        
        pixel = np.sqrt((x2-x1)**2 + (y2-y1)**2)

        distance = pixel/total_pixel*total_distance
        distance = round(distance, 2)
        return distance

    def get_pos_on_screen(self, x, y):
        x -= int((self.img.shape[1]/2))
        x_pos = self.get_distance(0, 0, x, 0)
        x_pos = round(x_pos,4)
        if x < 0:
            x_pos = -x_pos

        y = -y
        y += int((self.img.shape[0])/2)
        y_pos = self.get_distance(0, 0, 0, y)
        y_pos = round(y_pos, 4)
        if y < 0:
            y_pos  = -y_pos
        return x_pos, y_pos

    def get_read_list(self, x1, y1, x2, y2):
        x_temp, y_temp = Pos_of_Line(x1, y1, x2, y2)
        points = [[x1, y1]]
        x_start, y_start = x1, y1
        for i in range(len(x_temp)):
            if self.get_distance(x_temp[i], y_temp[i], x_start, y_start) > 2:
                points.append([x_temp[i], y_temp[i]])
                x_start, y_start = x_temp[i], y_temp[i]
        if points[-1][0] != x2 or points[-1][1] != y2:
            points.append([x2, y2])
        return points
            
        
    def wait_cut(self):
        pass
            
              
    def repeat_cut(self):
        print('repeat cut')
        
        

if __name__ == '__main__':
    #os.environ["CUDA_VISIBLE_DEVICES"] = "1"
    app = QApplication(sys.argv)
    
    splash_path = os.path.abspath(__file__).replace('\\','/')
    splash_path = get_folder_from_file(splash_path)
    splash = QSplashScreen(QPixmap(splash_path + 'support_files/drawing.jpg'))
    
    splash.show()
    splash.showMessage('Loading……')
    
    window = MainWindow()
    splash.close()
    sys.exit(app.exec_())




    
