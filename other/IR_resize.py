# -*- coding:utf-8 -*-
import os
import sys
import csv
import numpy as np
import cv2


inputpath = "IRcamera/img/"
outputpath = "IRcamera/resized_img/"
scale = 10
folderpath = os.listdir(inputpath)

for foldername in folderpath:
    files = os.listdir(inputpath+foldername)
    os.makedirs(outputpath+foldername+"_{}times/".format(scale), exist_ok=True)
    #--------全部でかくする--------
    for f in files:
        img = cv2.imread(inputpath + foldername + "/" + f)
        img = cv2.resize(img,None,fx=scale,fy=scale,interpolation=cv2.INTER_NEAREST)
        cv2.imwrite(outputpath + foldername + "_{}times/".format(scale) + f, img)

#------------------------------------

#--------周り画素だけでかくする--------
#img = cv2.imread(path+"read_8.png",0)
#dot1 = img[18:21,7:11]
#dot2 = img[25:28,13:17]
#img = cv2.resize(img,None,fx=8,fy=8,interpolation=cv2.INTER_NEAREST)
#dot1 = cv2.resize(dot1,None,fx=8,fy=8,interpolation=cv2.INTER_NEAREST)
#dot2 = cv2.resize(dot2,None,fx=8,fy=8,interpolation=cv2.INTER_NEAREST)

#cv2.imwrite(path+"big_8.png",img)
#cv2.imwrite(path+"8_dot1.png",dot1)
#cv2.imwrite(path+"8_dot2.png",dot2)
#----------------------------------

cv2.waitKey(0)
cv2.destroyAllWindows()
