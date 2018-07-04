# -*- coding: utf-8 -*-

import os
import glob

#PATH = "C:\\Users\\Takumi\\PycharmProjects\\OWLIFT\\image_data\\right_or_left\\distance_test\\"
PATH = "C:\\Users\\Takumi\\PycharmProjects\\OWLIFT\\image_data\\lie\\1120_lie4m\\"
#PATH = "C:\\Users\\Takumi\\PycharmProjects\\OWLIFT\\image_data\\right_or_left\\"
#PATH = "C:\\Users\\Takumi\\PycharmProjects\\OWLIFT\\image_data\\17_11_20\\distance_test\\"
#folder = "l2m6m"
#"""
#---------複数フォルダ-----------------

folders = os.listdir(PATH)
print(folders)

i = 30

for folder in folders:

    #imgs = glob.glob(PATH+folder+'\\*')
    #os.rename(PATH+folder, PATH+'{0:04d}'.format(i))
    os.rename(PATH + folder, PATH + folder + '_1120_lie_4m')
    #for img in imgs:
        #os.rename(img, img[:-7] + img[-5:])
        #os.rename(img, PATH+folder+'\\{0:04d}.png'.format(i))
    i += 1
"""
#-----------------------------------------

imgs = glob.glob(PATH+folder+'\\*')
i =2000
for img in imgs:
    os.rename(img, PATH+folder+'\\%04d.png'%(i))
    i += 1

"""