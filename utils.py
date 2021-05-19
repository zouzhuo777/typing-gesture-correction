# coding=utf-8
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random


def cv2ImgAddText(img, text, left, top, textColor=(0, 255, 0), textSize=20):
    # 实现cv2中文输出
    if isinstance(img, np.ndarray):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontText = ImageFont.truetype(
        "font/simsun.ttc", textSize, encoding="utf-8")
    draw.text((left, top), text, textColor, font=fontText)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


def plot_one_box(x, img, color=None, label=None, line_thickness=None):
    # 将xyxy的矩形绘制在图像上
    # 例子：plot_one_box(xyxy, img_, label=label, color=(0,175,255), line_thickness = 2)
    tl = line_thickness or round(0.002 * max(img.shape[0:2])) + 1  # line thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(img, c1, c2, color, thickness=tl)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(img, c1, c2, color, -1)  # filled
        cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3, [255, 55,90], thickness=tf, lineType=cv2.LINE_AA)


def bbox_xy(result):
    # bbox整理为角点形式，并扩大一定的像素大小
    bbox_point = []
    for i in result:
        if i['score'] < 0.5:
            continue
        tmp = i['bbox']
        delta = 50
        tmp_list = list(map(int, [tmp[0]-delta, tmp[1]-delta, tmp[0] + tmp[2] + delta, tmp[1] + tmp[3] + delta]))
        for j in range(len(tmp_list)):
            if j % 2 == 0:
                # 要考虑边界是否超出
                tmp_list[j] = sorted([0, 640, tmp_list[j]])[1]
            else:
                tmp_list[j] = sorted([0, 480, tmp_list[j]])[1]
        bbox_point.append(tmp_list)
    # print(bbox_point)
    return bbox_point

