
# -*- coding: utf-8 -*-
"""

Usage:
    landsat_color [options] ID

Make true color image from ID.

Arguments:
    ID              Landsat file ID

Options:
    --7             For landsat7
    --5             For landsat5
    --hist          Save histgram Image
    --ndvi          Calc ndvi
    --inpdir=PATH     Input directory of tif files.(default is current dir)
    --outdir=PATH     Output directory of true color image.(default is current dir)
    -h --help       Show this screen.
    --version       Show version.

"""

from docopt import docopt
import numpy as np
import cv2
import sys
import gdal
from osgeo import osr
from gdalconst import *
import landsat
import time
from os.path import exists,join
import math
import pylab as plt

def stretch_hist(file,band,cloud,savehist):
   im = cv2.imread(file,-1)
   #im,T = rof.denoise(im,im)
   #im = np.ma.masked_equal(im,0)
   hist,bins = np.histogram(im.flatten(),65536,[1,65536]) #0を抜く
   cdf = hist.cumsum()
   cdf = 100.0*cdf/cdf[-1]
   #hist = cv2.calcHist([im],[0],None,[65536],[0,65536])
   if savehist:
      #fig = plt.figure()
      plt.plot(hist[1:])
      plt.xlim([10000,65535])
      plt.yscale('log')
      plt.savefig('hist' + str(band) +'.png', bbox_inches='tight')
      #plt.close(fig)

   #ヒストグラム（0を除く）でピクセル数h を閾値とする最大、最小を見つける。
   for i in range(1,len(hist)):#enumerate(hist[1:]):
     if cdf[i]>=0.2: #h>50:#はじめて50ピクセル以上ある色を黒にする。（黒はnodataになるので、実際には少しずらす。青味の調整も）
         hmin = i
         print cdf[i],"% --> ",hmin
         break
   for i in range(1,len(hist)):
     if cdf[65535-i] < 100 - 0.04 * cloud:
         hmax=65535-i
         print cdf[65535-i],"% --> ",hmax
         break
   #これはやってはいけない。0は0
   #im[im<hmin]=hmin
   #im[im>hmax]=hmax
   if cloud < 1:
       sigma = 0.5
   elif 1<= cloud < 2:
       sigma = 0.55
   elif 2<= cloud < 3:
       sigma = 0.6
   elif 3<= cloud < 10:
       sigma = 0.65
   else:
       sigma = 0.7

   im = landsat.stretch(im,hmin,hmax,sigma)


   #im = np.ma.filled(im,255)
   #cythonじゃない場合
   #value = 0.5
   #diff =65535.0/(hmax-hmin)
   #im = np.uint8((np.power((2.0/(1+np.exp(-6*np.intc(diff*(im-hmin))/65535.0))-1), value))*255)


   return im

def stretch_hist2(rgb):
   r = rgb[:,:,2]
   g = rgb[:,:,1]
   b = rgb[:,:,0]
   hist_r,bins = np.histogram(r.flatten(),256,[1,256]) #0を抜く
   hist_g,bins = np.histogram(g.flatten(),256,[1,256]) #0を抜く
   hist_b,bins = np.histogram(b.flatten(),256,[1,256]) #0を抜く
   hist = hist_r + hist_g + hist_b
   cdf = hist.cumsum()
   cdf = 100.0*cdf/cdf[-1]
   #hist_r = cv2.calcHist([r],[0],None,[256],[0,256])
   #hist_g = cv2.calcHist([g],[0],None,[256],[0,256])
   #hist_b = cv2.calcHist([b],[0],None,[256],[0,256])
   #hist = hist_r + hist_g + hist_b
   #ヒストグラム（0を除く）でピクセル数h を閾値とする最大、最小を見つける。
   for i in range(1,len(hist)):#enumerate(hist[1:]):
      if cdf[i] > 0.5:#h>40000:#はじめて50ピクセル以上ある色を黒にする。（黒はnodataになるので、実際には少しずらす。青味の調整も）
         hmin = i#-2*band
         print cdf[i],"% --> ",hmin
         break
   for i in range(1,len(hist)):#numerate(reversed(hist)):
      if cdf[255-i]<99:#h>140000:#はじめて10ピクセル以上ある色を白にする
         hmax=255-i
         print cdf[255-i],"% --> ",hmax
         break
   r[r<hmin]=hmin
   r[r>hmax]=hmax
   g[g<hmin]=hmin
   g[g>hmax]=hmax
   b[b<hmin]=hmin
   b[b>hmax]=hmax
   r = landsat.stretch2(r,hmin,hmax)
   g = landsat.stretch2(g,hmin,hmax)
   b = landsat.stretch2(b,hmin,hmax)
   rgb = cv2.merge([b,g,r])
   #im = np.ma.filled(im,255)
   #cythonじゃない場合
   #value = 0.5
   #diff =65535.0/(hmax-hmin)
   #im = np.uint8((np.power((2.0/(1+np.exp(-6*np.intc(diff*(im-hmin))/65535.0))-1), value))*255)
   return rgb

def stretch_hist7(file,band):
   im = cv2.imread(file,-1)
   #im,T = rof.denoise(im,im)
   #im = np.ma.masked_equal(im,0)
   hist = cv2.calcHist([im],[0],None,[256],[0,256])
   #ヒストグラム（0を除く）でピクセル数h を閾値とする最大、最小を見つける。
   for i,h in enumerate(hist[20:]):
      if band == 8 and h > 40000:#はじめて50ピクセル以上ある色を黒にする。（黒はnodataになるので、実際には少しずらす。青味の調整も）
          hmin = i+19+2
          hmin = 20
          print i+19+2,h
          break
      elif band != 8 and h > 10000:
          hmin = i-2*band+19
          print i-2*band+19,h
          break
   for i,h in enumerate(reversed(hist[:-4])):
      if band ==8 and h > 40000:#はじめて10ピクセル以上ある色を白にする
        hmax=255-i-4
        hmax = 150
        print 255-i-4,h
        break
      elif band != 8 and h > 10000:
        hmax=255-i-4
        print 255-i-4,h
        break
   im[im<hmin]=hmin
   im[im>hmax]=hmax
   #hmax = 100
   #hmin = 0
   im = landsat.stretch7(im,hmin,hmax)
   #im = np.ma.filled(im,255)
   #cythonじゃない場合
   #value = 0.5
   #diff =65535.0/(hmax-hmin)
   #im = np.uint8((np.power((2.0/(1+np.exp(-6*np.intc(diff*(im-hmin))/65535.0))-1), value))*255)


   return im

def process(id,inpdir,outdir,ltype,savehist=False):
    start = time.time()
    pansharpen = False
    if ltype == "8":
        pansharpen = True
        #pass
    ##
    for line in open(join(inpdir,id) + "_MTL.txt",'r'):
        if "CLOUD_COVER" in line:
            cloud = np.float32(line.split("=")[1])
    print "cloud:",cloud
    if ltype == "8":
        r_no = 4
        g_no = 3
        b_no = 2
        p_no = 8
        ##
        print "stretch"
        r = stretch_hist(join(inpdir,id) + "_B" + str(r_no) + ".tif",1,cloud,savehist)
        g = stretch_hist(join(inpdir,id) + "_B" + str(g_no) + ".tif",2,cloud,savehist)
        b = stretch_hist(join(inpdir,id) + "_B" + str(b_no) + ".tif",3,cloud,savehist)
        p = stretch_hist(join(inpdir,id) + "_B" + str(p_no) + ".tif",8,cloud,savehist)
    elif ltype == "7" or ltype == "5":
        r_no = 3
        g_no = 2
        b_no = 1
        p_no = 8
        ##
        print "stretch"
        r = stretch_hist7(join(inpdir,id) + "_B" + str(r_no) + ".tif",1)
        g = stretch_hist7(join(inpdir,id) + "_B" + str(g_no) + ".tif",2)
        b = stretch_hist7(join(inpdir,id) + "_B" + str(b_no) + ".tif",3)
        if pansharpen:
            p = stretch_hist7(join(inpdir,id) + "_B" + str(p_no) + ".tif",8)

    ##
    print "merge"
    rgb = cv2.merge([b,g,r])

    ##

    if pansharpen:
        print "pansharpen"
        rows = p.shape[0]
        cols = p.shape[1]
        rgb = cv2.resize(rgb,(cols,rows))
        hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
        hsv[:,:,2] = p
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    else:
        rows = r.shape[0]
        cols = r.shape[1]

    ##
    #print "stretch2"
    #rgb = stretch_hist2(rgb)

    print "write out"
    #cv2.imwrite("out.tif",rgb)
    gdal.SetConfigOption('GDAL_CACHEMAX','2048')
    if pansharpen:
        ds = gdal.Open(join(inpdir,id) + "_B" + str(p_no) + ".tif")
    else:
        ds = gdal.Open(join(inpdir,id) + "_B" + str(r_no) + ".tif")
    driver = gdal.GetDriverByName('GTiff')
    # compression option cause a slow reading for GIS
    dst_ds  = driver.Create(join(outdir,id) + "truecolor.tif", cols, rows, 3, gdal.GDT_Byte,options = [ 'TILED=YES','TFW=YES'])
    dst_ds.SetGeoTransform(ds.GetGeoTransform())
    dst_ds.SetProjection(ds.GetProjection())
    ds = None

    for i in range(3):
       dst_band = dst_ds.GetRasterBand(i+1)
       dst_band.WriteArray(rgb[:,:,2-i])
       dst_band.FlushCache()
       dst_band.SetNoDataValue(0)

    dst_ds = None
    del dst_ds

    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time)) + "[sec]"

def ndvi_process(id,inpdir,outdir,ltype):
    start = time.time()
    if ltype == "8":
        nir_no = 5
        red_no = 4
    elif ltype == "7" or ltype == "5":
        nir_no = 4
        red_no = 3
    ##radiance,reflectanceを計算するためのパラメータ
    ESUN7=[1970,1842,1547,1044,225.7,np.nan,82.06,1369]
    ESUN5=[1957,1826,1554,1036,215,np.nan,80.67]
    doy = int(id[13:16])
    d = [float(n) for n in open("earth-sun_distance.txt",'r').read().split('\n') if n!=""]
    REMB=[]
    REAB=[]
    RAMB=[]
    RAAB=[]

    for line in open(join(inpdir,id) + "_MTL.txt",'r'):
        if "REFLECTANCE_MULT_BAND_" in line:
            REMB.append(np.float32(line.split("=")[1]))
        if "REFLECTANCE_ADD_BAND_" in line:
            REAB.append(np.float32(line.split("=")[1]))
        if "SUN_ELEVATION" in line:
            SE = np.float32(line.split("=")[1])
        if "RADIANCE_MULT_BAND_" in line:
            RAMB.append(np.float32(line.split("=")[1]))
        if "RADIANCE_ADD_BAND_" in line:
            RAAB.append(np.float32(line.split("=")[1]))


    nir = cv2.imread(join(inpdir,id) + "_B" + str(nir_no) + ".tif",-1).astype(np.float32)
    red = cv2.imread(join(inpdir,id) + "_B" + str(red_no) + ".tif",-1).astype(np.float32)
    nir[nir==0] = np.nan
    red[red==0] = np.nan
    #放射輝度の計算
    nir_radiance = nir * RAMB[nir_no-1] + RAAB[nir_no-1]
    red_radiance = red * RAMB[red_no-1] + RAAB[red_no-1]
    #反射率の計算
    if ltype == "5":
        nir_reflectance = (math.pi * nir_radiance * d[doy-1]**2)/ (ESUN5[nir_no-1]*math.sin(math.radians(SE)))
        red_reflectance = (math.pi * red_radiance * d[doy-1]**2)/ (ESUN5[red_no-1]*math.sin(math.radians(SE)))
    elif ltype == "7":
        nir_reflectance = (math.pi * nir_radiance * d[doy-1]**2)/ (ESUN7[nir_no-1]*math.sin(math.radians(SE)))
        red_reflectance = (math.pi * red_radiance * d[doy-1]**2)/ (ESUN7[red_no-1]*math.sin(math.radians(SE)))
    elif ltype == "8":
        nir_reflectance = (nir * REMB[nir_no-1] + REAB[nir_no-1]) / math.sin(math.radians(SE))
        red_reflectance = (red * REMB[red_no-1] + REAB[red_no-1]) / math.sin(math.radians(SE))

    ndvi = (nir_reflectance - red_reflectance)/(nir_reflectance + red_reflectance)
    green = ndvi.copy()
    green[np.isnan(green)] = 0
    green[green>0.4]=1
    green[green<=0.4]=0

    rows = nir.shape[0]
    cols = nir.shape[1]

    ##
    print "write out"
    #cv2.imwrite("out.tif",rgb)
    gdal.SetConfigOption('GDAL_CACHEMAX','2048')
    ds = gdal.Open(join(inpdir,id) + "_B4.tif")
    driver = gdal.GetDriverByName('GTiff')
    # compression option cause a slow reading for GIS
    dst_ds  = driver.Create(join(outdir,id) + "ndvi.tif", cols, rows, 1, gdal.GDT_Float32,options = [ 'TILED=YES','TFW=YES'])
    dst_ds.SetGeoTransform(ds.GetGeoTransform())
    dst_ds.SetProjection(ds.GetProjection())
    dst_band = dst_ds.GetRasterBand(1)
    dst_band.WriteArray(ndvi)
    dst_band.FlushCache()
    dst_band.SetNoDataValue(0)
    dst_ds = None

    dst_ds  = driver.Create(join(outdir,id) + "green.tif", cols, rows, 1, gdal.GDT_Byte,options = [ 'TILED=YES','TFW=YES'])
    dst_ds.SetGeoTransform(ds.GetGeoTransform())
    dst_ds.SetProjection(ds.GetProjection())
    dst_band = dst_ds.GetRasterBand(1)
    dst_band.WriteArray(green)
    dst_band.FlushCache()
    dst_band.SetNoDataValue(0)
    dst_ds = None

    ds = None
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time)) + "[sec]"

if __name__ == "__main__":
    args = docopt(__doc__, version="0.1.0")

    inpdir = outdir = "."
    ltype = "8"
    if args["--7"]:
        ltype = "7"
    if args["--5"]:
        ltype = "5"
    if args["--inpdir"]:
        inpdir = args["--inpdir"]
    if args["--outdir"]:
        outdir = args["--outdir"]
    if args["--ndvi"]:
        ndvi_process(args["ID"],inpdir,outdir,ltype)
    else:
        process(args["ID"],inpdir,outdir,ltype,args["--hist"])
