# -*- coding: utf-8 -*-
"""

Usage:
    landsat [--thumbnail=PATH] -g <startdate> <enddate>
    landsat [--thumbnail=PATH] -g --list=FILE
    landsat [--overwrite] [--dir=PATH] [-dxcw] ID [ID...]
    landsat [--overwrite] [--dir=PATH] [-dxcw] --list=FILE

Process for landsat Image. Generate html file to select image's ID.
And make true color image from ID.

Arguments:
    ID              Landsat file ID
    FILE            File of ID's list
    startdate       Search date of start "2014-4-1"
    enddate         Search date of end End "2014-12-31"

Options:
    -g              Generate html.
    -d              Download tar.gz file.
    -x              Extract tar.gz file.
    -c              Create true color image.
    -w              Warp to epsg:3857.
    --list=FILE     Use file of ID's list.
    --overwrite     Overwrite file
    --dir=PATH      Directory of process.(default is current directory)
    --thumbnail=PATH      Directory of thumbnail files.(default is "thumbnail")
    -h --help       Show this screen.
    --version       Show version.

"""

from docopt import docopt
import requests
import json
import datetime
import urllib
from os.path import exists,join
from homura import download as fetch
import tarfile
import landsat_color
import subprocess

def process_landsat(idlist,download,extract,create,warp,dir,overwrite):
   thumb_list = [['' for i in range(13)] for j in range(43-28+1)]
   date_list = ['-1' for i in range(13)]
   path_list = ['-1' for i in range(13)]

   for id in idlist:
       path = id[3:6]
       row =id[6:9]
       year = id[9:13]
       ddd = id[13:16]
       refdate = datetime.date(int(year),1,1)
       d = refdate + datetime.timedelta(days=int(ddd))
       date = d.strftime('%Y-%m-%d')

       file = id + ".tar.bz"

       thumb_list[int(row)-28][int(path)-104] = id + ".jpg"
       date_list[int(path)-104] = date
       path_list[int(path)-104] = path

       url = "http://storage.googleapis.com/earthengine-public/landsat/L8/%s/%s/%s" % (path,row,file)
       fpath = join(dir,file)
       unzipdir =join(dir,id)

       if download:
           if (not exists(fpath) or overwrite):
               if not exists(dir):
                  print "skip! not exist:" + dir + " directory"
               else:
                   print "download " + url
                   fetch(url, fpath)
                   # no info download
                   #urllib.urlretrieve(url, fpath)
           else:
                print "already exist:" + fpath
       if extract:
          if (not exists(unzipdir) or overwrite):
               if not exists(fpath):
                  print "skip! not exist:" + fpath
               else:
                  print "unzip " + unzipdir
                  tar = tarfile.open(fpath, 'r')
                  tar.extractall(path=unzipdir)
                  tar.close()
          else:
               print "already exist:" + unzipdir
       if create:
          if (not exists(join(dir,id+".tif")) or overwrite):
               if not exists(unzipdir):
                   print "skip! not exist:" + unzipdir
               else:
                   print "create " + id + ".tif"
                   landsat_color.process(id,join(dir,id),dir)
          else:
               print "already exist:" + join(dir,id+".tif")
       if warp:
           if (not exists(join(dir,id+"w.tif")) or overwrite):
               if not exists(join(dir,id+".tif")):
                   print "skip! not exist:" + join(dir,id+".tif")
               else:
                   cmd = "gdalwarp --config GDAL_CACHEMAX 2048 -wm 2048 -multi -co TILED=YES -co TFW=YES -t_srs EPSG:3857 %s %s;" % (join(dir,id+".tif"),join(dir,id+"w.tif"))
                   #print cmd
                   #cmd = cmd + "nearblack --config GDAL_CACHEMAX 2048 %s" % (join(dir,id+"w.tif"))
                   subprocess.call( cmd,shell=True)
           else:
               print "already exist:" + join(dir,id+"w.tif")
def selected_html(idlist,thumbdir):
    htmlfile = "cloudlist_selected.html"

    thumb_list = [['' for i in range(13)] for j in range(43-28+1)]
    date_list = ['-1' for i in range(13)]
    path_list = ['-1' for i in range(13)]
    for id in idlist:
        path = id[3:6]
        row =id[6:9]
        year = id[9:13]
        ddd = id[13:16]
        refdate = datetime.date(int(year),1,1)
        d = refdate + datetime.timedelta(days=int(ddd))
        date = d.strftime('%Y-%m-%d')
        thumb_list[int(row)-28][int(path)-104] = join(thumbdir,id + ".jpg")
        date_list[int(path)-104] = date
        path_list[int(path)-104] = path
    path_list.reverse()
    date_list.reverse()

    hf = open(htmlfile,"w")
    hf.write('<table cellpadding="0" style="border: solid 1px #000000; border-collapse: collapse;font-size:xx-small">')
    hf.write('<tr><th style="border: solid 1px #000000;width:40px"></th><th style="border: solid 1px #000000;width:40px">' + '</th><th style="border: solid 1px #000000;width:40px">'.join(path_list) + '</th></tr>\n')
    hf.write('<tr><th style="border: solid 1px #000000;width:40px"></th><th style="border: solid 1px #000000;width:40px">' + '</th><th style="border: solid 1px #000000;width:40px">'.join(date_list) + '</th></tr>\n')
    for r,t in zip(range(28,44),thumb_list):
        t.reverse()
        hf.write('<tr><th style="border: solid 1px #000000;">' + str(r) +'</th><td><img src="'+ '" width="300"></td><td><img src="'.join(t) + '" width="300"></td></tr>\n')
    hf.write('</table>')
    hf.close()

def generate_html(s_date,e_date,thumbdir):
   #s_date = "2014-4-1"
   #e_date = "2014-9-30"
   s_path = "104"
   e_path = "116"
   s_row = "28"
   e_row = "43"
   s_cloud = "0"
   e_cloud = "100"

   url = "https://api.developmentseed.org/landsat?search=acquisitionDate:[%s+TO+%s]+AND+cloudCoverFull:[%s+TO+%s]\
   +AND+path:[%s+TO+%s]+AND+row:[%s+TO+%s]&limit=10000"\
   % (s_date,e_date,s_cloud,e_cloud,s_path,e_path,s_row,e_row)
   r = requests.get(url)
   r_dict = json.loads(r.text)

   d =  datetime.datetime.strptime(s_date, '%Y-%m-%d')
   refdate = datetime.date(d.year,d.month,d.day)
   d =  datetime.datetime.strptime(e_date, '%Y-%m-%d')
   term = (datetime.date(d.year, d.month, d.day) -refdate).days
   times = int(term/16)+1

   cloud_list = [[['-1' for i in range(13)] for j in range(43-28+1)] for k in range(times)]
   thumb_list = [[['' for i in range(13)] for j in range(43-28+1)] for k in range(times)]
   date_list = [['-1' for i in range(13)] for k in range(times)]
   path_list = [['-1' for i in range(13)] for k in range(times)]
   for i in r_dict['results']:
      path = i['path']
      row = i['row']
      cloud = i['cloudCoverFull']
      date = i['acquisitionDate']
      thumburl = i['browseURL']
      thumbfile = join(thumbdir,thumburl.split('/')[-1])
      if not exists(thumbfile):
         urllib.urlretrieve(thumburl, thumbfile)
      d =  datetime.datetime.strptime(date, '%Y-%m-%d')
      no = int(((datetime.date(d.year, d.month, d.day) -refdate).days) / 16)
      cloud_list[no][row-28][path-104] = str(int(cloud))
      thumb_list[no][row-28][path-104] = join(thumbdir,thumburl.split('/')[-1])
      date_list[no][path-104] = date
      path_list[no][path-104] = str(path)

   csvfile = "cloudlist" + s_date + "TO"+e_date+".csv"
   htmlfile = "cloudlist" + s_date + "TO"+e_date+".html"
   cf = open(csvfile,"w")
   hf = open(htmlfile,"w")
   for k in range(times):
      path_list[k].reverse()
      date_list[k].reverse()
      cf.write(',' + ','.join(path_list[k]) + '\n')
      cf.write(',' + ','.join(date_list[k]) + '\n')
      hf.write('<table cellpadding="0" style="border: solid 1px #000000; border-collapse: collapse;font-size:xx-small">')
      hf.write('<tr><th style="border: solid 1px #000000;width:30px"></th><th style="border: solid 1px #000000;width:30px">' + '</th><th style="border: solid 1px #000000;width:30px">'.join(path_list[k]) + '</th></tr>\n')
      hf.write('<tr><th style="border: solid 1px #000000;width:30px"></th><th style="border: solid 1px #000000;width:30px">' + '</th><th style="border: solid 1px #000000;width:30px">'.join(date_list[k]) + '</th></tr>\n')
      for r,c,t in zip(range(28,44),cloud_list[k],thumb_list[k]):
         c.reverse()
         t.reverse()
         cf.write(str(r) + ',' + ','.join(c) + '\n')
         hf.write('<tr><th style="border: solid 1px #000000;">' + str(r) +'</th>')
         for tt in t:
            hf.write('<td><img src="' +  tt + '" width="50" onclick=myselect(this,"' + tt +'"); class="pr' + tt[3:9]+'";></td>')
         hf.write('</tr>\n')
      hf.write('</table>')
   hf.write('<table cellpadding="0" style="border: solid 1px #000000; border-collapse: collapse;font-size:xx-small">')
   hf.write('<tr><th style="border: solid 1px #000000;width:30px"></th><th style="border: solid 1px #000000;width:30px">' + '</th><th style="border: solid 1px #000000;width:30px">'.join(path_list[0]) + '</th></tr>\n')
   for r in range(28,44):
      #t.reverse()
      hf.write('<tr><th style="border: solid 1px #000000;">' + str(r) +'</th>')
      for p in range(116,103,-1):
         hf.write('<td><img src="" width="50" id="pr' + str(p) + "0" + str(r) +'"></td>')
      hf.write('</tr>\n')
   hf.write('</table>')
   hf.write('<form><input type="button" value="download" onClick="makelist()"></form>')
   hf.write('<script>function myselect(e,f){var elms = document.getElementsByClassName("pr" +f.substr(3,6));for(var i=0;i<elms.length;i++){elms[i].style.border="none";}var img = document.getElementById("pr"+f.substr(3,6));img.src = f;e.style.border = "solid 1px black";e.style.borderColor ="red"; }function makelist(){var list="";for(var p=104;p<=116;p++){for(var r=28;r<=43;r++){var img = document.getElementById("pr" + p +"0" + r);if(img!=null && img.src.indexOf(".jpg") != -1) list = list + img.src.substring(img.src.lastIndexOf("/")+1, img.src.length).replace(".jpg","") + "\\n"}}var blob = new Blob( [list], {type: "text/plain"} );var link = document.createElement("a");link.href = URL.createObjectURL(blob);link.download = "list.txt";link.click();}</script>')
   cf.close()
   hf.close()



if __name__ == "__main__":
    args = docopt(__doc__, version="0.1.0")
    #print args
    dir = "."
    thumbdir = "thumbnail"
    if args["--dir"]:
        dir = args["--dir"]
    if args["--thumbnail"]:
        thumbdir = args["--thumbnail"]
    if args["-g"]:
        if args["--list"]:
            idlist=[]
            for line in open(args["--list"], 'r'):
                idlist.append(line.rstrip())
            selected_html(idlist,thumbdir)
        else:
            generate_html(args["<startdate>"],args["<enddate>"],thumbdir)
    else:
        if args["--list"]:
            idlist=[]
            for line in open(args["--list"], 'r'):
                idlist.append(line.rstrip())
            process_landsat(idlist,args["-d"],args["-x"],args["-c"],args["-w"],dir,args["--overwrite"])
        else:
            process_landsat(args["ID"],args["-d"],args["-x"],args["-c"],args["-w"],dir,args["--overwrite"])
