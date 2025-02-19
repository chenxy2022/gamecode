import time
import os
from datetime import datetime
import pygetwindow as gw
import mss
import cv2
import numpy as np
import pyautogui
import winsound


def find_and_activate_window(window_title: str):
    try:
        # 查找窗口
        window = gw.getWindowsWithTitle(window_title)[0]  # 查找包含指定标题的第一个窗口
        print(f"找到窗口: {window.title}")
        # 激活窗口
        window.activate()
        x, y = window.midbottom
        return x, y - 10
    except IndexError:
        print(f'没有发现窗口{window_title}')
        return None


def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = sct.grab(monitor)
    img_np = np.array(img)
    img_np = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
    return img_np


def find_image_on_screen(image_path, threshold=0.8):
    screen_image = capture_screen()
    template = cv2.imread(image_path)
    if template is None:
        print("无法读取模板图像，请检查路径。")
        return None
    result = cv2.matchTemplate(screen_image, template, cv2.TM_CCOEFF_NORMED)
    yloc, xloc = np.where(result >= threshold)
    h, w = template.shape[:2]
    if len(xloc) > 0 and len(yloc) > 0:
        center_x = xloc[0] + w // 2
        center_y = yloc[0] + h // 2
        return center_x, center_y
    return None


def click_image_center(image_path):
    position = find_image_on_screen(image_path)
    if position:
        original_pos = pyautogui.position()
        pyautogui.click(*position)
        pyautogui.moveTo(*original_pos)
        time.sleep(1)
        return image_path
    return None


def main():
    images = ['x.png', 'accept.png', 'gou.png', 'auto.png', 'end.png']
    if 'end.png' in [click_image_center(img) for img in images]:
        # 播放系统提示音
        winsound.Beep(1000, 500)  # 1000赫兹，持续500毫秒


if __name__ == '__main__':
    title = "雷电模拟器"
    mid_bottom = find_and_activate_window(title)
    if mid_bottom:
        while True:
            main()
            time.sleep(1)
            now = datetime.now()
            if now.hour == 0 and now.minute == 0:
                break
        os.system("shutdown /s /t 1")
