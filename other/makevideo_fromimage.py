import cv2
import numpy as np
import os

#inputPath = "C:\\users\\Takumi\\PycharmProjects\\OWLIFT\\image_data\\fall\\"
inputPath = r"C:\Users\Takumi\PycharmProjects\OWLIFT\image_data\dataset\fall_detection_dataset\fall_270\\"
#inputPath = "C:\\Users\\Takumi\\chuukan\\winter\\_5times\\"
#outputPath = "C:\\users\\Takumi\\PycharmProjects\\OWLIFT\\Videos\\"
outputPath = "C:\\users\\Takumi\\PycharmProjects\\OWLIFT\\image_data\\"
#outputPath = "C:\\Users\\Takumi\\chuukan\\winter\\"
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