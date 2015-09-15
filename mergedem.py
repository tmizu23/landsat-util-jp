import cv2
import numpy as np
import landsat
import sys
    
def merge(ftile,fdem,fout):
    tile = cv2.imread(ftile)
    dem = cv2.imread(fdem)
    #a = mergetiledem(tile,dem)
    a = landsat.mergetiledem(tile,dem)
    cv2.imwrite(fout,a)

argvs = sys.argv
merge(argvs[1],argvs[2],argvs[3])
#merge("./landsat/13/7164/3231.png","./dem/13/7164/3231.png","test.png")