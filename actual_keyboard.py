# coding=utf-8
import time
import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
from copy import deepcopy
import pandas as pd
import random


def inter(x1, y1, x2, y2, y):
    return x2 - ((x2 - x1) / (y2 - y1) * (y2 - y))


def trans_points(ppoints, MM):
    points_after = np.matmul(ppoints, MM.T)
    points_after0 = np.array([points_after[:, 0] / points_after[:, 2]]).T
    points_after1 = np.array([points_after[:, 1] / points_after[:, 2]]).T
    points_after = np.hstack((points_after0, points_after1))
    points_after = np.around(points_after).astype(np.int16)
    return points_after


def get_M(point_list):
    arr = np.load('biaozhu/100%ANSI_main角点标注.npy')
    biaozhu_points = []
    for i in range(len(arr)):
        biaozhu_points.append((arr[i][0], arr[i][1], 1))
    # print(arr)
    target_points = point_list[:2] + point_list[3:] + point_list[2:3]


    ori_points = [(-15, 0), (1240, 0), (1235, 555), (-15, 555)]
    # 原图中需要变换的点们，最后一位固定是1

    ori_points, target_points = np.array(ori_points, dtype=np.float32), np.array(target_points, dtype=np.float32)
    # 透视变换矩阵
    M = cv2.getPerspectiveTransform(ori_points, target_points)
    return M


def return4point(x1, y1, x2, y2, x3, y3, x4, y4, line1, line2, reverseMatRotation):
    section1 = int(inter(x1, y1, x2, y2, line1))
    section2 = int(inter(x1, y1, x2, y2, line2))
    section3 = int(inter(x3, y3, x4, y4, line1))
    section4 = int(inter(x3, y3, x4, y4, line2))
    P1 = np.dot(reverseMatRotation, np.array([[section1], [line1], [1]]))
    P2 = np.dot(reverseMatRotation, np.array([[section2], [line2], [1]]))
    P3 = np.dot(reverseMatRotation, np.array([[section3], [line1], [1]]))
    P4 = np.dot(reverseMatRotation, np.array([[section4], [line2], [1]]))

    list = [(round(P1[0][0]), round(P1[1][0])), (round(P3[0][0]), round(P3[1][0])), (round(P2[0][0]), round(P2[1][0])),
            (round(P4[0][0]), round(P4[1][0]))]
    return list


def line_detection(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gauss = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(gauss, 50, 200)

    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, minLineLength=30, maxLineGap=5, threshold=50)
    lines1 = lines[:, 0, :]
    count = np.zeros(180)

    for x1, y1, x2, y2 in lines1:
        if x2 - x1 != 0:
            angle = math.atan((y2 - y1) / (x2 - x1)) * 180 / math.pi
        else:
            angle = 90
        if (angle < 0):
            angle = 180 + angle
        # print(angle)
        count[int(angle)] += 1

    max = 0
    index = 0
    for i in range(180):
        if (count[i] > max):
            max = count[i]
            index = i

    return index


def rotate(image, degree):
    height, width = image.shape[:2]
    heightNew = int(
        width * math.fabs(math.sin(math.radians(degree))) + height * math.fabs(math.cos(math.radians(degree))))
    widthNew = int(
        height * math.fabs(math.sin(math.radians(degree))) + width * math.fabs(math.cos(math.radians(degree))))
    matRotation = cv2.getRotationMatrix2D((width / 2, height / 2), degree, 1)
    matRotation[0, 2] += (widthNew - width) // 2
    matRotation[1, 2] += (heightNew - height) // 2

    imgRotation = cv2.warpAffine(image, matRotation, (widthNew, heightNew))
    reverseMatRotation = cv2.invertAffineTransform(matRotation)
    return imgRotation, reverseMatRotation


def line(image, reverseMatRotation):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gauss = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(gauss, 50, 200)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, minLineLength=30, maxLineGap=5, threshold=50)
    lines1 = list(lines[:, 0, :])
    # count = np.zeros(320)
    delta_pix = 4
    count = np.zeros(640 // delta_pix)

    point_list = []
    # 去掉旋转后图像的边框
    k = -1
    while k < len(lines1) - 1:
        k += 1
        x1, x2 = lines1[k][0], lines1[k][2]
        y1, y2 = lines1[k][1], lines1[k][3]
        if abs(x1 - 0) <= 5 and abs(x2 - 0) <= 5:
            lines1.pop(k)
            k -= 1
        elif abs(x1 - 640) <= 5 and abs(x2 - 640) <= 5:
            lines1.pop(k)
            k -= 1
        if abs(y1 - 0) <= 5 and abs(y2 - 0) <= 5:
            lines1.pop(k)
            k -= 1
        elif abs(y1 - 480) <= 5 and abs(y2 - 480) <= 5:
            lines1.pop(k)
            k -= 1

    # 去掉旋转前图像的边框
    k = 0
    while k < len(lines1):
        tmp = lines1[k]
        P1 = np.dot(reverseMatRotation, np.array([[tmp[0]], [tmp[1]], [1]]))
        P2 = np.dot(reverseMatRotation, np.array([[tmp[2]], [tmp[3]], [1]]))
        if (abs(P1[0][0] - 0) < 3 and abs(P2[0][0] - 0) < 3) or (abs(P2[0][0] - 640) < 3 and abs(P2[0][0] - 640) < 3):
            lines1.pop(k)
            k -= 1
        k += 1

    im = deepcopy(image)
    for x1, y1, x2, y2 in lines1:
        cv2.line(im, (x1, y1), (x2, y2), (0, 0, 255), 2)
        if math.fabs(int(y1) - int(y2)) <= 1:
            count[int(y1 // 4)] += int(math.fabs(x1 - x2))

    sum_count = sum(count)
    dict1, dict2 = {}, {}
    formeri = -100

    # 横向线筛选 、 合并横向线
    for i in range(len(count)):
        if (count[i] > sum_count * 0.025 and i - formeri >= 2):
            formeri = i
            dict1[i * 4 + 2] = count[i]
    list1 = sorted(dict1)
    if len(list1) < 3:
        return point_list, '请移动键盘！'

    # 纵向线筛选
    dict_zuo = {}
    dict_you = {}
    for x1, y1, x2, y2 in lines1:
        if x2 == x1:
            angle = 90
        else:
            angle = math.atan((y2 - y1) / (x2 - x1)) * 180 / math.pi
        if (angle < 0):
            angle = 180 + angle
        # print(angle)
        if (((y1 + y2) / 2) < list1[0]) or (((y1 + y2) / 2) > list1[-1]):
            continue
        elif (int(angle) > 20) and (int(angle) < 160):
            if (x1 + x2) < image.shape[0]:
                dict_zuo[(x1 + x2) / 2] = (x1, y1, x2, y2)
            else:
                dict_you[(x1 + x2) / 2] = (x1, y1, x2, y2)

    list_zuo = sorted(dict_zuo)
    list_you = sorted(dict_you, reverse=True)

    former = -100
    # 合并纵向线
    k = 0
    while k < len(list_zuo):
        if list_zuo[k] - former < 4:
            del list_zuo[k]
            continue
        else:
            former = list_zuo[k]
            k += 1

    if len(list_zuo) < 1 or len(list_you) < 1:
        return point_list, '请移动键盘！'

    (x1, y1, x2, y2) = dict_zuo[list_zuo[0]]
    (x3, y3, x4, y4) = dict_you[list_you[0]]

    point_list.append(return4point(x1, y1, x2, y2, x3, y3, x4, y4, list1[2], list1[-1], reverseMatRotation))

    return point_list, ''


def get_actual_keyboard(imgname):
    img = cv2.imread(imgname)

    angle = line_detection(img)
    # print(angle)
    rotate_img, reverseMatRotation = rotate(img, angle)
    point_list = line(rotate_img, reverseMatRotation)

    # 获得标准键盘图像到实际键盘图像的映射矩阵
    M = get_M(point_list[0])

    df = pd.read_csv('./biaozhu/keyboard_layout.csv', index_col=0)
    keyboard_layout = {}
    keyboard_x1 = df.to_dict('dict')['x1']
    keyboard_y1 = df.to_dict('dict')['y1']
    keyboard_x2 = df.to_dict('dict')['x2']
    keyboard_y2 = df.to_dict('dict')['y2']
    for key in keyboard_x1.keys():
        keyboard_layout[key] = ((keyboard_x1[key], keyboard_y1[key]), (keyboard_x2[key], keyboard_y1[key]),
                                (keyboard_x2[key], keyboard_y2[key]), (keyboard_x1[key], keyboard_y2[key]))
    keyboard_actual = {}
    for key in keyboard_layout.keys():
        t_points = keyboard_layout[key]
        tmp_points = []
        # 需要添加一维才能进行透视变换
        for i in range(4):
            tmp_points.append((t_points[i][0], t_points[i][1], 1))
        tmp_actual = trans_points(tmp_points, M)
        keyboard_actual[str(key).lower()] = tmp_actual

    # 打印实际键盘布局点

    for i in keyboard_actual.values():
        for each in i:
            cv2.circle(img, tuple(each), 1, (255, 0, 0), thickness=2)
    cv2.imshow('actual', img)
    cv2.waitKey(0)
    # print(keyboard_actual)

    return keyboard_actual


if __name__ == '__main__':
    actual = get_actual_keyboard('image_test/1.jpg')
