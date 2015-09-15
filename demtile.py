# -*- coding: utf-8 -*-
"""

Usage:
    demtile --from_landsat --demdir=PATH
    demtile --demdir=PATH

Make true color image from ID.

Arguments:
    ID              Landsat file ID

Options:
    --from_landsat    Input directory of tif files.(default is current dir)
    --inpdir=PATH     Input directory of tif files.(default is current dir)
    --outdir=PATH     Output directory of true color image.(default is current dir)
    -h --help       Show this screen.
    --version       Show version.

"""

from docopt import docopt

from PIL import Image
import os
import numpy as np
from numpy import pi,arctan,sqrt,arctan2,sin,cos
import scipy.ndimage
import subprocess
import cv2
import landsat

def merge(ftile,fdem,fout):
    #print fdem
    if os.path.exists(ftile) and os.path.exists(fdem):
       tile = cv2.imread(ftile)
       dem = cv2.imread(fdem)
       #a = mergetiledem(tile,dem)
       a = landsat.mergetiledem(tile,dem)
       cv2.imwrite(fout,a)

def txt2png(data,z):
    data = data.replace("e","0")
    dem = np.array([row.split(',') for row in data.splitlines()],dtype=np.float32)

    TSIZE = 20037508.342789244

    size = TSIZE / 2 ** (z - 1)
    res = size/256.
    zscale=5
    azimuth=225
    angle_altitude=45

    x, y = np.gradient(dem*zscale,res,-res)
    slope = pi/2. - arctan(sqrt(x*x + y*y))
    aspect = arctan2(-x, y)
    azimuthrad = azimuth*pi / 180.
    altituderad = angle_altitude*pi / 180.
    shaded = sin(altituderad) * sin(slope) + cos(altituderad) * cos(slope) * cos(azimuthrad - aspect)
    shaded = 255*(shaded + 1)/2
    slope =  (1-slope*2/pi)*255

    rgb = (slope*shaded)/255
    return Image.fromarray(np.uint8(rgb)),Image.fromarray(np.uint8(slope))

def from_landsat(demdir):
    for dpath,dnames,fnames in os.walk("./landsat"):
        outdir = dpath.replace('landsat','dem_landsat')

        if not os.path.exists(outdir):
           os.mkdir(outdir)

        for fname in fnames:
           if ".png" in fname:
              #print os.path.join(os.getcwd(),outdir,fname)
              if not os.path.exists(os.path.join(os.getcwd(),outdir,fname)):
                 merge(os.path.join(dpath,fname),os.path.join(demdir,dpath.replace('landsat','.'),fname),os.path.join(outdir,fname))

def from_dem(demdir):
    for dpath,dnames,fnames in os.walk(demdir):
        ldir = dpath.replace('dem','landsat')
        odir = dpath.replace('dem','dem_landsat')

        if not os.path.exists(odir):
           os.mkdir(odir)

        for fname in fnames:
           if ".txt" in fname:
              zoom = int(dpath.split('/')[1])
              fpng = fname.replace('txt','png')
              print zoom,fpng
              if not os.path.exists(os.path.join(dpath,fpng)):
                 with open(os.path.join(dpath,fname)) as f:
                    data = f.read()
                 img,img2 = txt2png(data,zoom)
                 img.save(os.path.join(dpath,fpng))
                 img2.save(os.path.join(dpath,"a"+fpng))
              if not os.path.exists(os.path.join(os.getcwd(),odir,fpng)):
                 #cmd = "convert " + os.path.join(dpath,fpng) + " " + os.path.join(ldir,fpng) + " -compose softlight -sigmoidal-contrast 2,100% -composite " + os.path.join(odir,fpng)
                 #subprocess.call( cmd, shell=True  )
                 merge(os.path.join(ldir,fpng),os.path.join(dpath,fpng),os.path.join(odir,fpng))

if __name__ == "__main__":
    args = docopt(__doc__, version="0.1.0")
    if args["--from_landsat"]:
       from_landsat(args["--demdir"])
    else:
       from_dem(args["--demdir"])
