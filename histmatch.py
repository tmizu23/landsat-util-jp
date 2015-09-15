# -*- coding:utf-8 -*-

import cv2
import sys
#import mytest
import numpy as np


def cal_trans(ref,adj):
    """
        calculate transfer function
        algorithm refering to wiki item: Histogram matching
    """
    #print ref
    #print adj
    #table = np.array([0]*256,dtype=np.uint8)
    table = np.arange(256,dtype=np.uint8)
    for i in range(1,256):
        for j in range(0,255): #255
            if ref[0] > adj[i]:
               table[i] = 0
               break
            elif ref[j] <= adj[i] < ref[j+1]:
               table[i] = j
               break
            else:
               pass
               #table[i] = 255

    #table[255] = 255
    print table
    return table


if __name__ == '__main__':


    refimg = cv2.imread(sys.argv[1])
    dstimg = cv2.imread(sys.argv[2])
    tables = []
    for b in range(3):
       hist,bins = np.histogram(refimg[:,:,b].flatten(),256,[0,256])
       refcdf = hist.cumsum()
       #print refcdf
       hist,bins = np.histogram(dstimg[:,:,b].flatten(),256,[0,256])
       dstcdf = hist.cumsum()
       #print dstcdf
       tables.append(cal_trans(refcdf,dstcdf))
    tables = np.dstack(tables)


    print "b"
    im = cv2.LUT(dstimg,tables)
    #im = mytest.calc(dstimg,tables)

    print "c"

    print "d"
    cv2.imwrite("test.tif",im)
