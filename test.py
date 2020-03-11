import win32gui
import pyautogui
import numpy as np
from pywinauto.controls.win32_controls import ButtonWrapper, EditWrapper
'''
window_name = 'NanoDrive Innova Tapping'
innova_hwnd = win32gui.FindWindow(None, window_name)

hwnd = innova_hwnd
hwndChildList = []
win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
for hwnd_child in hwndChildList:
    name = win32gui.GetWindowText(hwnd_child)
    if name == 'z_position':
        z_position_hwnd = hwnd_child
    elif name == 'z_offset':
        z_offset_hwnd = hwnd_child
        print('yes!')
        
hwnd = z_position_hwnd
hwndChildList = []
win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)

z_position_hwnd = hwndChildList[3]
edit = EditWrapper(z_position_hwnd)
print(edit.text_block())
left, top, right, bottom = win32gui.GetWindowRect(z_position_hwnd)
screenshot = pyautogui.screenshot(region=[left+1,top+1,\
                                               right-left-2,\
                                               bottom-top-2])
screenshot = np.asarray(screenshot)
print(screenshot.shape)

hwnd = z_offset_hwnd
hwndChildList = []
win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
z_offset_button_hwnd = hwndChildList[0]
z_offset_text_hwnd = hwndChildList[2]
print(win32gui.GetWindowText(z_offset_text_hwnd))

button = ButtonWrapper(z_offset_button_hwnd)
button.click()
print(button.is_checked())
'''
'''
for hwnd_child in hwndChildList:
    name = win32gui.GetWindowText(hwnd_child)
    print(win32gui.GetWindowText(hwnd_child))
    '''



window_name = 'Scanning control'
scan_control_hwnd = win32gui.FindWindow(None, window_name)

hwnd = scan_control_hwnd
hwndChildList = []
win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
for hwnd_child in hwndChildList:
    name = win32gui.GetWindowText(hwnd_child)
    if name == 'probe_position':
        probe_position_hwnd = hwnd_child
        print('yes!')

hwnd = probe_position_hwnd
hwndChildList = []
win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
new_x_hwnd = hwndChildList[3]
new_y_hwnd = hwndChildList[2]
move_time_hwnd = hwndChildList[0]

#print(win32gui.GetWindowRect(new_x_hwnd))
#print(win32gui.GetWindowRect(new_y_hwnd))
move_time_Edit = EditWrapper(move_time_hwnd)
move_time_Edit.set_text(5)
'''
for hwnd_child in hwndChildList:
    name = win32gui.GetWindowRect(hwnd_child)
    print(name)
'''






