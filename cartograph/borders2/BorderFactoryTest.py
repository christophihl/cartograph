import unittest
from BorderProcessor import BorderProcessor
from BorderBuilder import BorderBuilder
from Noiser import NoisyEdgesMaker
from Vertex import Vertex
from matplotlib import pyplot as plt
import matplotlib.path as mplPath
import math
import random
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d


class BorderProcessorTest(unittest.TestCase):

    def test_makeNewRegionFromProcessed(self):
        processor = BorderProcessor({}, 5, 0.1, 13)
        region = [(1, 1), (2, 2), (3, 3), (4, 5), (5, 5)]
        processed = [[(1, 2), (3, 4)]]
        stopStartList = [(1, 2)]
        processedRegion = processor.makeNewRegionFromProcessed(region, processed, stopStartList)
        self.assertEqual([tuple(point) for point in processedRegion], [(1, 1), (1, 2), (3, 4), (4, 5), (5, 5)])

        stopStartList = [(4, 0)]
        processedRegion = processor.makeNewRegionFromProcessed(region, processed, stopStartList)
        self.assertEqual([tuple(point) for point in processedRegion], [(2, 2), (3, 3), (4, 5), (1, 2), (3, 4)])

        stopStartList = [(0, 4)]
        processedRegion = processor.makeNewRegionFromProcessed(region, processed, stopStartList, reverse=True)
        self.assertEqual([tuple(point) for point in processedRegion], [(2, 2), (3, 3), (4, 5), (3, 4), (1, 2)])

        region = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)]
        processed = [[(1, 2), (3, 4), (5, 6)], [(-1, 2), (-2, 3), (-3, 4), (-5, 6)]]
        stopStartList = [(1, 1), (9, 9)]
        processedRegion = processor.makeNewRegionFromProcessed(region, processed, stopStartList)
        self.assertEquals([tuple(point) for point in processedRegion],
                          [(0, 0),
                           (1, 2), (3, 4), (5, 6),
                           (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8),
                           (-1, 2), (-2, 3), (-3, 4), (-5, 6)])

        stopStartList = [(9, 2), (3, 3)]
        processedRegion = processor.makeNewRegionFromProcessed(region, processed, stopStartList)
        self.assertEquals([tuple(point) for point in processedRegion],
                          [(-1, 2), (-2, 3), (-3, 4), (-5, 6),
                           (4, 4), (5, 5), (6, 6), (7, 7), (8, 8),
                           (1, 2), (3, 4), (5, 6)])

        processed = [[(1, 2), (2, 3), (3, 4), (5, 6)], [(-1, 2)], [(-3, 2)], [(-7, 5), (5, 6)]]
        stopStartList = [(0, 4), (6, 6), (7, 7), (8, 9)]
        processedRegion = processor.makeNewRegionFromProcessed(region, processed, stopStartList)
        self.assertEquals([tuple(point) for point in processedRegion],
                          [(1, 2), (2, 3), (3, 4), (5, 6),
                           (5, 5),
                           (-1, 2),
                           (-3, 2),
                           (-7, 5), (5, 6)])

        processed = [[(-3, 2)], [(-7, 5), (5, 6)], [(1, 2), (2, 3), (3, 4), (5, 6)], [(-1, 2)]]
        stopStartList = [(4, 4), (2, 1), (0, 8), (6, 6)]
        # [[6, 6], [8, 0], [1, 2], [4, 4]]
        processedRegion = processor.makeNewRegionFromProcessed(region, processed, stopStartList, reverse=True)
        self.assertEquals([tuple(point) for point in processedRegion],
                          [(5, 6), (-7, 5),
                           (3, 3),
                           (-3, 2),
                           (5, 5),
                           (-1, 2),
                           (7, 7),
                           (5, 6), (3, 4), (2, 3), (1, 2)])

    def test_Noiser(self):
        points = [(0, 0), (1, 0), (0.5, math.sqrt(3)/2)]  # , (10, 5), (10,10)]
        vertices = [Vertex(None, point, True) for point in points]
        center = (0.5, 1/(2*math.sqrt(3)))
        circular = True
        regionPoints = [(center[0], -center[1]), center, (1, 1/math.sqrt(3)), center, (0.1, 0.3), center]
        for i in range(len(vertices) - 1):
            regionPts = [regionPoints[2*i], regionPoints[2*i + 1]]
            vertices[i].addRegionPoints(regionPts)
            vertices[i+1].addRegionPoints(regionPts)
        if circular:
            vertices[-1].addRegionPoints([regionPoints[-1], regionPoints[-2]])
            vertices[0].addRegionPoints([regionPoints[-1], regionPoints[-2]])
        maker = NoisyEdgesMaker(vertices, 0.001)
        pointsDict = {0: (-3.5645326384944758, 4.3235963816080876, True, ((-3.7859823546892883, 4.9354556312011777), (-3.6315628970293714, 4.970835643825799), (-3.0, 4.0))), 1: (-3.3495160514721061, 4.4634722704599632, True, ((-3.6315628970293714, 4.970835643825799), (-3.2102954361437774, 5.0270196384686923), (-3.0, 4.0))), 2: (-2.6837791924572265, 4.5997904262960745, True, ((-3.2102954361437774, 5.0270196384686923), (-3.0, 4.0), (-2.1035341299985939, 4.2489915920736561))), 3: (-2.6162582311893843, 4.3566888951070144, True, ((-3.0, 4.0), (-2.5455559643105907, 3.8375685791100747), (-2.1035341299985939, 4.2489915920736561))), 4: (-2.3029308940245201, 4.0200584200247516, True, ((-2.5455559643105907, 3.8375685791100747), (-2.1035341299985939, 4.2489915920736561), (-2.0, 4.0))), 5: (-1.725205182621355, 4.2602847200768883, True, ((-2.1035341299985939, 4.2489915920736561), (-2.0, 4.0), (-1.4154286894154584, 4.0428017289701721))), 6: (-1.691705677977704, 3.8027599937482153, True, ((-2.0, 4.0), (-1.4154286894154584, 4.0428017289701721), (-1.3977125939059807, 3.5847758760345894))), 7: (-1.2283946157702661, 3.8206805171773128, True, ((-1.4154286894154584, 4.0428017289701721), (-1.3977125939059807, 3.5847758760345894), (-1.0, 4.0))), 8: (-1.2137759380474145, 3.962567732332182, True, ((-1.4154286894154584, 4.0428017289701721), (-1.0445239259002674, 4.098417217921746), (-1.0, 4.0))), 9: (-0.60831812490482828, 4.2364767025037731, True, ((-1.0445239259002674, 4.098417217921746), (-1.0, 4.0), (-0.15353233744776773, 4.2865347651129966))), 10: (-0.55343237832448877, 4.0743357853380218, True, ((-1.0, 4.0), (-0.45295612129868434, 3.6329142504251593), (-0.15353233744776773, 4.2865347651129966))), 11: (-0.36581474597163427, 3.9883880830645224, True, ((-0.45295612129868434, 3.6329142504251593), (-0.15353233744776773, 4.2865347651129966), (0.0, 4.0))), 12: (0.188854694250154, 4.2855935395630134, True, ((-0.15353233744776773, 4.2865347651129966), (0.0, 4.0), (0.52462905003207361, 4.2186208034707313))), 13: (0.19197211237353129, 4.3167228176787615, True, ((-0.15353233744776773, 4.2865347651129966), (-0.029680526477780411, 4.5834712966890123), (0.52462905003207361, 4.2186208034707313))), 14: (0.45003763573826477, 4.7087962659186058, True, ((-0.029680526477780411, 4.5834712966890123), (0.52462905003207361, 4.2186208034707313), (0.86339414782362667, 4.9826068884097037))), 15: (0.86348789395662817, 4.5254650247894235, True, ((0.52462905003207361, 4.2186208034707313), (0.86339414782362667, 4.9826068884097037), (1.1777934208356928, 4.193515136951163))), 16: (0.85526036636302738, 4.3114126362676908, True, ((0.52462905003207361, 4.2186208034707313), (1.0, 4.0), (1.1777934208356928, 4.193515136951163))), 17: (1.2201041430854596, 3.9762097981017788, True, ((1.0, 4.0), (1.1777934208356928, 4.193515136951163), (1.4409795720289384, 3.9912381845346889))), 18: (1.2124926821805491, 3.5931272296944416, True, ((1.0, 4.0), (1.4409795720289384, 3.9912381845346889), (1.6304746923143156, 3.4034178983452978))), 19: (1.124371716994063, 3.5, True, ((1.0, 3.0), (1.0, 4.0), (1.6304746923143156, 3.4034178983452978))), 20: (1.5, 2.9129558278794621, True, ((1.0, 3.0), (1.6304746923143156, 3.4034178983452978), (2.0, 3.0))), 21: (2.2559235044386359, 3.6053714760454687, True, ((1.6304746923143156, 3.4034178983452978), (2.0, 3.0), (2.163465427634236, 4.2560810642391989))), 22: (2.4728882879140492, 3.5771358453030695, True, ((2.0, 3.0), (2.163465427634236, 4.2560810642391989), (2.5372612598066393, 2.8337885258959936))), 23: (2.5214043756763425, 3.5898864651017086, True, ((2.163465427634236, 4.2560810642391989), (2.5372612598066393, 2.8337885258959936), (3.1973710767703629, 3.9290096778983532))), 24: (2.5284160127195676, 3.5856604232317566, True, ((2.5372612598066393, 2.8337885258959936), (3.0, 3.0), (3.1973710767703629, 3.9290096778983532))), 25: (3.1231838701111667, 3.4593000900355015, True, ((3.0, 3.0), (3.19067318898135, 2.9885814581537549), (3.1973710767703629, 3.9290096778983532))), 26: (3.0664580918065978, 2.5120613626722528, True, ((3.0, 3.0), (3.026065657058286, 2.0212770485596927), (3.19067318898135, 2.9885814581537549))), 27: (3.2548619148018516, 2.4800004230130064, True, ((3.026065657058286, 2.0212770485596927), (3.19067318898135, 2.9885814581537549), (3.6981331878643573, 2.2225408333589396))), 28: (3.6108841856889891, 2.71584569719165, True, ((3.19067318898135, 2.9885814581537549), (3.6981331878643573, 2.2225408333589396), (4.1116023274609379, 2.7002437882682866))), 29: (3.8307953804667276, 2.5255046252808375, True, ((3.6981331878643573, 2.2225408333589396), (4.1116023274609379, 2.7002437882682866), (4.1404173321777051, 2.4092266670065001))), 30: (3.9486339179457, 2.2463290944024945, True, ((3.6981331878643573, 2.2225408333589396), (4.0, 2.0), (4.1404173321777051, 2.4092266670065001))), 31: (4.3975783803118249, 2.0922834547022742, True, ((4.0, 2.0), (4.1404173321777051, 2.4092266670065001), (4.6731296645418183, 1.7911916177781197))), 32: (4.2138489199895703, 1.5, True, ((4.0, 1.0), (4.0, 2.0), (4.6731296645418183, 1.7911916177781197))), 33: (4.5661760303831089, 1.200247292439466, True, ((4.0, 1.0), (4.3390084098948734, 0.64432540250219716), (4.6731296645418183, 1.7911916177781197))), 34: (4.2022415225669585, 0.85336601480931862, True, ((3.9744276845016273, 0.75087692149180718), (4.0, 1.0), (4.3390084098948734, 0.64432540250219716))), 35: (4.1233375245017072, 0.58338509737292088, True, ((3.9744276845016273, 0.75087692149180718), (4.3380586438475355, 0.51917845828944209), (4.3390084098948734, 0.64432540250219716))), 36: (4.0295020743605701, 0.43611836852252084, True, ((3.9744276845016273, 0.75087692149180718), (4.1517009201877109, 0.14086665021394218), (4.3380586438475355, 0.51917845828944209))), 37: (3.8223268291010593, 0.37591179855071449, True, ((3.4226594757620834, 0.3126700377369005), (3.9744276845016273, 0.75087692149180718), (4.1517009201877109, 0.14086665021394218))), 38: (3.8162265166632579, 0.35002534395151219, True, ((3.4226594757620834, 0.3126700377369005), (4.0, 0.0), (4.1517009201877109, 0.14086665021394218))), 39: (3.5, -0.23388216515852733, True, ((3.0, 0.0), (3.4226594757620834, 0.3126700377369005), (4.0, 0.0))), 40: (3.5, -0.44731425922592583, True, ((3.0, 0.0), (3.5836715394498615, -1.1129636564260803), (4.0, 0.0))), 41: (3.5223494376761311, -0.4556745564630737, True, ((3.5836715394498615, -1.1129636564260803), (4.0, 0.0), (4.1218056934662535, -0.73215522213468009))), 42: (3.6913825174280985, -0.69454130725437668, True, ((3.5836715394498615, -1.1129636564260803), (3.9221695531247267, -1.0598032149559033), (4.1218056934662535, -0.73215522213468009))), 43: (3.7139814801686906, -0.70831087031016349, True, ((3.9221695531247267, -1.0598032149559033), (4.0, -1.0), (4.1218056934662535, -0.73215522213468009))), 44: (4.1615849198755814, -0.91186401704649012, True, ((4.0, -1.0), (4.0550811534867162, -1.0619792580027818), (4.1218056934662535, -0.73215522213468009))), 45: (3.9885475595245596, -1.0656428409879302, True, ((3.9221695531247267, -1.0598032149559033), (4.0, -1.0), (4.0550811534867162, -1.0619792580027818))), 46: (3.9827529804963913, -1.4195727750316012, True, ((3.9221695531247267, -1.0598032149559033), (4.0550811534867162, -1.0619792580027818), (4.191993508862538, -1.7184421266189034))), 47: (3.8159772396352492, -1.4878956289101195, True, ((3.5836715394498615, -1.1129636564260803), (3.9221695531247267, -1.0598032149559033), (4.191993508862538, -1.7184421266189034))), 48: (3.7090273813426009, -1.5953477541760619, True, ((3.5836715394498615, -1.1129636564260803), (4.0, -2.0), (4.191993508862538, -1.7184421266189034))), 49: (4.1982704086646052, -1.9289611757227689, True, ((4.0, -2.0), (4.191993508862538, -1.7184421266189034), (4.3968619916161238, -1.8588252171313933))), 50: (4.2198865393922551, -1.989727132059276, True, ((4.0, -2.0), (4.3968619916161238, -1.8588252171313933), (4.4310626372789397, -2.0518582651809476))), 51: (4.1838198210087141, -2.2895253356852203, True, ((4.0, -2.0), (4.1259602217469169, -2.6275592295073924), (4.4310626372789397, -2.0518582651809476))), 52: (3.7585092711989736, -2.3748913197173414, True, ((3.3181431112702349, -2.3046138774909961), (4.0, -2.0), (4.1259602217469169, -2.6275592295073924))), 53: (3.6402127458122648, -2.6707988369510023, True, ((3.3181431112702349, -2.3046138774909961), (4.0, -3.0), (4.1259602217469169, -2.6275592295073924))), 54: (3.5, -2.808283643629137, True, ((3.0, -3.0), (3.3181431112702349, -2.3046138774909961), (4.0, -3.0))), 55: (2.60238179643531, -2.39761820356469, True, ((2.0, -2.0), (3.0, -3.0), (3.3181431112702349, -2.3046138774909961))), 56: (2.6373642357176834, -2.2462401319702581, True, ((2.0, -2.0), (3.068453750436527, -1.7161182574317815), (3.3181431112702349, -2.3046138774909961))), 57: (2.5020734796771249, -1.7370424837411158, True, ((2.0, -2.0), (2.7189388405009343, -1.2134072580095987), (3.068453750436527, -1.7161182574317815))), 58: (2.3131005147042369, -1.564322857597795, True, ((1.9378342653097302, -1.9477570068140446), (2.0, -2.0), (2.7189388405009343, -1.2134072580095987))), 59: (1.8697184630708399, -2.0919184126640986, True, ((1.7494589616664769, -1.9872287485454017), (1.9378342653097302, -1.9477570068140446), (2.0, -2.0))), 60: (1.8559724221937048, -2.3615824598074555, True, ((1.4670793899589434, -2.3458335586263868), (1.7494589616664769, -1.9872287485454017), (2.0, -2.0))), 61: (1.9457971157768839, -2.5, True, ((1.4670793899589434, -2.3458335586263868), (2.0, -3.0), (2.0, -2.0))), 62: (2.5, -2.5, True, ((2.0, -3.0), (2.0, -2.0), (3.0, -3.0))), 63: (2.5, -2.7835522905098986, True, ((2.0, -3.0), (2.8893351830535909, -3.1646923253791552), (3.0, -3.0))), 64: (2.390346584660294, -3.3756784869132894, True, ((2.0, -3.0), (2.6986718083449244, -3.8211449145206204), (2.8893351830535909, -3.1646923253791552))), 65: (2.2442322330901465, -3.5, True, ((2.0, -4.0), (2.0, -3.0), (2.6986718083449244, -3.8211449145206204))), 66: (1.9065437715492803, -3.5, True, ((1.6493232766352968, -3.9388299028466935), (2.0, -4.0), (2.0, -3.0))), 67: (1.7802202807107566, -4.2241889405573732, True, ((1.6493232766352968, -3.9388299028466935), (2.0, -4.0), (2.082033211088179, -4.3106340742323779))), 68: (1.5699869375951323, -4.468860902629058, True, ((1.6493232766352968, -3.9388299028466935), (1.7444934857082206, -4.9755901992838325), (2.082033211088179, -4.3106340742323779))), 69: (1.3734123232966633, -4.4869056205889422, True, ((1.0, -4.0), (1.6493232766352968, -3.9388299028466935), (1.7444934857082206, -4.9755901992838325))), 70: (1.3562533441190556, -4.5, True, ((1.0, -5.0), (1.0, -4.0), (1.7444934857082206, -4.9755901992838325))), 71: (1.2237712753085042, -4.5, True, ((0.75053147645739493, -4.7758943211386491), (1.0, -5.0), (1.0, -4.0))), 72: (0.60807978491806891, -4.3020405061864073, True, ((0.23839997059180718, -4.6309276559002708), (0.75053147645739493, -4.7758943211386491), (1.0, -4.0))), 73: (0.58596584156635645, -4.2753465108455888, True, ((0.23839997059180718, -4.6309276559002708), (0.24293323485603224, -3.9153901022094661), (1.0, -4.0))), 74: (0.57787734240879507, -4.275295266429425, True, ((0.090133628734760052, -4.213445834839689), (0.23839997059180718, -4.6309276559002708), (0.24293323485603224, -3.9153901022094661))), 75: (0.15692010740919041, -4.0594896547264643, True, ((0.0, -4.0), (0.090133628734760052, -4.213445834839689), (0.24293323485603224, -3.9153901022094661))), 76: (-0.11393266683674161, -4.1738650109567619, True, ((-0.28648342379582559, -4.289778473852035), (0.0, -4.0), (0.090133628734760052, -4.213445834839689))), 77: (-0.18526838858580361, -4.1033404425374638, True, ((-0.28648342379582559, -4.289778473852035), (-0.12865352551643205, -3.8988939210394067), (0.0, -4.0))), 78: (-0.56422465945780842, -3.9503269011895217, True, ((-1.0, -4.0), (-0.28648342379582559, -4.289778473852035), (-0.12865352551643205, -3.8988939210394067))), 79: (-0.5693212865089079, -3.9064034491242516, True, ((-1.0, -4.0), (-0.46044360342211821, -3.4793318875378692), (-0.12865352551643205, -3.8988939210394067))), 80: (-0.68015488939702995, -3.791549134134089, True, ((-1.0, -4.0), (-0.97009037008810584, -3.5431742656523744), (-0.46044360342211821, -3.4793318875378692))), 81: (-1.0056960889809163, -3.7702350616803275, True, ((-1.1818840284834016, -3.9178229415505594), (-1.0, -4.0), (-0.97009037008810584, -3.5431742656523744))), 82: (-1.2464283751481497, -4.3030523566806647, True, ((-1.6366698612953554, -4.3197633547801857), (-1.1818840284834016, -3.9178229415505594), (-1.0, -4.0))), 83: (-1.5961174081732141, -3.9073876937728924, True, ((-2.0, -4.0), (-1.6366698612953554, -4.3197633547801857), (-1.1818840284834016, -3.9178229415505594))), 84: (-1.6255282192054294, -3.6145875535060599, True, ((-2.1619748189875532, -3.5830136068712353), (-2.0, -4.0), (-1.1818840284834016, -3.9178229415505594))), 85: (-1.5759744997377085, -3.4695284435739664, True, ((-2.1619748189875532, -3.5830136068712353), (-1.5650895893747245, -2.8727397245318604), (-1.1818840284834016, -3.9178229415505594))), 86: (-1.6430230956783869, -3.413183535534468, True, ((-2.1619748189875532, -3.5830136068712353), (-2.0, -3.0), (-1.5650895893747245, -2.8727397245318604))), 87: (-1.7571003398357798, -3.023325970658203, True, ((-2.0, -3.0), (-1.8657058337859516, -2.8048100845105814), (-1.5650895893747245, -2.8727397245318604))), 88: (-2.1852568659842366, -2.7287465937265729, True, ((-2.1774511069021711, -2.4003602558037063), (-2.0, -3.0), (-1.8657058337859516, -2.8048100845105814))), 89: (-2.2105333356949699, -2.7362266474957915, True, ((-2.4476194961683344, -2.9764157801437081), (-2.1774511069021711, -2.4003602558037063), (-2.0, -3.0))), 90: (-2.2287218185000581, -3.0814371127513493, True, ((-2.4476194961683344, -2.9764157801437081), (-2.2235340709711213, -3.3241689830667767), (-2.0, -3.0))), 91: (-2.5723343905412754, -3.3028543956455003, True, ((-2.8840047342461226, -3.1448114539363452), (-2.4476194961683344, -2.9764157801437081), (-2.2235340709711213, -3.3241689830667767))), 92: (-2.6423017820962773, -3.5605040729799167, True, ((-2.8840047342461226, -3.1448114539363452), (-2.2235340709711213, -3.3241689830667767), (-2.1619748189875532, -3.5830136068712353))), 93: (-2.6711989144976203, -3.6081181568433007, True, ((-2.8840047342461226, -3.1448114539363452), (-2.1989698054919389, -3.8003135950957372), (-2.1619748189875532, -3.5830136068712353))), 94: (-2.6720615925988449, -3.6090197017727572, True, ((-3.0, -4.0), (-2.8840047342461226, -3.1448114539363452), (-2.1989698054919389, -3.8003135950957372))), 95: (-3.2452990183283275, -3.5312674588976396, True, ((-3.7694814114304025, -3.6027840460848015), (-3.0, -4.0), (-2.8840047342461226, -3.1448114539363452))), 96: (-3.284742529980293, -3.4550045771600786, True, ((-3.7694814114304025, -3.6027840460848015), (-2.9357724289455804, -3.0875397173312802), (-2.8840047342461226, -3.1448114539363452))), 97: (-3.3607523243069459, -3.3320142893479665, True, ((-3.7694814114304025, -3.6027840460848015), (-3.0, -3.0), (-2.9357724289455804, -3.0875397173312802))), 98: (-3.4747370391677985, -3.1865075861724117, True, ((-3.9375162310688872, -2.9720413753114858), (-3.7694814114304025, -3.6027840460848015), (-3.0, -3.0))), 99: (-3.472433577964857, -3.1092672966569492, True, ((-3.9375162310688872, -2.9720413753114858), (-3.1200450385510345, -2.7761679946504945), (-3.0, -3.0))), 100: (-2.7355152955952771, -2.7140450697109588, True, ((-3.1200450385510345, -2.7761679946504945), (-3.0, -3.0), (-2.4476194961683344, -2.9764157801437081))), 101: (-2.6769745246282515, -2.5174670672524115, True, ((-3.1200450385510345, -2.7761679946504945), (-2.4476194961683344, -2.9764157801437081), (-2.1774511069021711, -2.4003602558037063))), 102: (-2.7067764855162788, -2.4427183471475726, True, ((-3.1200450385510345, -2.7761679946504945), (-3.0, -2.0), (-2.1774511069021711, -2.4003602558037063))), 103: (-3.0409641628192978, -2.3910316338566098, True, ((-3.1556529058813103, -2.0149594419480463), (-3.1200450385510345, -2.7761679946504945), (-3.0, -2.0))), 104: (-3.0991896432294879, -1.7851958511010271, True, ((-3.1556529058813103, -2.0149594419480463), (-3.0, -2.0), (-2.8879468962047321, -1.6786317411125307))), 105: (-3.1606993579671681, -1.7362361006913452, True, ((-3.4363663556069337, -1.7777074649350224), (-3.1556529058813103, -2.0149594419480463), (-2.8879468962047321, -1.6786317411125307))), 106: (-3.4779945861993928, -2.1116556829427395, True, ((-3.7884145633871631, -2.2416316794018289), (-3.4363663556069337, -1.7777074649350224), (-3.1556529058813103, -2.0149594419480463))), 107: (-3.6953683090804401, -1.9467019530609289, True, ((-4.0, -2.0), (-3.7884145633871631, -2.2416316794018289), (-3.4363663556069337, -1.7777074649350224))), 108: (-3.7399878441488226, -1.8335669296362096, True, ((-4.0, -2.0), (-3.727392584337986, -1.5251068065548088), (-3.4363663556069337, -1.7777074649350224))), 109: (-4.1290698873847935, -1.6102184972917153, True, ((-4.24635652753107, -1.2167308866528925), (-4.0, -2.0), (-3.727392584337986, -1.5251068065548088))), 110: (-3.9487065898215681, -1.3066862106576267, True, ((-4.24635652753107, -1.2167308866528925), (-4.0, -1.0), (-3.727392584337986, -1.5251068065548088))), 111: (-4.237099020074897, -0.97887249300674617, True, ((-4.372215636493225, -0.78289847217773811), (-4.24635652753107, -1.2167308866528925), (-4.0, -1.0))), 112: (-4.6176914928092501, -1.0892861640414455, True, ((-5.0, -1.0), (-4.372215636493225, -0.78289847217773811), (-4.24635652753107, -1.2167308866528925))), 113: (-4.6886887424344401, -0.88398607419974118, True, ((-5.0, -1.0), (-4.6460624222082103, -0.55450629198145496), (-4.372215636493225, -0.78289847217773811))), 114: (-4.2599031535429948, -0.36986358901694827, True, ((-4.6460624222082103, -0.55450629198145496), (-4.372215636493225, -0.78289847217773811), (-4.2232655626195381, 0.056598127278217447))), 115: (-4.2146049914632, -0.37790074436993049, True, ((-4.372215636493225, -0.78289847217773811), (-4.2232655626195381, 0.056598127278217447), (-4.0, 0.0))), 116: (-4.0373017447019075, 0.3215165516801769, True, ((-4.2232655626195381, 0.056598127278217447), (-4.0, 0.0), (-3.8203030364508281, 0.56167457003367893))), 117: (-4.3744421717901165, 0.59049555500074602, True, ((-4.2232655626195381, 0.056598127278217447), (-4.0, 1.0), (-3.8203030364508281, 0.56167457003367893))), 118: (-4.6869763125488495, 0.66445990973856028, True, ((-5.3845035649251285, 0.35144339520894619), (-4.2232655626195381, 0.056598127278217447), (-4.0, 1.0))), 119: (-4.7181702886537851, 0.73105112290704943, True, ((-5.3845035649251285, 0.35144339520894619), (-5.2271831671170945, 1.3046432703019697), (-4.0, 1.0))), 120: (-4.6679602923037002, 0.9333101857143723, True, ((-5.2271831671170945, 1.3046432703019697), (-4.2840351574826379, 1.483964318792955), (-4.0, 1.0))), 121: (-4.7842052456740154, 1.5447063231107807, True, ((-5.2271831671170945, 1.3046432703019697), (-5.0, 2.0), (-4.2840351574826379, 1.483964318792955))), 122: (-5.1223742301112969, 1.6551910536441232, True, ((-5.3433398088942656, 1.3635699387098814), (-5.2271831671170945, 1.3046432703019697), (-5.0, 2.0))), 123: (-5.6165279902186356, 1.9217759745633367, True, ((-6.2371062983434271, 1.9550674804397215), (-5.3433398088942656, 1.3635699387098814), (-5.0, 2.0))), 124: (-5.6294194097114492, 2.2767094705083295, True, ((-6.2371062983434271, 1.9550674804397215), (-5.5878792287375205, 2.9630121280546646), (-5.0, 2.0))), 125: (-5.3566911950652436, 2.4431988093342585, True, ((-5.5878792287375205, 2.9630121280546646), (-5.1781826041435801, 2.9833732961434176), (-5.0, 2.0))), 126: (-4.8402190544934651, 2.5367811257705464, True, ((-5.1781826041435801, 2.9833732961434176), (-5.0, 2.0), (-4.6025633720309305, 2.0296482988664657))), 127: (-4.7678991507998711, 1.5673299343721809, True, ((-5.0, 2.0), (-4.6025633720309305, 2.0296482988664657), (-4.2840351574826379, 1.483964318792955))), 128: (-4.3101529658530433, 1.8345268474788543, True, ((-4.6025633720309305, 2.0296482988664657), (-4.2840351574826379, 1.483964318792955), (-4.0, 2.0))), 129: (-4.2770490444041114, 2.5073212842037598, True, ((-4.6025633720309305, 2.0296482988664657), (-4.0, 2.0), (-3.7018812180757337, 2.4497623581533841))), 130: (-3.576153551730525, 2.0427423643716138, True, ((-4.0, 2.0), (-3.7018812180757337, 2.4497623581533841), (-3.5961223360325993, 1.6172144932794588))), 131: (-3.4580398333215858, 2.0577463963797658, True, ((-3.7018812180757337, 2.4497623581533841), (-3.5961223360325993, 1.6172144932794588), (-3.0, 2.0))), 132: (-3.1746456940519896, 2.5, True, ((-3.7018812180757337, 2.4497623581533841), (-3.0, 2.0), (-3.0, 3.0))), 133: (-3.351781126134429, 2.7259533397554288, True, ((-3.7018812180757337, 2.4497623581533841), (-3.2461699226558354, 3.159194388590155), (-3.0, 3.0))), 134: (-2.8697223731352475, 3.471383923033637, True, ((-3.2461699226558354, 3.159194388590155), (-3.0, 3.0), (-2.5455559643105907, 3.8375685791100747))), 135: (-2.9157140953452725, 3.5188834343637847, True, ((-3.2461699226558354, 3.159194388590155), (-3.0, 4.0), (-2.5455559643105907, 3.8375685791100747))), 136: (-3.3229666188620679, 3.6381182739688875, True, ((-3.486825352748455, 3.1815921127649496), (-3.2461699226558354, 3.159194388590155), (-3.0, 4.0))), 137: (-3.4164417383508958, 3.6937214258056721, True, ((-3.9297645233915617, 3.7547951911171467), (-3.486825352748455, 3.1815921127649496), (-3.0, 4.0))), 138: (-3.5792877599152177, 4.311198930899379, True, ((-3.9297645233915617, 3.7547951911171467), (-3.7859823546892883, 4.9354556312011777), (-3.0, 4.0))), 139: (1.498827998010855, 4.9503953487678665, True, ((1.0, 5.0), (1.43414270169826, 4.4532979685048737), (1.4845874589036914, 5.4514813693963777))), 140: (1.0450649145198672, 5.4374318346082182, True, ((0.8624989085351622, 5.8374907176594348), (1.0, 5.0), (1.4845874589036914, 5.4514813693963777))), 141: (0.87837896398484383, 5.4100649639705667, True, ((0.8624989085351622, 5.8374907176594348), (0.86339414782362667, 4.9826068884097037), (1.0, 5.0))), 142: (0.90792579882197655, 5.1780035222275682, True, ((0.86339414782362667, 4.9826068884097037), (0.979877262955549, 4.9909583425061257), (1.0, 5.0))), 143: (1.1386962604919391, 4.6644103761747209, True, ((0.979877262955549, 4.9909583425061257), (1.0, 5.0), (1.43414270169826, 4.4532979685048737))), 'n12': (-3.4034845609758806, 4.4217388966226405), 'n13': (-3.3899852744005741, 4.4275626504830621), 'n10': (-3.4207165847139476, 4.4143691234762104), 'n11': (-3.4154959760976582, 4.4182902255703471), 'n16': (-3.3610327837117371, 4.4504449981973675), 'n14': (-3.3841661822077707, 4.4358059462540993), 'n15': (-3.371102441707063, 4.4449809959799147), 'n8': (-3.4367827015735077, 4.4053236504721536), 'n9': (-3.4262028370042135, 4.408083226133428), 'n1': (-3.5049470430087402, 4.3499067847664543), 'n2': (-3.5041710823269367, 4.353524980528789), 'n3': (-3.5004787648475513, 4.3621356512644756), 'n4': (-3.4953591494667102, 4.3730821401415856), 'n5': (-3.4889271687349752, 4.3789607022534822), 'n6': (-3.4690808141810692, 4.3809943367306552), 'n7': (-3.4570243449832909, 4.3935343260340254)}
        commonPoints = [139, 140, 141, 142, 143, 139]
        processor = BorderProcessor({}, 5, 0.1, 13)
        idGenerator = processor.idGenerator
        noised = maker.makeNoisyEdges_new(commonPoints, pointsDict, circular, idGenerator)[0]
        x = []
        y = []
        for lineId in noised:
           x.append(pointsDict[lineId][0])
           y.append(pointsDict[lineId][1])
           x.append(pointsDict[lineId][0])
           y.append(pointsDict[lineId][1])
        plt.plot(x, y)
        xPoints = zip(*points)[0]
        yPoints = zip(*points)[1]
        plt.scatter(xPoints, yPoints, c="r")
        xRegion = zip(*regionPoints)[0]
        yRegion = zip(*regionPoints)[1]
        plt.scatter(xRegion, yRegion, c="g")
        #debug = maker.debug
        #plt.scatter(zip(*debug)[0], zip(*debug)[1], c="y", s=0.1)
        plt.show()

    @staticmethod
    def generatePolygon(ctrX, ctrY, aveRadius, irregularity, spikeyness, numVerts):
        '''Start with the centre of the polygon at ctrX, ctrY,
            then creates the polygon by sampling points on a circle around the centre.
            Random noise is added by varying the angular spacing between sequential points,
            and by varying the radial distance of each point from the centre.

            Params:
            ctrX, ctrY - coordinates of the "centre" of the polygon
            aveRadius - in px, the average radius of this polygon, this roughly controls how large the polygon is, really only useful for order of magnitude.
            irregularity - [0,1] indicating how much variance there is in the angular spacing of vertices. [0,1] will map to [0, 2pi/numberOfVerts]
            spikeyness - [0,1] indicating how much variance there is in each vertex from the circle of radius aveRadius. [0,1] will map to [0, aveRadius]
            numVerts - self-explanatory

            Returns a list of vertices, in CCW order.
            '''

        irregularity = np.clip(irregularity, 0, 1) * 2 * math.pi / numVerts
        spikeyness = np.clip(spikeyness, 0, 1) * aveRadius

        # generate n angle steps
        angleSteps = []
        lower = (2 * math.pi / numVerts) - irregularity
        upper = (2 * math.pi / numVerts) + irregularity
        sum = 0
        for i in range(numVerts):
            tmp = random.uniform(lower, upper)
            angleSteps.append(tmp)
            sum = sum + tmp

        # normalize the steps so that point 0 and point n+1 are the same
        k = sum / (2 * math.pi)
        for i in range(numVerts):
            angleSteps[i] = angleSteps[i] / k

        # now generate the points
        points = []
        angle = random.uniform(0.1, 2 * math.pi)
        for i in range(numVerts):
            r_i = np.clip(random.gauss(aveRadius, spikeyness), aveRadius/2, 2 * aveRadius)
            x = ctrX + r_i * math.cos(angle)
            y = ctrY + r_i * math.sin(angle)
            points.append((int(x), int(y)))

            angle = angle + angleSteps[i]

        return points

    class TestBorderBuilder(BorderBuilder):
        def __init__(self, x, y, clusterLabels, minNumInCluster=5, blurRadius=5, minBorderNoiseLength=0.01):
            self.x = x
            self.y = y
            self.clusterLabels = clusterLabels
            self.minNumInCluster = minNumInCluster
            self.blurRadius = blurRadius
            self.minBorderNoiseLength = minBorderNoiseLength

    @staticmethod
    def _addRandomPoints(x, y, waterLevel):
        length = len(x)
        np.random.seed(42)
        randX = np.random.uniform(np.min(x) - 3,
                                    np.max(x) + 3,
                                    int(length * waterLevel))
        randY = np.random.uniform(np.min(x) - 3,
                                    np.max(x) + 3,
                                    int(length * waterLevel))
        x = np.append(x, randX)
        y = np.append(y, randY)
        return x, y

    def test_BorderBuilder(self):
        plt.clf()
        polygon = self.generatePolygon(0, 0, 5, 0.1, 0.1, 50)
        polygon.append(polygon[0])
        x, y = zip(*polygon)
        plt.plot(x, y)
        x, y = self._addRandomPoints(x, y, 10)
        points = zip(x, y)

        vor = Voronoi(points)
        voronoi_plot_2d(vor)
        plt.show()

        labels = map(int, mplPath.Path(polygon).contains_points(points))
        waterX, waterY, insideX, insideY = [], [], [], []
        for i in range(len(x)):
            if labels[i]:
                insideX.append(x[i])
                insideY.append(y[i])
            else:
                waterX.append(x[i])
                waterY.append(y[i])
        plt.scatter(insideX, insideY, c="g")
        plt.scatter(waterX, waterY, c="b")
        plt.show()
        borders = self.TestBorderBuilder(x, y, labels).build()
        region = borders[0]
        for section in region:
            section.append(section[0])
            x, y = zip(*section)
            plt.plot(x, y)
        plt.show()


if __name__ == '__main__':
    unittest.main()