# coding: utf-8

import numpy as np
import array
import argparse
import cv2
import os
import sys

from PIL import Image
import matplotlib.pyplot as plt



#rawデータを2bytesずつに区切った配列を返す
def readTwoBytes(path):

    numOfPixel = os.path.getsize(path) / 2   #number of pixel
    data = array.array('H')   #'H': unsigned short (2byte)

    f = open(path, 'rb')
    data.fromfile(f, numOfPixel)
    f.close()

    raw = np.array(data)

    return raw



#ベイヤー配列4つ分を1画素として1/4サイズのRGB画像を返す
def rgb_q(raw):
    height = raw.shape[0]
    width = raw.shape[1]

    #ベイヤー配列
    #R:偶数行，奇数列
    #G0:偶数行，偶数列        G | R
    #G1:奇数行，奇数列        -----
    #B:奇数行，偶数列         B | G

    r = raw[0::2, 1::2]

    g0 = raw[0::2, 0::2]
    g1 = raw[1::2, 1::2]
    g = (g0 + g1) / 2.0

    b = raw[1::2, 0::2]

    img = np.array([r,g,b]).astype(np.float32)
    img /= img.max()

    return img


#OpenCVのcvtColorで色付け，出力サイズ=入力サイズ
def rgb(raw):
    raw = np.uint16(raw)  # cvtColorはuint8かuint16
    #cvtColor: GBベイヤー配列 -> RGB
    img = cv2.cvtColor(raw, cv2.COLOR_BAYER_GB2RGB)  # [[[RGB],[]...
    img = img.astype(np.float32)
    img /= img.max()

    return img



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str)
    parser.add_argument('--movie', action='store_true')
    parser.add_argument('--path')
    args = parser.parse_args()

    # SDR, SEHDR: 1920x1090   MEHDR: 3840x1390
    if args.mode == 'SDR' or args.mode == 'SE':
        width = 1920
        height = 1090
    elif args.mode == 'ME':
        width = 1920 * 2
        height = 1390
    else:
        sys.exit()

    raw = readTwoBytes(args.path)

    #画像1枚のとき
    if args.movie is False:
        raw = raw.reshape(height, width)  # 画像の形に変える
        raw = raw[10:]   #上から10行は真っ黒
        img = rgb(raw)

    #動画のとき
    else:
        n = int(len(raw) / width / height)   #画像何枚分の動画か
        raw = raw.reshape(n, height, width)
        raw = raw[:, 10:, :]   #上から10行は真っ黒
        dark = raw[:, 0:1080, 0:1920]   #MEの暗部,SE,SDR
        bright = raw[:, 30:1110, 1920:3840]   #MEの明部

        d_imgs = []   #darkの動画
        b_imgs = []   #brightの動画
        for i in range(n):
            d_imgs.append(rgb(dark[i]))
            b_imgs.append(rgb(bright[i]))

        d_imgs = np.array(d_imgs)
        b_imgs = np.array(b_imgs)




if __name__ == '__main__':
    main()
