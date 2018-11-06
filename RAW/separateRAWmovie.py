# coding: utf-8

import numpy as np
import os
import array
import tifffile

import readRaw
import hdrRendering



def separete(mode, path, output, saveRaw=True, saveTiff=True, ratio=None, ofset=None, th=None):
    outRaw = output[0]
    outTiff = output[1]

    width, height, bit = readRaw.modeCheck(mode)
    if mode == 'ME':
        if th == None:
            render = hdrRendering.HDRrendering(ratio, ofset)
        else:
            render = hdrRendering.HDRrendering(ratio, ofset, th)


    numOfPixel = int(os.path.getsize(path) / 2)  # number of pixel
    length = int(numOfPixel / width / height)
    print('the number of frames: {}'.format(length))
    f = open(path, 'rb')

    for i in range(length):
        f.seek(width * height * i * 2)

        data = array.array('H')  # 'H': unsigned short (2byte)
        data.fromfile(f, width * height)
        raw = np.array(data).reshape(height, width)  # 画像の形に変える
        raw = raw[10:]  # 上から10行は真っ黒
        #raw -= 256  #sub dark ofset
        #raw[raw < 0] = 0  #0~3839

        #RAW保存名
        nameRaw = outRaw + '\\' + path.split('\\')[-1][:-4] + '_{:05d}.raw'.format(i)
        nameTiff = outTiff + '\\' + path.split('\\')[-1][:-4] + '_{:05d}.tif'.format(i)

        if mode == 'SE' or mode == 'SDR':
            print('raw min: {}  max: {}'.format(raw.min(), raw.max()))

            # --------------- save raw ---------------
            if saveRaw == True:
                rawfile = open(nameRaw, 'wb')
                rawfile.write(bytearray(data))
                rawfile.close()

            # --------------- save tiff ---------------
            if saveTiff == True:
                raw16bit = raw.astype(np.uint16)
                img16bit = readRaw.rgb(raw16bit)
                tifffile.imsave(nameTiff, img16bit, dtype='uint16')

            print('{} / {}\n\n'.format(i+1, length))

            """
            from PIL import Image
            img16bit3839 = np.float32(img16bit)
            img16bit3839 /= 3839
            img8bit = img16bit3839 * 255
            img = Image.fromarray(np.uint8(img8bit))

            img.show()
            break
            """

        elif mode == 'ME':
            raw0 = raw[0:1080, 0:1920]
            raw1 = raw[ofset:ofset+1080, 1920:3840]
            print('raw   dark  min: {}  max: {}'.format(raw0.min(), raw0.max()))
            print('raw bright  min: {}  max: {}'.format(raw1.min(), raw1.max()))

            #--------------- save raw ---------------
            if saveRaw == True:
                rawfile = open(nameRaw, 'wb')
                rawfile.write(bytearray(data))
                rawfile.close()

            #--------------- save tiff ---------------
            if saveTiff == True:
                GrGbRB0 = render.separateColor(raw0)
                tint0area = render.checkSaturation(GrGbRB0)
                hdr = render.rendering(raw0, raw1, tint0area)

                raw16bit = hdr.astype(np.uint16)
                img16bit = readRaw.rgb(raw16bit)
                tifffile.imsave(nameTiff, img16bit, dtype='uint16')


            print('{} / {}\n\n'.format(i+1, length))

    f.close()

    return





def main():
    mode = 'SDR'
    path = '\\'
    files = sorted([f for f in os.listdir(path) if f[-4:] == '.raw'])
    print(files)

    #------ME-HDR setting--------
    exp1 = np.array([276, 2186])
    exp2 = np.array([8, 68])
    expRatio = exp1 / exp2
    ofset = exp2
    #---------------------------


    for i, file in enumerate(files):
        print('INPUT PATH: {}'.format(path))
        outRaw = path + file[:-4] + '_raw'
        print('RAW OUTPUT PATH: {}'.format(outRaw))
        outTiff = path + file[:-4] + '_tiff'
        print('TIFF OUTPUT PATH: {}'.format(outTiff))

        os.mkdir(outRaw)
        os.mkdir(outTiff)

        output = [outRaw, outTiff]
        #separete(mode, path+file, output, ratio=expRatio[i], ofset=ofset[i])
        separete(mode, path + file, output)

    return




if __name__ == '__main__':
    main()
