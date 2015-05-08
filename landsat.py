import requests
import json
import datetime
import urllib
from os.path import exists,join


htmldir = join("landsat","html")

def download_list(flag):
   thumb_list = [['' for i in range(13)] for j in range(43-28+1)]
   date_list = ['-1' for i in range(13)]
   path_list = ['-1' for i in range(13)]
   
   for line in open('listtest.txt', 'r'):
       path,row,date = line.rstrip().split(',')
       d =  datetime.datetime.strptime(date, '%Y-%m-%d')
       refdate = datetime.date(d.year,1,1)
       ddd = (datetime.date(d.year, d.month, d.day) -refdate).days + 1
       file = "LC8%s%s%s%sLGN00.tar.bz"% (path,row,d.year,ddd)
       
       thumb_list[int(row)-28][int(path)-104] = "LC8%s%s%s%sLGN00.jpg"% (path,row,d.year,ddd)
       date_list[int(path)-104] = date
       path_list[int(path)-104] = path
       
       url = "http://storage.googleapis.com/earthengine-public/landsat/L8/%s/%s/%s" % (path,row,file)
       fpath = join("landsat","download",file)
       if flag:
          print fpath
          if not exists(fpath):
             print url
             urllib.urlretrieve(url, fpath)
       
   path_list.reverse()
   date_list.reverse()
   htmlfile = "cloudlist_selected.html"
   
   hf = open(join(htmldir,htmlfile),"w")
   hf.write('<table cellpadding="0" style="border: solid 1px #000000; border-collapse: collapse;font-size:xx-small">')
   hf.write('<tr><th style="border: solid 1px #000000;width:40px"></th><th style="border: solid 1px #000000;width:40px">' + '</th><th style="border: solid 1px #000000;width:40px">'.join(path_list) + '</th></tr>\n')
   hf.write('<tr><th style="border: solid 1px #000000;width:40px"></th><th style="border: solid 1px #000000;width:40px">' + '</th><th style="border: solid 1px #000000;width:40px">'.join(date_list) + '</th></tr>\n')
   for r,t in zip(range(28,44),thumb_list):
     t.reverse()
     hf.write('<tr><th style="border: solid 1px #000000;">' + str(r) +'</th><td><img src="'+ '" width="300"></td><td><img src="'.join(t) + '" width="300"></td></tr>\n')
   hf.write('</table>')
   hf.close()    

def search_landsat():
   s_date = "2014-5-1"
   e_date = "2014-10-31"
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
      thumbfile = join(htmldir,thumburl.split('/')[-1])
      if not exists(thumbfile):
         urllib.urlretrieve(thumburl, thumbfile)
      d =  datetime.datetime.strptime(date, '%Y-%m-%d')
      no = int(((datetime.date(d.year, d.month, d.day) -refdate).days) / 16)
      cloud_list[no][row-28][path-104] = str(int(cloud))
      thumb_list[no][row-28][path-104] = thumburl.split('/')[-1]
      date_list[no][path-104] = date
      path_list[no][path-104] = str(path)
   
   csvfile = "cloudlist" + s_date + "TO"+e_date+".csv"
   htmlfile = "cloudlist" + s_date + "TO"+e_date+".html"
   cf = open(join(htmldir,csvfile),"w")
   hf = open(join(htmldir,htmlfile),"w")
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
         hf.write('<tr><th style="border: solid 1px #000000;">' + str(r) +'</th><td><img src="'+ '" width="50"></td><td><img src="'.join(t) + '" width="50"></td></tr>\n')
      hf.write('</table>')
   cf.close()
   hf.close()
   
#search_landsat() 
download_list(1)
