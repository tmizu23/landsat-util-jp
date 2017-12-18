# -*- coding: utf-8 -*-
"""

Usage:
    demtile --from_gtiff=GeoTIFF
    demtile --from_landsat --demdir=PATH
    demtile --demdir=PATH



Make dem from GeoTIFF.

Arguments:
    GeoTIFF              GeoTIFF file

Options:
    --from_landsat    hogehoge
    --from_gtiff=GeoTIFF       fugafuga
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
from osgeo import gdal,osr
import math
import urllib2

def Resolution(zoom ):
    "Resolution (meters/pixel) for given zoom level (measured at Equator)"
    tileSize = 256
    initialResolution = 2 * math.pi * 6378137 / tileSize
    # 156543.03392804062 for tileSize 256 pixels

    return initialResolution / (2**zoom)

def MetersToPixels(mx, my, zoom):
    "Converts EPSG:900913 to pyramid pixel coordinates in given zoom level"
    originShift = 2 * math.pi * 6378137 / 2.0
    # 20037508.342789244
    res = Resolution( zoom )
    px = (mx + originShift) / res
    py = (my + originShift) / res
    return px, py

def PixelsToTile(px, py):
    "Returns a tile covering region in given pixel coordinates"
    tileSize = 256
    tx = int( math.ceil( px / float(tileSize) ) - 1 )
    ty = int( math.ceil( py / float(tileSize) ) - 1 )

    return tx, ty

def GoogleTile(tx, ty, zoom):
    "Converts TMS tile coordinates to Google Tile coordinates"

    # coordinate origin is moved from bottom-left to top-left corner of the extent
    return tx, (2**zoom - 1) - ty

def PixelsToMeters(px, py, zoom):
    "Converts pixel coordinates in given zoom level of pyramid to EPSG:900913"
    originShift = 2 * math.pi * 6378137 / 2.0
    res = Resolution( zoom )
    mx = px * res - originShift
    my = py * res - originShift
    return mx, my

def TileBounds(tx, ty, zoom):
    "Returns bounds of the given tile in EPSG:900913 coordinates"
    tileSize = 256
    minx, miny = PixelsToMeters( tx*tileSize, ty*tileSize, zoom )
    maxx, maxy = PixelsToMeters( (tx+1)*tileSize, (ty+1)*tileSize, zoom )
    return ( minx, miny, maxx, maxy )

def GetExtent(gt,cols,rows):
    ext=[]
    xarr=[0,cols]
    yarr=[0,rows]

    for px in xarr:
        for py in yarr:
            x=gt[0]+(px*gt[1])+(py*gt[2])
            y=gt[3]+(px*gt[4])+(py*gt[5])
            ext.append([x,y])
            #print x,y
        yarr.reverse()
    return ext

def ReprojectCoords(coords,src_srs,tgt_srs):
    trans_coords=[]
    transform = osr.CoordinateTransformation( src_srs, tgt_srs)
    for x,y in coords:
        x,y,z = transform.TransformPoint(x,y)
        trans_coords.append([x,y])
    return trans_coords

def gtiff2tilearea(gtiff,zoom):
   ds = gdal.Open(gtiff)
   gt=ds.GetGeoTransform()
   cols = ds.RasterXSize
   rows = ds.RasterYSize
   ext=GetExtent(gt,cols,rows)
   src_srs=osr.SpatialReference()
   src_srs.ImportFromWkt(ds.GetProjection())
   tgt_srs=osr.SpatialReference()
   tgt_srs.ImportFromEPSG(3857)
   geo_ext=ReprojectCoords(ext,src_srs,tgt_srs)
   tile_area=[]
   for mx,my in geo_ext:
      px,py = MetersToPixels(mx, my, zoom)
      tx,ty = PixelsToTile(px, py)
      tx,ty = GoogleTile(tx,ty,zoom)
      tile_area.append([tx,ty])
      tilemin = min(tile_area)
      tilemax = max(tile_area)
   #[xmin,xmax],[ymin,ymax]
   return [tilemin[0],tilemax[0]],[tilemin[1],tilemax[1]]
   #print geo_ext

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
    return Image.fromarray(np.uint8(shaded))

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
                 img = txt2png(data,zoom)
                 img.save(os.path.join(dpath,fpng))
                 #img2.save(os.path.join(dpath,"a"+fpng))
              if not os.path.exists(os.path.join(os.getcwd(),odir,fpng)):
                 #cmd = "convert " + os.path.join(dpath,fpng) + " " + os.path.join(ldir,fpng) + " -compose softlight -sigmoidal-contrast 2,100% -composite " + os.path.join(odir,fpng)
                 #subprocess.call( cmd, shell=True  )
                 merge(os.path.join(ldir,fpng),os.path.join(dpath,fpng),os.path.join(odir,fpng))


def make_wldfile(tx,ty,zoom,wldfile):

    tileSize = 256
    ty = (2**zoom - 1) - ty
    minx,miny,maxx,maxy = TileBounds(tx, ty, zoom)
    wld_A = (maxx-minx)/tileSize
    wld_B = 0
    wld_C = 0
    wld_D = (miny-maxy)/tileSize
    wld_E = minx + wld_A/2.0
    wld_F = maxy + wld_D/2.0
    f = open(wldfile,"w")
    f.write(str(wld_A)+"\n")
    f.write(str(wld_B)+"\n")
    f.write(str(wld_C)+"\n")
    f.write(str(wld_D)+"\n")
    f.write(str(wld_E)+"\n")
    f.write(str(wld_F)+"\n")
    f.close()

def download_tile(tx,ty,zoom,outpng):

    if not os.path.exists(outpng):
       url = "http://cyberjapandata.gsi.go.jp/xyz/dem/%d/%d/%d.txt" % (zoom,tx,ty)
       response = urllib2.urlopen(url)
       data = response.read()
       img = txt2png(data,zoom)
       img.save(outpng)

def merge_tile():
    #cmd = "gdalbuildvrt -input_file_list tilelist.txt temp.vrt"
    #subprocess.call( cmd, shell=True  )
    #gdalbuildvrt temp.vrt *.png
    cmd = "gdalwarp --config GDAL_CACHEMAX 2048 -s_srs epsg:3857 dem_tmp/*.png dem.tif"
    subprocess.call( cmd, shell=True  )
    cmd = "gdaltindex -t_srs epsg:4612 aso.shp aso.tif"
    subprocess.call( cmd, shell=True  )
    cmd = "gdalwarp -tr 30 30 -cutline aso.shp -crop_to_cutline dem.tif dem_cut.tif"
    subprocess.call( cmd, shell=True  )
    #python mergedem.py aso.tif dem_cut.tif tmp3.tif



def from_gtiff(gtiff):
    zoom = 14
    tmpdir = "dem_tmp"
    if not os.path.exists(tmpdir):
       os.mkdir(tmpdir)
    f = open("tilelist.txt","w")
    x_range,y_range = gtiff2tilearea(gtiff,zoom)
    for tx in range(x_range[0],x_range[1]+1):
       for ty in range(y_range[0],y_range[1]+1):
          outpng = os.path.join(tmpdir,str(zoom)+str(tx)+str(ty) + ".png")
          wldfile = os.path.join(tmpdir,str(zoom)+str(tx)+str(ty) + ".wld")
          download_tile(tx,ty,zoom,outpng)
          make_wldfile(tx,ty,zoom,wldfile)
          f.write(outpng+"\n")
    f.close()
    merge_tile()


if __name__ == "__main__":
    args = docopt(__doc__, version="0.1.0")
    if args["--from_landsat"]:
       from_landsat(args["--demdir"])
    elif args["--from_gtiff"]:
       from_gtiff(args["--from_gtiff"])

    else:
       from_dem(args["--demdir"])
