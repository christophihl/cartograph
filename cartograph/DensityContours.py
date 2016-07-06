import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mplPath
import scipy.ndimage as spn
from geojson import Feature, FeatureCollection
from geojson import dumps, MultiPolygon
import json
import shapely.geometry as shply


class ContourCreator:

    def __init__(self, numClusters):
        self.numClusters = numClusters
        pass

    def buildContours(self, featureDict, writeFile):
        xs, ys = self._sortClusters(featureDict)
        self.CSs = self._calc_contour(xs, ys, 200)
        # Nested list.
        # One outer parent list for each cluster. (n=~10)
        # One child inner list for each contour (n=~7)
        # One grandchild list for each polygon within the contour
        self.plyList = self._get_contours(self.CSs)
        self.newPlys = self._cleanContours(self.plyList, writeFile)

    def _sortClusters(self, featureDict):
        xs = [[] for i in range(self.numClusters)]
        ys = [[] for i in range(self.numClusters)]

        keys = featureDict.keys()
        for index in keys:
            pointInfo = featureDict[index]
            if pointInfo['keep'] != 'True' or 'cluster' not in pointInfo:
                continue
            c = int(pointInfo['cluster'])
            xs[c].append(float(pointInfo['x']))
            ys[c].append(float(pointInfo['y']))
        return xs, ys

    @staticmethod
    def _calc_contour(clusterXs, clusterYs, binSize):
        CSs = []
        for (xs, ys) in zip(clusterXs, clusterYs):
            H, yedges, xedges = np.histogram2d(ys, xs,
                                               bins=binSize,
                                               range=[[np.min(ys),
                                                      np.max(ys)],
                                                      [np.min(xs),
                                                      np.max(xs)]])

            H = spn.filters.gaussian_filter(H, 2)
            extent = [xedges.min(), xedges.max(), yedges.min(), yedges.max()]

            smoothH = spn.zoom(H, 4)
            smoothH[smoothH < 0] = 0
            CSs.append(plt.contour(smoothH, extent=extent))

        return CSs

    @staticmethod
    def _get_contours(CSs):
        plyList = []
        for CS in CSs:
            plys = []
            for i in range(len(CS.collections)):
                shapes = []
                for j in range(len(CS.collections[i].get_paths())):
                    p = CS.collections[i].get_paths()[j]
                    v = p.vertices
                    shapes.append(v)
                plys.append(shapes)
            plyList.append(plys)
        return plyList

    @staticmethod
    def _cleanContours(plyList, writeFile):
        js = json.load(open(writeFile, 'r'))

        newPlys = []
        for (clusterId, clusterFeatures) in enumerate(js['features']):
            clusterGeom = shply.shape(clusterFeatures['geometry']).buffer(0.0)
            newClusterContours = []
            for clusterCounters in plyList[clusterId]:
                newPolygons = []
                for polygon in clusterCounters:
                    if len(polygon) < 3: continue
                    shplyPoly = shply.Polygon(polygon).buffer(0.0)
                    newPolygon = shplyPoly.intersection(clusterGeom)
                    if newPolygon.geom_type == 'Polygon':
                        newPolygon = [newPolygon]
                    for p in newPolygon:
                        newCoords = p.exterior.coords
                        if len(newCoords) > 0:
                            newPolygons.append(newCoords)
                if len(newPolygons) > 0:
                    newClusterContours.append(newPolygons)
            newPlys.append(newClusterContours)

        return newPlys

    @staticmethod
    def _gen_contour_polygons(newPlys):
        countryGroup = []
        for plys in newPlys:
            contourList = []
            for group in plys:
                contour = Contour(group)
                contour.createHoles()
                contourList.append(contour)
            countryGroup.append(contourList)

        featureAr = []
        for clusterNum, contourList in enumerate(countryGroup):
            for index, contour in enumerate(contourList):
                geoPolys = []
                for polygon in contour.polygons:
                    geoPolys.append(polygon.points)
                newMultiPolygon = MultiPolygon(geoPolys)
                newFeature = Feature(geometry=newMultiPolygon, properties={"contourNum": index, "clusterNum": clusterNum, "identity": str(index) + str(clusterNum)})
                featureAr.append(newFeature)

        return featureAr

    def makeContourFeatureCollection(self, outputfilename):
        featureAr = self._gen_contour_polygons(self.newPlys)
        collection = FeatureCollection(featureAr)
        textDump = dumps(collection)
        with open(outputfilename, "w") as writeFile:
            writeFile.write(textDump)


class Contour:
    def __init__(self, shapes):
        self.shapes = shapes
        self.polygons = self._generatePolygons(self.shapes)

    @staticmethod
    def _generatePolygons(shapes):
        polys = set()
        for group in shapes:
            points = []
            for pt in group:
                points.append((pt[0], pt[1]))
            polys.add(Polygon(points))
        return polys

    def createHoles(self):
        toRemove = set()
        for poly in self.polygons:
            path = mplPath.Path(poly.points[0])
            for otherPolys in self.polygons:
                if poly is not otherPolys \
                   and path.contains_points(otherPolys.points[0]).all():
                    poly.children.add(otherPolys)
                    toRemove.add(otherPolys)
        for poly in toRemove:
            self.polygons.remove(poly)
        self.collapseHoles()

    def collapseHoles(self):
        for poly in self.polygons:
            poly.collapseChildren()


class Polygon:

    def __init__(self, points):
        self.points = [points]
        self.children = set()

    def collapseChildren(self):
        for child in self.children:
            self.points.append(child.points[0])
