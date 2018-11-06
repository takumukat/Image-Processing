# coding: utf-8

import numpy as np
import array
import argparse
import cv2
import os
from PIL import Image



#width, height, bit depthを返す
def modeCheck(mode):
    # SDR, SEHDR: 1920x1090   MEHDR: 3840x1390
    if mode == 'SDR':
        width = 1920
        height = 1090
        bit = 12
    elif mode == 'SE':
        width = 1920
        height = 1090
        bit = 16
    elif mode == 'ME':
        width = 3840
        height = 1390
        bit = 12
    else:
        width = None
        height = None
        bit = None
    print('mode: "{}"   bit depth: "{}"'.format(mode, bit))

    return width, height, bit


#rawデータを2bytesずつに区切った配列を返す
def readTwoBytes(path):

    numOfPixel = int(os.path.getsize(path) / 2)   #number of pixel
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

    return img


#OpenCVのcvtColorで色付け，出力サイズ=入力サイズ
def rgb(raw):
    raw = np.uint16(raw)  # cvtColorはuint8かuint16
    #cvtColor: GBベイヤー配列 -> RGB
    img = cv2.cvtColor(raw, cv2.COLOR_BAYER_GB2RGB)  # [[[RGB],[]...

    return img



# 静止画: SDR, SE:1枚を入れた配列，ME:2枚を入れた配列  (値は0~2**bit-1)
def rawReader(path, mode, ofset=None):

    width, height, bit = modeCheck(mode)
    print('width: {}   height: {}\n'.format(width, height))


    raw = readTwoBytes(path)

    raw = raw.reshape(height, width)  # 画像の形に変える
    raw = raw[10:]   #上から10行は真っ黒

    if mode == 'ME':
        print('ofset: {}'.format(ofset))
        t0_raw = raw[0:1080, 0:1920]
        t1_raw = raw[ofset:ofset+1080, 1920:1920*2]
        print('TINT0 min: {}  max: {}'.format(t0_raw.min(), t0_raw.max()))
        print('TINT1 min: {}  max: {}\n'.format(t1_raw.min(), t1_raw.max()))

        return [t0_raw, t1_raw]

    else:
        print('minRAW: {}  maxRAW: {}\n'.format(raw.min(), raw.max()))
        return raw



def showRaw(raw):
    raw = raw.astype(np.float32)
    raw /= raw.max()
    raw *= 255.

    rawImg = Image.fromarray(raw.astype(np.uint8))
    rawImg.show()




def main():
    defImage = 'sample\\RGB_Linear\\20180713_155927.raw'
    defMode = 'SDR'

    parser = argparse.ArgumentParser()
    parser.add_argument('--path', default=defImage)
    parser.add_argument('--mode', type=str, default=defMode)
    parser.add_argument('--ofset', type=int, default=None)
    args = parser.parse_args()
    print(args)

    if args.mode == 'SDR' or args.mode == 'SE':
        raw = rawReader(args.path, args.mode)
    elif args.mode == 'ME':
        raw = rawReader(args.path, args.mode, args.ofset)
    else:
        return

    showRaw(raw)



if __name__ == '__main__':
    main()
