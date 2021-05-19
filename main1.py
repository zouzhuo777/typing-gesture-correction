# coding=utf-8
import paddlex as pdx
import numpy as np
import matplotlib.pyplot as plt
from ppqi import InferenceModel
import time
import os
from gesture import *
from actual_keyboard import *
from utils import *

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'


class general_pose_model(object):
    # 初始化
    def __init__(self, modelpath):
        self.num_points = 21
        self.inHeight = 368
        self.threshold = 0.1
        self.point_pairs = [[0, 1], [1, 2], [2, 3], [3, 4],
                            [0, 5], [5, 6], [6, 7], [7, 8],
                            [0, 9], [9, 10], [10, 11], [11, 12],
                            [0, 13], [13, 14], [14, 15], [15, 16],
                            [0, 17], [17, 18], [18, 19], [19, 20]]

        self.model = InferenceModel(
            modelpath=modelpath,
            use_gpu=True,
            use_mkldnn=False
        )
        self.model.eval()

    # 模型推理预测
    def predict(self, img_cv2):
        # 图像预处理
        img_height, img_width, _ = img_cv2.shape
        aspect_ratio = img_width / img_height
        inWidth = int(((aspect_ratio * self.inHeight) * 8) // 8)
        inpBlob = cv2.dnn.blobFromImage(img_cv2, 1.0 / 255, (inWidth, self.inHeight), (0, 0, 0), swapRB=False,
                                        crop=False)

        # 模型推理
        output = self.model(inpBlob)

        # 可视化热力图
        # self.vis_heatmaps(imgfile, output)

        # 关键点计算
        points = []
        for idx in range(self.num_points):
            # confidence map
            probMap = output[0, idx, :, :]
            probMap = cv2.resize(probMap, (img_width, img_height))

            # Find global maxima of the probMap.
            minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

            if prob > self.threshold:
                points.append((int(point[0]), int(point[1])))
            else:
                points.append(None)

        return points

    # 手部姿势可视化函数
    def vis_pose(self, img_cv2, points):
        img_cv2_copy = np.copy(img_cv2)
        for idx in range(len(points)):
            if points[idx]:
                # 实际位置，要加上基点坐标
                res = (points[idx][0], points[idx][1])
                cv2.circle(img_cv2_copy, res, 8, (0, 255, 255), thickness=-1,
                           lineType=cv2.FILLED)
                cv2.putText(img_cv2_copy, "{}".format(idx), res, cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 2, lineType=cv2.LINE_AA)

        # 画骨架
        for pair in self.point_pairs:
            partA = pair[0]
            partB = pair[1]
            if points[partA] and points[partB]:
                resA = (points[partA][0], points[partA][1])
                resB = (points[partB][0], points[partB][1])
                cv2.line(img_cv2, resA, resB, (0, 255, 255), 3)
                cv2.circle(img_cv2, resA, 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)

        return img_cv2


# 这是一个针对图像层面处理的class，视频层面封装在gui了
class main_project:
    def __init__(self):
        # 初始化读取模型
        yolov3_modelpath = 'yolov3_inference_model'
        self.predictor = pdx.deploy.Predictor(yolov3_modelpath, use_gpu=True, gpu_id=0)
        modelpath = "openpose_pd_model/inference_model"
        self.pose_model = general_pose_model(modelpath)

        # 上一个键盘输入的ascii码
        self.last_input = -1
        # 是否按下了按钮，新判定一次，否则继续输出上次的结果
        self.refresh_flag = False
        self.M = np.array([])

    def draw_hands(self, image):
        # 输入图像，根据self.bbox_point绘制叠加在图像上的显示图像
        for bbox in self.bbox_point:
            plot_one_box(bbox, image, label='Hand', color=(0, 175, 255), line_thickness=2)
        return image

    def check_hands(self, image):
        # 输入图像，两只手在图像中的坐标，赋给self中的bbox_point
        result = self.predictor.predict(image)
        self.bbox_point = bbox_xy(result)
        # print('手部检测完成')

    def draw_hands_points(self, image):
        # 输入图像，根据self中保存的hands_points绘制叠加在图像上的显示图像
        assert (len(self.bbox_point) == len(self.hands_points))
        for i in range(len(self.bbox_point)):
            res_points = self.hands_points[i]
            # 展示手部标注点
            self.pose_model.vis_pose(image, res_points)

        return image

    def check_hands_points(self, image):
        # 输入图像，根据self中两只手的坐标，返回手的关键点的坐标，也赋给self中的hands_points
        hands_points = []
        for bbox in self.bbox_point:
            one_hand = image[bbox[1]:bbox[3], bbox[0]:bbox[2], :]
            start = time.time()
            res_points = self.pose_model.predict(one_hand)
            base_point = (bbox[0], bbox[1])
            for idx in range(len(res_points)):
                if res_points[idx]:
                    # 实际位置，要加上基点坐标
                    res = (res_points[idx][0] + base_point[0], res_points[idx][1] + base_point[1])
                    res_points[idx] = res
            # print(res_points)
            # print("openpose Model predicts time: ", time.time() - start)
            # 展示手部标注点
            # pose_model.vis_pose(one_hand, res_points)
            hands_points.append(res_points)
        self.hands_points = hands_points
        # print('手部关键点识别完成')

    def draw_keyboard(self, image):
        # 输入图像，返回根据self.M绘制叠加在图像上的显示图像
        # 生成透视变换之后的图片
        img1 = cv2.imread('./biaozhu/pic/standard_keyboard.jpg')
        img1 = cv2.warpPerspective(img1, self.M, (640, 480))
        # 　叠加图层显示
        image = cv2.addWeighted(img1, 0.4, image, 0.6, 50)
        return image

    def check_keyboard(self, image):
        # 输入图像，返回每个按键在图像的坐标，也赋给self中的keys_coordinate
        angle = line_detection(image)
        rotate_img, reverseMatRotation = rotate(image, angle)
        point_list, text = line(rotate_img, reverseMatRotation)
        if text == '':
            # 获得标准键盘图像到实际键盘图像的映射矩阵
            self.M = get_M(point_list[0])

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
                tmp_actual = trans_points(tmp_points, self.M)
                keyboard_actual[str(key).lower()] = tmp_actual

            self.keyboard_actual = keyboard_actual

            return '键盘检测完成'
        else:
            return text

    def gesture_correction(self, image):
        # 在检测到按键输入时触发，根据键盘按键坐标和手的关键点位置判别，输出纠正
        print('进行纠正，当前按键:', self.last_input)
        return check_gesture(self.last_input, self.keyboard_actual, self.hands_points)


if __name__ == '__main__':
    hand_imgname = 'image_test/s2.jpg'
    hand_img = cv2.imread(hand_imgname)
    test = main_project()
    time.sleep(10)
    t1 = time.time()
    test.check_hands(hand_img)
    t2 = time.time()
    print(t2 - t1)
    #
    # t1 = time.time()
    # test.check_hands_points(hand_img)
    # t2 = time.time()
    # print(t2 - t1)

    hand_img = test.draw_hands(hand_img)
    cv2.imshow('img', hand_img)
    cv2.waitKey(0)
    print('ok')
