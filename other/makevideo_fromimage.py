import cv2
import numpy as np
import os

#inputPath = "chuukan\\winter\\_5times\\"
#outputPath = "PycharmProjects\\OWLIFT\\Videos\\"
filename = "1225_fall2m_1225_fall2m_00"
width = 80
height = 60

fourcc = cv2.VideoWriter_fourcc(*'XVID')
rec = cv2.VideoWriter(outputPath+"{}.avi".format(filename), fourcc, 18.6, (width, height))

frames = []

files = os.listdir(inputPath+filename)

for f in files:
    image = cv2.imread(inputPath+filename+'\\'+f)
    rec.write(image)


rec.release()
