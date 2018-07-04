# coding: utf-8

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import array

path = 'OneDrive_1_2018628\\20180628_161334.raw'
width = 1920
height = 1090
numOfPixel = width * height


data = array.array('h')   #'h': signed short (2byte)

file = open(path, 'rb')
data.fromfile(file, numOfPixel)
file.close()


ary = np.array(data)
ary = ary.reshape((height, width))   #画像の形に変える
#ary = np.float32(ary)

# 正規化
#ary = ary / 4095.0


plt.imshow(ary, 'gray')
plt.show()