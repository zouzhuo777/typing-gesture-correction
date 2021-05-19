import cv2
import numpy as np

def add_alpha_channel(img):
    """ 为jpg图像添加alpha通道 """

    b_channel, g_channel, r_channel = cv2.split(img) # 剥离jpg图像通道
    alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255 # 创建Alpha通道

    img_new = cv2.merge((b_channel, g_channel, r_channel, alpha_channel)) # 融合通道
    return img_new

def merge_img(jpg_img, png_img, y1, y2, x1, x2):
    """ 将png透明图像与jpg图像叠加
        y1,y2,x1,x2为叠加位置坐标值
    """

    # 判断jpg图像是否已经为4通道
    if jpg_img.shape[2] == 3:
        jpg_img = add_alpha_channel(jpg_img)

    yy1 = 0
    yy2 = png_img.shape[0]
    xx1 = 0
    xx2 = png_img.shape[1]

    if x1 < 0:
        xx1 = -x1
        x1 = 0
    if y1 < 0:
        yy1 = - y1
        y1 = 0
    if x2 > jpg_img.shape[1]:
        xx2 = png_img.shape[1] - (x2 - jpg_img.shape[1])
        x2 = jpg_img.shape[1]
    if y2 > jpg_img.shape[0]:
        yy2 = png_img.shape[0] - (y2 - jpg_img.shape[0])
        y2 = jpg_img.shape[0]

    alpha_png = png_img[yy1:yy2,xx1:xx2,3] / 255.0
    alpha_jpg = 1 - alpha_png

    # 开始叠加
    for c in range(0,3):
        jpg_img[y1:y2, x1:x2, c] = ((alpha_jpg*jpg_img[y1:y2,x1:x2,c]) + (alpha_png*png_img[yy1:yy2,xx1:xx2,c]))

    res = []
    for i in jpg_img:
        res1 = []
        for j in i:
            tmp = j[:3]
            res1.append(tmp)
        res.append(res1)
    return np.array(res)



