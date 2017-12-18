import cython
cimport cython
import numpy as np
cimport numpy as np
from libc.math cimport exp,pow

DTYPE16 = np.uint16
DTYPE8 = np.uint8
ctypedef np.uint16_t DTYPE16_t
ctypedef np.uint8_t DTYPE8_t

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
def stretch(np.ndarray[DTYPE16_t, ndim=2] im,int hmin,int hmax,float sigma):
   cdef int xmax = im.shape[0]
   cdef int ymax = im.shape[1]
   cdef float diff = 65535./(hmax-hmin)
   cdef np.ndarray[DTYPE8_t, ndim=2] im2 = np.zeros([xmax, ymax], dtype=DTYPE8)
   cdef int x, y, d
   # stretch and logistics and bright
   # http://earthobservatory.nasa.gov/blogs/elegantfigures/2013/10/22/how-to-make-a-true-color-landsat-8-image/
   for x in range(xmax):
      for y in range(ymax):
         if im[x,y] == 0: #nodata
            im2[x,y] = 0
         else:
            d = (int)(((2.0/(1+exp(-6*(diff*(im[x,y]-hmin))/65535.0))-1)**sigma)*255)
            if d<=15: #near black
               im2[x,y]=10 #the value 10 is important. if the value is 1, it  change to 0 when converting to hsv
            else:
               im2[x,y]=d
   return im2

def stretch7(np.ndarray[DTYPE8_t, ndim=2] im,int hmin,int hmax,float sigma):
   cdef int xmax = im.shape[0]
   cdef int ymax = im.shape[1]
   cdef float diff = 1./(hmax-hmin)
   cdef np.ndarray[DTYPE8_t, ndim=2] im2 = np.zeros([xmax, ymax], dtype=DTYPE8)
   cdef int x, y, d
   # stretch and logistics and bright
   # http://earthobservatory.nasa.gov/blogs/elegantfigures/2013/10/22/how-to-make-a-true-color-landsat-8-image/
   for x in range(xmax):
      for y in range(ymax):
         if im[x,y] == 0: #nodata
            im2[x,y] = 0
         else:
            d = (int)(((diff*(im[x,y]-hmin))**0.4)*255)
            #d = (int)(((2.0/(1+exp(-6*(diff*(im[x,y]-hmin))/255.0))-1)**sigma)*255)
            if d==0: #near black
               im2[x,y]=1 #the value 10 is important. if the value is 1, it  change to 0 when converting to hsv
            else:
               im2[x,y]=d
   return im2

def mergetiledem(np.ndarray[DTYPE8_t, ndim=3] tile,np.ndarray[DTYPE8_t, ndim=3] dem):
    #http://ofo.jp/osakana/cgtips/blendmode.phtml
    #softlight 2times
    cdef int xsize = tile.shape[0]
    cdef int ysize = tile.shape[1]
    cdef np.ndarray[DTYPE8_t, ndim=3] a = np.zeros([xsize,ysize,3], dtype=np.uint8)
    cdef int x, y, b, m
    for x in range(xsize):
       for y in range(ysize):
          for b in range(3):
            #soft-light 2times http://ofo.jp/osakana/cgtips/blendmode.phtml
            if 0<dem[x,y,b]<128:
               m= (int)(255*(tile[x,y,b]/255.0)**(2*(1-dem[x,y,b]/255.0)))
            elif dem[x,y,b]>=128:
               m= (int)(255*(tile[x,y,b]/255.0)**(1/(2*dem[x,y,b]/255.0)))
            else:
               m=0
            if 0<tile[x,y,b]<128:
               m = (int)(255*(m/255.0)**(2*(1-tile[x,y,b]/255.0)))
            elif tile[x,y,b]>=128:
               m = (int)(255*(m/255.0)**(1/(2*tile[x,y,b]/255.0)))
            else:
               m = 0
            if tile[x,y,b] == 0:
               a[x,y,b] = 0
            elif m < 5:
               a[x,y,b] = 5
            else:
               a[x,y,b] = m

    return a
