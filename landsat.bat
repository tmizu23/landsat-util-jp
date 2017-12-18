SET id=LC81070332014151LGN00

FOR %%B in (4,3,2) DO gdalwarp -t_srs EPSG:3857 %id%_B%%B.tif %%B-projected.tif
"C:\Program Files\ImageMagick-6.9.1-Q16\convert.exe" -combine 4-projected.tif 3-projected.tif 2-projected.tif RGB.tif
"C:\Program Files\ImageMagick-6.9.1-Q16\convert.exe" -channel B -gamma 0.925 -channel R -gamma 1.03 -channel RGB -sigmoidal-contrast 50x16%% RGB.tif RGB-corrected.tif
"C:\Program Files\ImageMagick-6.9.1-Q16\convert.exe" -depth 8 RGB-corrected.tif RGB-corrected-8bit.tif
listgeo -tfw 3-projected.tif
mv 3-projected.tfw RGB-corrected-8bit.tfw
gdal_translate -of VRT -a_srs EPSG:3857 RGB-corrected-8bit.tif RGB-corrected-8bit.vrt 
gdalwarp -srcnodata 0 -dstalpha RGB-corrected-8bit.vrt %id%.tif

