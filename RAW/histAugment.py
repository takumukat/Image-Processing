# coding: utf-8

import readRaw
import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image
import sys
import tifffile


class HistAugment(object):
    def __init__(self, mode, max=None):
        # SDR:12bit image  ME & SE: 16bit image
        if mode == 'SDR':
            bit = 12
        elif mode == 'SE' or mode == 'ME':
            bit = 16
        else:
            print('mode error')
            sys.exit()

        self.min = np.float32(0)
        if max == None:
            self.max = np.float32(2**bit - 1)
        else:
            self.max = np.float32(max)


    #vmax, vminを求める
    def hl(self, ch):
        #chを一直線に並べたときの長さ(ピクセル数)
        length = ch.shape[0] * ch.shape[1]
        #小さいものから順に並べる
        ch_sorted = sorted(ch.reshape(length))

        ratio = 0.05

        th_h = ch_sorted[-int(length*ratio)-1]
        th_l = ch_sorted[int(length*ratio)]

        # high = ch_sorted[-1]
        # low = ch_sorted[0]
        #return high, low

        return th_h, th_l



    # RGB3chに分けた画像を渡す
    # ヒストグラムを拡張した画像を返す
    def hist_augment(self, image):
        img = image.astype(np.float32)

        min = self.min
        max = self.max

        r, g, b = img

        hR, lR = self.hl(r)
        hG, lG = self.hl(g)
        hB, lB = self.hl(b)
        print("highR:{}, highG:{}, highB:{}".format(hR, hG, hB))
        print(" lowR:{},  lowG:{},  lowB:{}\n".format(lR, lG, lB))

        vmax = np.max([hR, hG, hB])
        vmin = np.min([lR, lG, lB])
        print("value > {} --> {}".format(vmax, max))
        print("value < {} --> {}".format(vmin, min))

        highR = highG = highB = vmax
        lowR = lowG = lowB = vmin


        r[r >= highR] = max
        r[r <= lowR] = min
        newR = np.where((r < highR) & (r > lowR), max * ((r - lowR) / (highR - lowR)), r)

        g[g >= highG] = max
        g[g <= lowG] = min
        newG = np.where((g < highG) & (g > lowG), max * ((g - lowG) / (highG - lowG)), g)

        b[b >= highB] = max
        b[b <= lowB] = min
        newB = np.where((b < highB) & (b > lowB), max * ((b - lowB) / (highB - lowB)), b)

        newImg = np.array([newR, newG, newB], dtype=np.float32)

        return newImg



def savePng(augmentedImg, outPath):
    augmentedImg /= augmentedImg.max()
    augmentedImg *= 255.
    newImg = augmentedImg.astype(np.uint8)
    Img = Image.fromarray(newImg)
    Img.save(outPath, 'PNG')





def showHistgram(beforeImg, mode, beforeHist=False, afterHist=True):
    w, h, bit = readRaw.modeCheck(mode)
    max = 2 ** bit - 1

    # 横 x 縦 x RGB3枚  (ヒストグラム調整用)
    img_3ch = beforeImg.transpose(2, 0, 1)

    n_bin = int(np.max(beforeImg))


    #----------------------------------------元の画像-------------------------------------
    if beforeHist == True:
        fig = plt.figure()
                #left,bottom,width,height
        plt.axes([0.05,0.2,0.5,0.8])
        plt.imshow(beforeImg / max)

        plt.axes([0.6,0.2,0.36,0.6])

        plt.hist(img_3ch[0].reshape(1080*1920), bins=n_bin, range=(0,max), alpha=0.4, color='r')
        plt.hist(img_3ch[1].reshape(1080*1920), bins=n_bin, range=(0,max), alpha=0.4, color='g')
        plt.hist(img_3ch[2].reshape(1080*1920), bins=n_bin, range=(0,max), alpha=0.4, color='b')

        plt.axes([0.12,0.1,0.3,0.2])
        plt.tick_params(labelbottom="off",bottom="off") # x軸の削除
        plt.tick_params(labelleft="off",left="off") # y軸の削除
        plt.box('off') # 枠を消す
        plt.text(0.35,0.85, 'min       max', fontsize=20)
        plt.text(0.35,0.7,  '{}        {}'.format(int(np.min(img_3ch[0])), int(np.max(img_3ch[0]))), color='r', fontsize=20)
        plt.text(0.35,0.55, '{}        {}'.format(int(np.min(img_3ch[1])), int(np.max(img_3ch[1]))), color='g', fontsize=20)
        plt.text(0.35,0.4,  '{}        {}'.format(int(np.min(img_3ch[2])), int(np.max(img_3ch[2]))), color='b', fontsize=20)

        plt.show()

    # -------------------------------------調整した画像--------------------------------------

    aug = HistAugment(mode=mode)
    newImg_3ch = aug.hist_augment(img_3ch)
    #plt.imshow((newImg_3ch / max).transpose(1, 2, 0))
    #plt.show()

    if afterHist == True:
        fig2 = plt.figure()

        plt.axes([0.05,0.2,0.5,0.8])
        plt.imshow((newImg_3ch / max).transpose(1,2,0))

        plt.axes([0.6,0.2,0.36,0.6])
        plt.hist(newImg_3ch[0].reshape(1080*1920), bins=n_bin, range=(0,max), alpha=0.4, color='r')
        plt.hist(newImg_3ch[1].reshape(1080*1920), bins=n_bin, range=(0,max), alpha=0.4, color='g')
        plt.hist(newImg_3ch[2].reshape(1080*1920), bins=n_bin, range=(0,max), alpha=0.4, color='b')

        plt.axes([0.12,0.1,0.3,0.2])
        plt.tick_params(labelbottom="off",bottom="off") # x軸の削除
        plt.tick_params(labelleft="off",left="off") # y軸の削除
        plt.box('off')
        plt.text(0.35,0.85, 'min       max', fontsize=20)
        plt.text(0.35,0.7,  '{}        {}'.format(int(np.min(newImg_3ch[0])), int(np.max(newImg_3ch[0]))), color='r', fontsize=20)
        plt.text(0.35,0.55, '{}        {}'.format(int(np.min(newImg_3ch[1])), int(np.max(newImg_3ch[1]))), color='g', fontsize=20)
        plt.text(0.35,0.4,  '{}        {}'.format(int(np.min(newImg_3ch[2])), int(np.max(newImg_3ch[2]))), color='b', fontsize=20)


        plt.show()




def main():
    mode = 'SE'

    path = 'driving\\0903_1_SE-HDR\\SEHDR20180903_115101_tiff\\'
    out = 'driving\\0903_1_SE-HDR\\SEHDR20180903_115101_augment\\'

    #path = 'E:\\HASHIMOTO\\0903_1_SDR\\sdr220180903_122144_me_tiff\\'
    #out = 'E:\\HASHIMOTO\\0903_1_SDR\\sdr220180903_122144_me_augment\\'

    files = os.listdir(path)
    os.mkdir(out)

    for i, file in enumerate(files):
        img = np.array(tifffile.imread(path+file), dtype=np.float32)

        img_3ch = img.transpose(2, 0, 1)

        aug = HistAugment(mode=mode)
        newImg_3ch = aug.hist_augment(img_3ch)
        newImg = newImg_3ch.transpose(1, 2, 0)

        # showHistgram(img, mode, before=True, after=True)

        outPath = out+file.split('.')[:-1]+'_aug.png'
        savePng(newImg, outPath)


        print('{} / {}\n'.format(i+1, len(files)))


if __name__ == '__main__':
    main()