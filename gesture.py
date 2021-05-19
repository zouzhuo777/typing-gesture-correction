from actual_keyboard import get_actual_keyboard
import cv2
import pandas as pd
import numpy as np
import random
from img_merge import merge_img

# 键盘和手指对应关系
mz = ['space']
sz_left = list('45rtfgvb')
sz_right = list('67yuhjnm')
zz_left = list('3edc')
zz_right = list('8ik,') + ['alt']
wmz_left = list('2wsx') + ['alt']
wmz_right = list('9ol.') + ['win']
xz_left = list('1qaz') + ['`', 'tab', 'caps lock', 'shift', 'ctrl', 'win']
xz_right = list('0p;/-[\'=]\\') + ['backspace', 'return', 'shift', 'ctrl', 'fn']


def trans_points(ppoints, MM):
    points_after = np.matmul(ppoints, MM.T)
    points_after0 = np.array([points_after[:, 0] / points_after[:, 2]]).T
    points_after1 = np.array([points_after[:, 1] / points_after[:, 2]]).T
    points_after = np.hstack((points_after0, points_after1))
    points_after = np.around(points_after).astype(np.int16)
    return points_after


# 注意finger有两个点, 满足其一即可
def is_region(finger, keyboard):
    if finger == (None, None):
        return random.choice[True, False]

    for eachone in finger:
        if eachone is not None:
            (x, y) = eachone
            d = 3
            if keyboard[0][0] - d <= x <= keyboard[1][0] + d and \
                    keyboard[1][1] - d <= y <= keyboard[2][1] + d:
                return True
    return False


def right_wrong(result, this_key, finger):
    # 根据key，在对应键盘按键上添加色块
    keyboard = cv2.imread('right_wrong/' + 'keyboard.png', cv2.IMREAD_UNCHANGED)
    # 读取csv
    df = pd.read_csv('./biaozhu/keyboard_layout2.csv', index_col=0)
    keyboard_x1 = df.to_dict('dict')['x1']
    keyboard_y1 = df.to_dict('dict')['y1']
    keyboard_x2 = df.to_dict('dict')['x2']
    keyboard_y2 = df.to_dict('dict')['y2']
    for key in keyboard_x1.keys():
        if str(key).lower() == str(this_key).lower():
            minx, maxx = map(int, [keyboard_x1[key], keyboard_x2[key]])
            miny, maxy = map(int, [keyboard_y1[key], keyboard_y2[key]])
            break

    # 正确显示绿色，错误显示红色
    if result == 1:
        d_color = [0, 255, 0, 1]
    else:
        d_color = [0, 0, 255, 1]

    line_width = [i for i in range(-1, 30)]
    for i in range(minx, maxx):
        for width in line_width:
            keyboard[miny + width, i] = np.array(d_color)
            keyboard[maxy - width, i] = np.array(d_color)

    for i in range(miny, maxy):
        for width in line_width:
            keyboard[i, minx + width] = np.array(d_color)
            keyboard[i, maxx - width] = np.array(d_color)

    if result == 1:
        pic_name = 'right' + str(finger) + '.png'
    else:
        pic_name = 'wrong' + str(finger) + '.png'
    hand = cv2.imread('./right_wrong/' + pic_name, cv2.IMREAD_UNCHANGED)
    res_img = merge_img(keyboard, hand, 0, hand.shape[0], 0, hand.shape[1])

    text_result = ['错误', '正确']
    text = "当前按下的是" + str(key).lower() + ', 指法' + text_result[result]
    text_finger = ['左手小指', '左手无名指', '左手中指', '左手食指', '左手拇指', '右手拇指', '右手食指', '右手中指', '右手无名指', '右手小指']
    if result == 0:
        text += "，应该用" + text_finger[finger - 1]
    text += '。'
    return res_img, text


def check_gesture(key, keyboard, hands_points):
    key = key.lower()
    flag = 0
    if len(hands_points) < 2:
        img = cv2.imread('right_wrong/origin.png')
        return img, '未检测到两只手'

    for i in range(21):
        if hands_points[0][i] is not None and hands_points[1][i] is not None:
            if hands_points[0][i][0] < hands_points[1][i][0]:
                flag += 1
            else:
                flag -= 1
    if flag > 0:
        left_hand, right_hand = hands_points[0], hands_points[1]
    else:
        left_hand, right_hand = hands_points[1], hands_points[0]

    lmuzhi, lshizhi, lzhongzhi, lwumingzhi, lxiaozhi = (left_hand[4], left_hand[20]), (left_hand[8], left_hand[16]), \
                                                       (left_hand[12], left_hand[12]), (left_hand[16], left_hand[8]), \
                                                       (left_hand[20], left_hand[4])
    rmuzhi, rshizhi, rzhongzhi, rwumingzhi, rxiaozhi = (right_hand[4], right_hand[20]), (right_hand[8], right_hand[16]), \
                                                       (right_hand[12], right_hand[12]), \
                                                       (right_hand[16], right_hand[8]), \
                                                       (right_hand[20], right_hand[4])

    if key == 'shift':
        if is_region(lxiaozhi, keyboard['l shift']):
            img, text = right_wrong(1, key, 1)
            return img, text
        elif is_region(rxiaozhi, keyboard['r shift']):
            return right_wrong(1, key, 10)
        else:
            img, text = right_wrong(0, key, 1)
            return img, text
    elif key == 'ctrl':
        if is_region(lxiaozhi, keyboard['l ctrl']):
            return right_wrong(1, key, 1)
        elif is_region(rxiaozhi, keyboard['r ctrl']):
            return right_wrong(1, key, 10)
        else:
            return right_wrong(0, key, 1)
    elif key == 'win':
        if is_region(lxiaozhi, keyboard['l win']):
            return right_wrong(1, key, 1)
        elif is_region(rwumingzhi, keyboard['r win']):
            return right_wrong(1, key, 9)
        else:
            return right_wrong(0, key, 1)
    elif key == 'alt':
        if is_region(lwumingzhi, keyboard['l alt']):
            return right_wrong(1, key, 2)
        elif is_region(rzhongzhi, keyboard['r alt']):
            return right_wrong(1, key, 8)
        else:
            return right_wrong(0, key, 2)
    elif key in mz:
        if is_region(lmuzhi, keyboard[key]) or is_region(rmuzhi, keyboard[key]):
            return right_wrong(1, key, 6)
        else:
            return right_wrong(0, key, 6)
    elif key in sz_left:
        if is_region(lshizhi, keyboard[key]):
            return right_wrong(1, key, 4)
        else:
            return right_wrong(0, key, 4)
    elif key in sz_right:
        if is_region(rshizhi, keyboard[key]):
            img, text = right_wrong(1, key, 7)
            return img, text
        else:
            return right_wrong(0, key, 7)
    elif key in zz_left:
        if is_region(lzhongzhi, keyboard[key]):
            return right_wrong(1, key, 3)
        else:
            return right_wrong(0, key, 3)
    elif key in zz_right:
        if is_region(rzhongzhi, keyboard[key]):
            return right_wrong(1, key, 8)
        else:
            return right_wrong(0, key, 8)
    elif key in wmz_left:
        if is_region(lwumingzhi, keyboard[key]):
            return right_wrong(1, key, 2)
        else:
            return right_wrong(0, key, 2)
    elif key in wmz_right:
        if is_region(rwumingzhi, keyboard[key]):
            return right_wrong(1, key, 9)
        else:
            return right_wrong(0, key, 9)
    elif key in xz_left:
        if is_region(lxiaozhi, keyboard[key]):
            img, text = right_wrong(1, key, 1)
            return img, text
        else:
            img, text = right_wrong(0, key, 1)
            return img, text
    elif key in xz_right:
        if is_region(rxiaozhi, keyboard[key]):
            return right_wrong(1, key, 10)
        else:
            return right_wrong(0, key, 10)
    pass
