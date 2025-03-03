import time, os
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import mss
import winsound


def find_window(window_title: str):
    """查找指定标题的窗口"""
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        return window
    except (IndexError, Exception) as e:
        print(f'没有发现窗口{window_title}，错误：{e}')
        return None


def capture_screen() -> np.ndarray:
    """捕获屏幕截图并返回为BGR格式的图像"""
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = sct.grab(monitor)
    return cv2.cvtColor(np.array(img), cv2.COLOR_BGRA2BGR)


def find_image_on_screen(image_path: str, threshold: float = 0.8, search_win=None, position='center') -> tuple or None:
    """在屏幕或指定窗口上查找图像"""

    screen_image = capture_screen()
    x, y = 0, 0
    if search_win:
        search_win.activate()
        x, y, width, height = search_win.left, search_win.top, search_win.width, search_win.height
        screen_image = screen_image[y:y + height, x:x + width]

    template = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if template is None:
        print(f"无法读取模板图像：{image_path}，请检查路径。")
        return None

    # 确保模板图像的尺寸小于或等于屏幕截图的尺寸
    h, w = template.shape[:2]
    screen_h, screen_w = screen_image.shape[:2]
    if h > screen_h or w > screen_w:
        template = cv2.resize(template, (min(w, screen_w), min(h, screen_h)))

    # print(template.shape, screen_image.shape, search_win)
    result = cv2.matchTemplate(screen_image, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)

    if locations[0].size > 0:
        h, w = template.shape[:2]
        center_x, center_y = locations[1][0] + w // 2, locations[0][0] + h // 2
        top_x, top_y = locations[1][0], locations[0][0]

        center_x += x
        center_y += y
        top_x += x
        top_y += y

        print(f'找到:{image_path}')
        return (center_x, center_y) if position == 'center' else (top_x, top_y)

    return None


def click_image(image_path, search_win=None, threshold=0.8, position='center'):
    """查找并点击图像"""
    if search_win:
        search_win.activate()
        time.sleep(0.5)
    pos = find_image_on_screen(image_path, search_win=search_win, threshold=threshold, position=position)
    if pos:
        x, y = pos
        pyautogui.click(x, y)
        time.sleep(1)
        return True
    return False


def click_left_select(source_pic, target_pic, win):
    """点击左侧选择，直到达到目标"""
    move_x = 50
    s_num = int(source_pic.split("_")[0])
    t_num = int(str(target_pic).split("_")[0])
    for _ in range(1, s_num - t_num):
        pyautogui.click(win.midleft[0] + move_x, win.midleft[1])
        time.sleep(.5)


def invite_player(invite_image, search_win):
    """邀请玩家"""
    time.sleep(.5)
    click_image(invite_image, search_win)


def wait_for_image(image, search_win):
    """等待指定图像出现在屏幕上"""
    while True:
        pos = find_image_on_screen(image, search_win=search_win)
        if pos:
            return pos
        time.sleep(1)


def click_for_image(image, search_win, threshold=0.8, position='center'):
    """持续查找并点击图像，直到成功"""
    while True:
        found = click_image(image, search_win, threshold, position)
        if found:
            return True
        time.sleep(1)


def execute_game_actions(caption_config, teammate_config, target_pic):
    """执行游戏动作"""
    win = caption_config['window']
    win.activate()

    click_image(caption_config['source_pic'], win)
    pyautogui.click(win.midtop[0], win.midleft[1])
    click_left_select(caption_config['source_pic'], target_pic, win)

    for select in caption_config['select_images']:
        click_image(select, win)

    invite_player(caption_config['invite_image'], win)
    teammate_ok = teammate_select(teammate_config['window'], teammate_config['pics'])
    if not teammate_ok: raise # 如果队友没法找到对应图片，那么就出错中止程序

    pos = wait_for_image(caption_config['teammate_pic'], win)
    if pos:
        pyautogui.click(*wait_for_image(caption_config['challenge_image'], win))


def teammate_select(win, pics):
    """队友点击对应的同意按钮"""
    find = False
    win.activate()
    time.sleep(1)
    for pic in pics:
        find = click_image(pic, win)
    return find


def main(caption_config, teammate_config, chapter_times):
    caption_win = find_window(caption_config['window_title'])
    teammate_win = find_window(teammate_config['window_title'])

    caption_config['window'] = caption_win
    teammate_config['window'] = teammate_win

    if not caption_win or not teammate_win:
        print("未能找到必要的窗口。请确保游戏窗口已打开。")
    else:

        for target_pic, times in chapter_times.items():
            for _ in range(times):
                execute_game_actions(caption_config, teammate_config, target_pic)

                for win_config in [caption_config, teammate_config]:
                    click_for_image(win_config['auto_image'], search_win=win_config['window'], threshold=.5,
                                    position='top_left')
                time.sleep(60 * 6)  # 等待6分钟
                for win_config in [caption_config, teammate_config]:
                    click_for_image(win_config['end_image'], search_win=win_config['window'], threshold=.5)

                while not find_image_on_screen(caption_config['source_pic'], search_win=caption_win):
                    click_for_image(caption_config['end_image'], search_win=caption_win, threshold=.5)
                    time.sleep(1)
                winsound.Beep(1000, 500)


if __name__ == '__main__':
    chapter_times = {
        # 8: 1,  # 章节1刷2次
        13: 5  # 章节13刷7次
    }

    caption_config = {
        'window_title': '行侠仗义五千年',
        'select_images': ['select.png', 'add.png'],
        'invite_image': 'first_invate.png',
        'challenge_image': 'challenge.png',
        'auto_image': 'auto.png',
        'end_image': 'z_end.png',
        'source_pic': '22_jy.png',  # 队长默认的普通章节
        'teammate_pic': 'teammate.png',  # 队友名字的截图
    }

    teammate_config = {
        'window_title': '雷电模拟器',
        'pics': ['x.png', 'accept.png', 'gou.png'],
        'auto_image': caption_config['auto_image'],
        'end_image': caption_config['end_image'],
    }

    try:
        main(caption_config, teammate_config, chapter_times)
    finally:
        # 关机
        os.system('shutdown /s /t 30')
        pass
