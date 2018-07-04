# -*- coding: utf-8 -*-

import numpy as np
import copy
import os
import sys
import cv2

WIDTH = 80
HEIGHT = 60
INPUT_PATH = "/home/pi/IRcamera/out/"
OUTPUT_PATH = "/home/pi/IRcamera/img/"


def decode(data):               
    imlist = data.split(",")
    imlist = imlist[0:WIDTH*HEIGHT]
    val = [int(p) for p in imlist]    #val:[0.01Kelvin]
                
    ary = np.array(val)
    ary = ary*0.01
    #ary = ary*0.01-273.15    #0.01*ary[Kelvin] - 273.15 --> [Celsius] 

    return(ary)


def bound(data):
    border = int(WIDTH * HEIGHT * 0.01)
    #print("border:" + str(border))
    data_a = data
    data_b = copy.deepcopy(data)
    data_a.sort()

    min_border = data_a[border]
    max_border = data_a[-(border + 1)]

    for i in range(border):
        mini = np.argmin(data_b)
        maxi = np.argmax(data_b)
        data_b[mini] = min_border
        data_b[maxi] = max_border

    return (np.resize(data_b, (HEIGHT, WIDTH)))


def createimg(data):
    maxi = np.max(data)
    mini = np.min(data)
    slope = (maxi - mini) / 255
    img = np.zeros([HEIGHT, WIDTH])
    j = 0
    for line in data:
        i = 0
        for val in line:
            if val == mini:
                img[j][i] = 0
            elif val == maxi:
                img[j][i] = 255
            else:
                img[j][i] = int((val - mini) / slope)
            i += 1
        j += 1

    return (img)


def main():
    try:
        files = os.listdir(INPUT_PATH)
    except:
        print("no folder")
        sys.exit()
    
    for f in files:
        i = 0
        csv = open(INPUT_PATH+f)
        lines = csv.readlines()
        csv.close()

        try:
            os.mkdir(OUTPUT_PATH+f[:-4])
        except:
            continue

        for line in lines:
            try:
                val = decode(line)
            except:
                print(f)
                continue

            if max(val) == 0:
                continue
            pic = bound(val)
            img = createimg(pic)
            
            cv2.imwrite(OUTPUT_PATH+f[:-4]+"/"+str('{0:03d}'.format(i))+".png",img)
            i += 1


if __name__ == '__main__':
    main()
