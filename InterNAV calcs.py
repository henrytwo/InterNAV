#database of ref points and their respective db and freqs to each access point
#database of access points and db and frequencies
#the floor and building you're on (buildingname-floor#)
#floorplan map and location of each AP and ref point
#take ref points and model out a graph using adjacent ref points
#NEED REF POINT AT EACH CORNER/INTERSECTION
#Find nearest ref points to location
#go through points in a line and find most accurate points in the adjacent ref points
#that's their location
#use map to get dist between points to model as graph
#shortest dist is easy
#Ref points need unique ID's

from math import *


class RefPoint:
    def __init__(self, ID, signalList, pos):
        self.ID = ID #Random unique ID
        self.signalList = signalList #Contains AP db's and freqs
        self.pos = pos #XY pos on map, go by 0-1 scale

    def getError(self, locList):
        tot = 0
        n = 0
        #sig is mac address
        for sig in locList.keys()+self.signalList.keys():
            if sig not in self.signalList.keys():
                tot += locList[sig]
            elif sig not in locList.keys():
                tot += sigList[sig]
            else:
                tot += abs(sigList[sig]-locList[sig])
            n += 1
        return tot/n



floorPlan = None
scale = None
refPoints = None
curLocation = None 
graph = None    

        

#rp = ref point list
#fp = floor plan
#sc = scale of pixels in a meter
#pairs = list of all ref point ID pairs that make an edge
def Initialize(rp, fp, sc, pairs):
    floorPlan = fp
    scale = sc #How many pixels are in a meter

    #List of all ref points (~75)?
    #each ref point contains 3 things: an ID, a signal list to all AP's, and a location scaled from 0 to 1 (ignore pixel coords currently there)
    refPoints = []
    for i in range(len(rp)):
        refPoints.append(RefPoint(i, rp[i][0], rp[i][1]))
    #refPoints = [
    #             RefPoint(0, {"00-D0-56-F2-B5-12":250, "00-D0-56-F2-B5-12":250}, (232, 356)),
    #             RefPoint(1, {"25-D5-56-F2-B8-12":450, "00-D0-56-F2-B5-12":250}, (335, 358)),
    #             RefPoint(2, {"35-D5-56-F2-B8-12":750, "00-D0-56-F2-B5-12":250}, (385, 328)),
    #             RefPoint(3, {"27-D5-56-F2-B8-12":0, "00-D0-56-F2-B5-12":250}, (435, 158)),
    #             RefPoint(4, {"29-D5-56-F2-B8-12":0, "00-D0-56-F2-B5-12":250}, (255, 258)),
    #             RefPoint(5, {"45-D5-56-F2-B8-12, "00-D0-56-F2-B5-12":250}, (319, 458))
    #            ]

    # address:[(address, dist), (address, dist)]
    # Ref points and what each ref point is connected to
    # [N:[nodes], M:[nodes]]
    graph = []
    for i in range(len(refPoints)):
        graph.append([])
    for pair in pairs:
        a = pair[0]
        b = pair[1]
        graph[a].append(b)
        graph[b].append(a)
    
#Mac Address:(Db, f)
#This is your current location signals to each AP
#locSigs = {1:(1, 1), 2:(3, 5), 4:(9, 2)}
def findLocation(locSigs):
    nodeBreadth = 2 #Number of nodes whose paths are being checked

    #Gets nodes whose avg error / AP signal are lowest
    temp = []
    for r in refPoints:
        temp.append((r.getError(locSigs), r.ID, r.pos))
    temp.sort()
    topNodeIDs = temp[:nodeBreadth]

    pointA = topNodeIDs[0][2]
    pointB = topeNodeIDs[1][2]
    totError = topNodeIDs[0][0] + topNodeIDs[1][0]+2
    loc = (pointA[0] + pointB[0]*((topNodeIDs[0][0]+1)/totError), pointA[1] + pointB[1]*((topNodeIDs[0][0]+1)/totError))
    return loc

    


def getPath(destination):
    pass


