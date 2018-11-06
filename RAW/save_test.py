# coding: utf-8

import os
import numpy as np
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import tifffile
import array

import readRaw
from histAugment import HistAugment

def sdr():
    path = 'driving\\0903_1_SDR\\SDR20180903_111911\\'
    name = 'SDR20180903_111911_0000.raw'
    mode = 'SDR'
    w, h, bit = readRaw.modeCheck(mode)

    img = readRaw.rawReader(path+name, mode)

    readRaw.show(img, mode)


    # 横 x 縦 x RGB3枚  (ヒストグラム調整用)
    img_3ch = img[0].transpose(2, 0, 1)
    # ヒストグラム拡張
    aug = HistAugment(mode)
    newImg_3ch = aug.hist_augment(img_3ch)
    print(newImg_3ch.max())
    readRaw.show([newImg_3ch.transpose(1,2,0)], mode)

    d = (2**bit-1)/(2**8-1)
    newImg = newImg_3ch.transpose(1,2,0)
    newImg /= d
    print(newImg.max())


    pilImg = Image.fromarray(np.uint8(newImg))
    pilImg.show()

    # opencv用にRGB->BGRにする
    #tmp = newImg_3ch[0].copy()
    #newImg_3ch[0] = newImg_3ch[2]
    #newImg_3ch[2] = tmp
    imgCV = cv2.cvtColor(np.uint8(newImg), cv2.COLOR_RGB2BGR)

    cv2.imshow('aug', newImg_3ch.transpose(1,2,0))
    cv2.waitKey(0)
    cv2.destroyAllWindows()




def meHDR():
    mode = 'ME'
    ofset = 4
    path = 'sample\\testME2\\'
    name = 'me20180903_122145_0000.raw'
    output = 'sample\\testME2\\ws2\\'

    imgs = readRaw.rawReader(path+name, mode, ofset)
    d_img, b_img = imgs
    #readRaw.showRaw(b_img)

    #d_img -= 256
    #b_img -= 256
    #d_img[d_img < 0] = 0
    #b_img[b_img < 0] = 0
    d_max = d_img.max()
    b_max = b_img.max()
    d_min = d_img.min()
    b_min = b_img.min()

    d_img = ( (d_img.astype(np.float32) - d_min) / (d_max-d_min) ) * (2 ** 16 - 1)
    b_img = ( (b_img.astype(np.float32) - b_min) / (b_max-b_min) ) * (2 ** 16 - 1)
    d_img = d_img.astype(np.uint16)
    b_img = b_img.astype(np.uint16)



    d_name = output + name[:-4] + '_d_.tif'
    b_name = output + name[:-4] + '_b_.tif'

    # 横 x 縦 x RGB3枚  (ヒストグラム調整用)
    # img_3ch = d_img.transpose(2, 0, 1)
    # ヒストグラム拡張
    # newImg_3ch = aug.hist_augment(img_3ch)

    # ---------------- save "tiff" -----------
    tifffile.imsave(d_name, d_img, dtype='uint16')
    tifffile.imsave(b_name, b_img, dtype='uint16')

    # --------------- save raw ---------------
    # rawfile = open(nameRaw, 'wb')
    # rawfile.write(bytearray(data))
    # rawfile.close()



def seHDR(path):

    #path = 'driving\\0903_1_SE-HDR\\'+p
    print(path)
    names = sorted(os.listdir(path))

    mode = 'SE'
    w, h, bit = readRaw.modeCheck(mode)
    print('width: {}   height: {}'.format(w,h))


    out = path.split('_raw')[0] + '_tiff\\'
    os.mkdir(out)

    for i, name in enumerate(names):
        raw = readRaw.readTwoBytes(path+name)

        raw = raw.reshape(h, w)  # 画像の形に変える
        raw = raw[10:]

        rgb = readRaw.rgb(raw)

        nameTiff = name[:-4] + '.tif'
        tifffile.imsave(out+nameTiff, rgb, dtype='uint16')

        print('{} / {}'.format(i+1, len(names)))


    """
    img_3ch = rgb.transpose(2, 0, 1)
    # ヒストグラム拡張
    aug = HistAugment(mode)
    newImg_3ch = aug.hist_augment(img_3ch)

    d = (2 ** bit - 1) / (2 ** 8 - 1)
    newImg = newImg_3ch.transpose(1, 2, 0)
    newImg = np.float32(newImg)
    newImg /= d
    print(newImg.max())

    pilImg = Image.fromarray(np.uint8(newImg))
    pilImg.save('a.png','PNG')
    """




def main():
    path = 'driving\\0903_2_SE-HDR\\'
    folders = sorted([f for f in  os.listdir(path) if f[-4:] == '_raw'])
    #for folder in folders:
    #    seHDR(path+folder+'\\')
    seHDR(path+folders[-1]+'\\')



if __name__ == '__main__':
    main()
