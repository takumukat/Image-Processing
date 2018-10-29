# coding: utf-8

import os
import array
import numpy as np
from PIL import Image
import tifffile

import read_raw


class HDRrendering(object):
    def __init__(self,expRatio, expLine, threshold='0xffe'):
        self.ratio = expRatio
        self.line = expLine
        self.th = int(threshold,0)
        self.width = 1920
        self.height = 1080
        print('\nexpRatio: {}   ofset: {}   threshold: {}'.format(self.ratio, self.line, self.th))


    def readME(self, path):
        dummy = 10
        ofset = self.line
        numOfPixel = int(os.path.getsize(path) / 2)

        data = array.array('H')  # 'H': unsigned short (2byte)

        f = open(path, 'rb')
        data.fromfile(f, numOfPixel)
        f.close()

        raw = np.array(data).reshape(1390, 3840)

        raw0 = raw[dummy:dummy+self.height, 0:self.width]
        raw1 = raw[dummy+ofset:dummy+ofset+self.height, self.width:self.width*2]

        return raw0, raw1



    def separateColor(self, rawMatrix):
        # ベイヤー配列
        # R:偶数行，奇数列
        # Gr:偶数行，偶数列        Gr | R
        # Gb:奇数行，奇数列        ------
        # B:奇数行，偶数列         B  | Gb

        gr = rawMatrix[0::2, 0::2]
        gb = rawMatrix[1::2, 1::2]
        r = rawMatrix[0::2, 1::2]
        b = rawMatrix[1::2, 0::2]

        GrGbRBarray = np.array([gr, gb, r, b])

        return GrGbRBarray


    def checkSaturation(self, GrGbRBarray):
        #閾値より大きい-->False
        boolean = ~(GrGbRBarray > self.th)
        tint0area = boolean[0] & boolean[1] & boolean[2] & boolean[3]

        # --------------大きさを戻す-------------
        tint0areaImg = Image.fromarray(tint0area, 'L')
        tint0areaImg = tint0areaImg.resize((self.width, self.height), Image.NEAREST)
        tint0area = np.array(tint0areaImg)

        # さちった部分を可視化
        """
        thimg = np.zeros((int(self.height), int(self.width)))
        thimg[tint0area == False] = 255  # 閾値越え-->白
        thImg = Image.fromarray(thimg)
        thImg.show()
        """
        return tint0area

    def convert8bit(self, img16bit):
        MAX = img16bit.max()
        MIN = img16bit.min()

        img8bit = ( (img16bit-MIN) / (MAX-MIN) ) * (2**8-1)

        return np.uint8(img8bit)


    def showTint0(self, raw0, tint0area):
        # tint0エリアだけ表示
        rgb = read_raw.rgb(raw0)

        thimg = np.zeros((int(self.height), int(self.width)))

        thimg[tint0area == True] = raw0[tint0area == True]
        img = self.convert8bit(rgb)
        thImg = Image.fromarray(img, 'RGB')
        thImg.show()


    def rendering(self, raw_0, raw_1, tint0area):
        raw0 = raw_0.astype(np.float32)
        raw1 = raw_1.astype(np.float32)
        raw0[tint0area == False] = raw1[tint0area == False]*self.ratio

        #16bitに正規化
        #MIN = raw0.min()
        #MAX = raw0.max()
        #raw0 = ( (raw0-MIN) / (MAX-MIN) ) * (2**16-1)

        return np.uint16(raw0)



    def renderingKai(self, raw0, raw1, tint0area):
        #色で分ける
        tint1 = self.separateColor(raw1)
        tint1 = np.float32(tint1)
        #露光比をかける
        tint1 *= self.ratio

        #掛けたときのbayer単位(4個単位)での最大値
        maxArray = tint1.max(axis=0)

        #最大値が4095をこえているところをマーク
        maxBoolean = np.zeros([int(self.height / 2), int(self.width / 2)])
        maxBoolean[maxArray > 4095] = True

        #こえているところはmaxで割って4095をかけて色が変わらないよう正規化
        tint1[0][maxBoolean == True] /= maxArray[maxBoolean == True]
        tint1[1][maxBoolean == True] /= maxArray[maxBoolean == True]
        tint1[2][maxBoolean == True] /= maxArray[maxBoolean == True]
        tint1[3][maxBoolean == True] /= maxArray[maxBoolean == True]
        tint1 *= 4095

        #色ごと960*540*4  --> 1枚1920*1080
        tint1Canvas = np.zeros([self.height, self.width])
        tint1Canvas[0::2, 0::2] = tint1[0]
        tint1Canvas[1::2, 1::2] = tint1[1]
        tint1Canvas[0::2, 1::2] = tint1[2]
        tint1Canvas[1::2, 0::2] = tint1[3]


        raw0[tint0area == False] = tint1Canvas[tint0area == False]

        return np.uint16(raw0)


    def __call__(self, path, renderMode=0):
        raw0, raw1 = self.readME(path)
        GrGbRB0 = self.separateColor(raw0)

        tint0area = self.checkSaturation(GrGbRB0)
        #self.showTint0(raw0, tint0area)

        if renderMode == 0:
            hdr = self.rendering(raw0, raw1, tint0area)
        else:
            hdr = self.renderingKai(raw0, raw1, tint0area)

        return hdr



def saveTiff(img, name):
    MIN = img.min()
    MAX = img.max()

    image = ((img.astype(np.float32) - MIN) / (MAX - MIN)) * (2 ** 16 - 1)
    img16bit = image.astype(np.uint16)

    tifffile.imsave(name, img16bit, dtype='uint16')



def saveImg(img, name):
    image = Image.fromarray(img)
    #image.show()
    image.save(name, 'PNG')
    print('save  '+name)



def main():
    exp1 = np.array([160,2186,2186])
    exp2 = np.array([4,68,68])

    path = 'sample\\testME2\\'
    name = ['me20180903_122145_0000.raw', 'me20180903_182506_0000.raw', 'MEHDR20180903_211819_0415.raw']

    expRatio = (exp1 / exp2).astype(np.int8)
    expLine = exp2


    for i in range(len(name)):
        render = HDRrendering(expRatio[i], expLine[i], threshold='0xffe')

        #Mode{0:普通   Not0:改}
        hdr = render(path+name[i], renderMode=0)
        rgb = read_raw.rgb(hdr)

        saveTiff(rgb, path+name[i][:-4]+'.tif')
        img = render.convert8bit(rgb)

        saveImg(img, path+name[i][:-4]+'.png')





if __name__ == '__main__':
    main()
