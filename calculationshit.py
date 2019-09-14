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
from queue import *

class RefPoint:
    def __init__(self, ID, signalList, pos):
        self.ID = ID #Random unique ID
        self.signalList = signalList #Contains AP db's and freqs
        self.pos = pos #XY pos on map, go by 0-1 scale

    def getError(self, locList):
        tot = 0
        n = 0
        #sig is mac address
        #print(locList)
        #print(self.signalList)
        for sig in set(locList.keys()) | set(self.signalList.keys()):
            if sig not in self.signalList.keys():
                tot += abs(110-locList[sig])
            elif sig not in locList.keys():
                tot += abs(110-self.signalList[sig])
            else:
                tot += abs(self.signalList[sig]-locList[sig])
            n += 1
        return tot/n



#rp = ref point list
#fp = floor plan
#sc = scale of pixels in a meter
#pairs = list of all ref point ID pairs that make an edge
#rlocs = list of all the positions of rps
def Initialize(rp, fp, sc, pairs):
    global floorPlan, scale, refPoints, curLocation, graph, closestNode, refCount
    floorPlan = fp
    scale = sc #How many pixels are in a meter



    #List of all  points (~75)?
    #each ref point contains 3 things: an ID, a signal list to all AP's, and a location scaled from 0 to 1 (ignore pixel coords currently there)
    refPoints = []
    refCount = len(rp)
    w = 0
    pairToIndex = {}
    for k in rp.keys():
        refPoints.append(RefPoint(w, rp[k]["aps"], rp[k]["location"]))
        pairToIndex[k] = w
        w += 1

    #Make edges list
    edges = []
    for i in range(len(pairs)):
        edges.append((pairToIndex[pairs[0]], pairToIndex[pairs[1]]))
        

    # address:[(address, dist), (address, dist)]
    # Ref points and what each ref point is connected to
    # [N:[nodes], M:[nodes]]
    graph = []
    for i in range(refCount):
        graph.append([])
    for pair in edges:
        a = pair[0]
        b = pair[1]
        dist = ((refPoints[a].pos[0]-refPoints[b].pos[0])**2+(refPoints[a].pos[1]-refPoints[b].pos[1])**2)**0.5
        graph[a].append((b, dist))
        graph[b].append((a, dist))


    
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
    pointB = topNodeIDs[1][2]
    totError = topNodeIDs[0][0] + topNodeIDs[1][0]+2
    curLocation = (pointA[0] + (pointB[0]-pointA[0])*((topNodeIDs[0][0]+1)/totError), pointA[1] + (pointB[1]-pointA[1])*((topNodeIDs[0][0]+1)/totError))
    closestNode = topNodeIDs[0]
    
    return curLocation

    

#Destination should be a ref point ID
def getPath(destination):
    lineSegList = [(closestNode[2], curLocation)]
    dists = [(99999, []) for i in range(refCount)]
    dists[closestNode[1]] = (0, [])
    points = Queue()
    points.put(closestNode[1])
    while not points.empty():
        cur = points.get()
        for edge in graph[cur]:
            if dists[edge[0]][0] > dists[cur][0]+edge[1]:
                dists[edge[0]][0] = dists[cur][0]+edge[1]
                dists[edge[0]][1] = (dists[cur][1]+[(cur, edge[0])])
                points.put(edge[0])
    return lineSegList
