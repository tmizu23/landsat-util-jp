from osgeo import ogr,osr
import os,sys



def writeshp(output,pointsX,pointsY):
    if os.path.exists(output):
        os.remove(output)
    driver = ogr.GetDriverByName('ESRI Shapefile')
    datasource = driver.CreateDataSource(output)
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(3857)
    layer = datasource.CreateLayer('',geom_type=ogr.wkbPolygon,srs = proj)
    #create polygon object:
    myRing = ogr.Geometry(type=ogr.wkbLinearRing)
    myRing.AddPoint(pointsX[0], pointsY[0])#UpperLeft
    myRing.AddPoint(pointsX[1], pointsY[1])#UpperRight
    myRing.AddPoint(pointsX[2], pointsY[2])#Lower Right
    myRing.AddPoint(pointsX[3], pointsY[3])#LowerLeft
    myRing.AddPoint(pointsX[0], pointsY[0])#close ring
    myPoly = ogr.Geometry(type=ogr.wkbPolygon)
    myPoly.AddGeometry(myRing)

    #create feature object with point geometry type from layer object:
    feature = ogr.Feature( layer.GetLayerDefn() )
    feature.SetGeometry(myPoly)
    layer.CreateFeature(feature)

    #flush memory
    feature.Destroy()
    datasource.Destroy()

input = sys.argv[1]
outdir = sys.argv[2]
driver = ogr.GetDriverByName('ESRI Shapefile')

#Read data
dataSource = driver.Open(input, 0)
layer = dataSource.GetLayer()
for i,feature in enumerate(layer):
    pointsX = []
    pointsY = []
    attr = feature.GetField(0)
    output = os.path.join(outdir,attr+".shp")
    geom = feature.GetGeometryRef()
    g = geom.GetGeometryRef(0)
    numpoints = g.GetPointCount()
    for p in range(numpoints):
        x, y, _ = g.GetPoint(p)
        pointsX.append(x)
        pointsY.append(y)
    print pointsX,pointsY
    path = int(attr[3:6])
    row = int(attr[6:9])
    print attr
    if path==107 and row>=31:
        diffx1 = (pointsX[1] - pointsX[0])/6.0
        diffx2 = (pointsX[2] - pointsX[3])/6.0
        diffy1 = (pointsY[0] - pointsY[3])/6.0
        diffy2 = (pointsY[1] - pointsY[2])/6.0
        pointsX[0] = pointsX[0] - diffx1
        pointsX[1] = pointsX[1]
        pointsX[2] = pointsX[2]
        pointsX[3] = pointsX[3] - diffx2
        pointsY[0] = pointsY[0] - diffy1
        pointsY[1] = pointsY[1] - diffy2
        pointsY[2] = pointsY[2] - diffy2
        pointsY[3] = pointsY[3] - diffy1
    else:
        diffx1 = (pointsX[1] - pointsX[0])/6.0
        diffx2 = (pointsX[2] - pointsX[3])/6.0
        diffy1 = (pointsY[0] - pointsY[3])/6.0
        diffy2 = (pointsY[1] - pointsY[2])/6.0
        pointsX[0] = pointsX[0] - diffx1
        pointsX[1] = pointsX[1] - diffx1
        pointsX[2] = pointsX[2] - diffx2
        pointsX[3] = pointsX[3] - diffx2
        pointsY[0] = pointsY[0] - diffy1
        pointsY[1] = pointsY[1] - diffy2
        pointsY[2] = pointsY[2] - diffy2
        pointsY[3] = pointsY[3] - diffy1
    writeshp(output,pointsX,pointsY)
