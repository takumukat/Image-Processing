# -*- coding: utf-8 -*-

import os
import glob
import numpy as np
import cv2

path = r'C:\Ritsumei\B4\fall_detection'
dirs = os.listdir(path)
#タイルを何列にするか
width = 5
#画像の縦横
imgW = 80
imgH = 60

#白線
white = np.array([255]*imgW*width)

for dir in dirs:
    imgs = sorted(glob.glob(path + '/' + dir + '/*'))
    height = int(len(imgs)/width)+int(bool(len(imgs)%width))
    #白線の分だけ余分に取っとく
    tile = np.array( [[255]*imgW*width,]*( imgH*height + height -1) )
    #タイルに入れる行を指定する変数  最初は0
    start = 0

    for j in range(height):
        #1行分の画像を入れる変数
        line = np.zeros([imgH, imgW*width])

        for i in range(width):
            try:
                img = cv2.imread(imgs[width*j + i], flags=cv2.IMREAD_GRAYSCALE)
            except:
                img = np.array([[255]*imgW,]*imgH)
            img = np.array(img)

            line[:, i*imgW:i*imgW+imgW] = img

        tile[start:start+imgH, :] = line
        #行ごとに白線を入れる
        tile[start+imgH:start+imgH+1, :] = white
        start += (imgH +1)

    cv2.imwrite(path + dir + '.png', tile)

