import time
from datetime import datetime
import cv2
import numpy as np
import pyautogui
import winsound
import os
import pygetwindow as gw  # 直接导入 pygetwindow 模块
import mss


def find_and_activate_window(window_title: str) -> tuple or None:
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        print(f"找到窗口: {window.title}")
        window.activate()
        x, y = window.midbottom
        return x, y - 10
    except (IndexError, Exception) as e:
        print(f'没有发现窗口{window_title}，错误：{e}')
        return None


def capture_screen() -> np.ndarray:
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = sct.grab(monitor)
    return cv2.cvtColor(np.array(img), cv2.COLOR_BGRA2BGR)


def find_image_on_screen(image_path: str, threshold: float = 0.8) -> tuple or None:
    screen_image = capture_screen()
    template = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if template is None:
        print(f"无法读取模板图像：{image_path}，请检查路径。")
        return None
    result = cv2.matchTemplate(screen_image, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    if locations[0].size > 0:
        h, w = template.shape[:2]
        center_x, center_y = locations[1][0] + w // 2, locations[0][0] + h // 2
        return center_x, center_y
    return None


def click_image_center(image_path: str) -> str or None:
    position = find_image_on_screen(image_path)
    if position:
        original_pos = pyautogui.position()
        pyautogui.click(*position)
        pyautogui.moveTo(*original_pos)
        time.sleep(1)
        return image_path
    return None


def main():
    if shutdown_signal_image in (click_image_center(img) for img in images_to_find):
        # 播放系统提示音
        winsound.Beep(1000, 500)  # 1000赫兹，持续500毫秒


if __name__ == '__main__':
    window_title = "雷电模拟器"
    images_to_find = ['x.png', 'accept.png', 'gou.png', 'auto.png', 'end.png']
    shutdown_signal_image = 'end.png'
    mid_bottom = find_and_activate_window(window_title)
    if mid_bottom:
        while True:
            main()
            time.sleep(1)
            now = datetime.now()
            if now.hour == 0 and now.minute == 0:
                break
        os.system("shutdown /s /t 1")
