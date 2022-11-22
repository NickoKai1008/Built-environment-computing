# Author: Nicko
# -*- coding = utf-8 -*-
# @Time : 2021/10/16 23:45
# @Author : kai
# @File : R2P.py
# @Software : PyCharm

import shapely
from shapely.geometry import Point, Polygon, MultiPoint
from osgeo import gdal, ogr
from sklearn import preprocessing
import csv
import numpy as np
import math
import json
import geojson
import matplotlib.pyplot as plt
import codecs
import geopandas as gpd

gj1 = gpd.read_file(r'..\AD35.shp')
iDriver = ogr.GetDriverByName('ESRI Shapefile')
iShpGrid1 = iDriver.Open(r'..\AD35.shp', 1)
iShpGrid = iShpGrid1.GetLayer()
iCountGrid = iShpGrid.GetFeatureCount()
iFeatureList1 = []  # 存储多个feature
iFeatureList2 = []  # 存储多个feature
iFeatureList3 = []  # 存储多个feature
iFeatureList4 = []  # 存储多个feature
iFeatureList5 = []  # 存储多个feature
iFeatureList6 = []  # 存储多个feature
iFeatureList7 = []  # 存储多个feature
iFeatureList8 = []  # 存储多个feature
iFeatureList9 = []  # 存储多个feature
iFeatureList10 = []  # 存储多个feature
H = gj1['height']
radious = 300

for i in range(iCountGrid):
    print(i)
    h = H[i]
    iFeatureGrid = iShpGrid.GetFeature(i)
    iGeometry = iFeatureGrid.GetGeometryRef()
    iPolygonJSONStr = iGeometry.ExportToJson()
    iPolygonJSON = json.loads(iGeometry.ExportToJson())
    ori_area = iGeometry.GetArea()
    iXYTuple = ()
    for j in range(len(iPolygonJSON['coordinates'][0])):
        iXYTuple = iXYTuple+((iPolygonJSON['coordinates'][0][j][0] , iPolygonJSON['coordinates'][0][j][1]),)
    polygon = Polygon(iXYTuple)
    min_rect = polygon.minimum_rotated_rectangle
    print("面积:", min_rect.area)
    iFeature = {}  # 存储单个feature
    iFeature["type"] = "Feature"
    iPolygonJSON = json.loads(json.dumps(shapely.geometry.mapping(min_rect)))
    iFeature["geometry"] = iPolygonJSON
    # 获取每个外接矩形的顶点坐标
    iCoords1 = iPolygonJSON['coordinates'][0]
    iX1, iY1 = iCoords1[0]
    iX2, iY2 = iCoords1[1]
    iX3, iY3 = iCoords1[2]
    iX4, iY4 = iCoords1[3]
    centroidX = (iX1 + iX2 + iX3 + iX4) / 4
    centroidY = (iY1 + iY2 + iY3 + iY4) / 4

    # 计算高宽长
    p1 = np.array([iX1, iY1])
    p2 = np.array([iX2, iY2])
    p3 = np.array([iX3, iY3])
    l1 = p2-p1
    l2 = p3-p2
    len1 = math.hypot(l1[0], l1[1])
    len2 = math.hypot(l2[0], l2[1])

    if len1 > len2:
        l = len1
        w = len2
        ang = math.atan2(l1[1], l1[0])
        ang = int(ang * 180 / math.pi)
    else:
        l = len2
        w = len1
        ang = math.atan2(l2[1], l2[0])
        ang = int(ang * 180 / math.pi)
    if ang < 0:
        ang = ang + 180
    # 计算宽长比
    widlen = w/l
    concentricity = ori_area / min_rect.area

    iA = i
    iFeatureList2.append(centroidX)
    iFeatureList3.append(centroidY)
    iFeatureList4.append(ori_area)
    iFeatureList5.append(widlen)
    iFeatureList6.append(concentricity)


    insA = []  # 存储多个feature
    for z in range(len(iFeatureList2)):
        dis = math.sqrt(((iFeatureList2[i] - iFeatureList2[z]) ** 2) + ((iFeatureList3[i] - iFeatureList3[z]) ** 2))
        if dis < radious:
            insA.append(iFeatureList4[z])
        totalZ = sum(insA)
        var = np.var(insA)
        density = totalZ / (3.14 * (radious) ** 2)
    print(i)
    print(var)
    print(density)

    iFeatureList7.append(density)
    iFeatureList8.append(var)
    iFeatureList1.append(iA)
    iFeatureList10.append(h)

x1 = (iFeatureList10 - np.min(iFeatureList10)) / (np.max(iFeatureList10) - np.min(iFeatureList10))
x2 = (iFeatureList4 - np.min(iFeatureList4)) / (np.max(iFeatureList4) - np.min(iFeatureList4))
x3 = (iFeatureList5 - np.min(iFeatureList5)) / (np.max(iFeatureList5) - np.min(iFeatureList5))
x4 = (iFeatureList6 - np.min(iFeatureList6)) / (np.max(iFeatureList6) - np.min(iFeatureList6))
x5 = (iFeatureList7 - np.min(iFeatureList7)) / (np.max(iFeatureList7) - np.min(iFeatureList7))
x6 = (iFeatureList8 - np.min(iFeatureList8)) / (np.max(iFeatureList8) - np.min(iFeatureList8))

for i in range(iCountGrid):
    if iFeatureList10[i] < float(12) and iFeatureList4[i] < float(500) and iFeatureList6[i] < 15000000:
        zw = x1[i] + x2[i] - x3[i] - x4[i] - x5[i] * 4 + x6[i]
    else:
        zw = x1[i] + x2[i] - x3[i] - x4[i] - x5[i] + x6[i]
    iFeatureList9.append(zw)
zy = 100 * (iFeatureList9 - np.min(iFeatureList9)) / (np.max(iFeatureList9) - np.min(iFeatureList9))
zk = zy.tolist()

zData_list = []
for a, b, c, d, e, f, g, gg in zip(iFeatureList1, iFeatureList10, iFeatureList4, zk, iFeatureList2, iFeatureList3, iFeatureList7, iFeatureList8):
    k = {}
    k['ID'] = a
    k['height'] = b
    k['Area'] = c
    k['resilience'] = d
    k['x'] = e
    k['y'] = f
    k['density'] = g
    k['var'] = gg
    zData_list.append(k)
# print(zk)
with open(r'..\resilience1.csv', 'w', newline = '', encoding = 'UTF-8') as f_c_csv:
    writer = csv.writer(f_c_csv)
    writer.writerow(['ID', 'height', 'Area', 'resilience', 'x', 'y', 'density', 'var'])
    for nl in zData_list:
        writer.writerow(nl.values())
print("finished")

