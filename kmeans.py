import math
import sys

def validateArgs(k, maxIterations = 200):
    if '.' in str(k) or int(k) <= 0:
        print("Invalid Input!")
        quit()
    if maxIterations != 200:
        if '.' in maxIterations or int(maxIterations) < 0:
            print("Invalid Input!")
            quit()
    return int(maxIterations)

#get and validate the k and max iterations arguments
try:
    k = int(sys.argv[1])
except:
    print("Invalid Input!")
    quit()

#read the input and output file names
if len(sys.argv) == 5:
    maxIterations = sys.argv[2]
    maxIterations = validateArgs(k, maxIterations)
    inputFile = sys.argv[3]
    outputFile = sys.argv[4]
elif len(sys.argv) == 4:
    inputFile = sys.argv[2]
    outputFile = sys.argv[3]
    maxIterations = validateArgs(k)
else:
    print("Invalid Input!")
    quit()

#prepare data structs
clusters = [[] for i in range(k)]
dataPoints = []

#read input file into the data points structure
f = open(inputFile, 'r')
lines = f.readlines()
for line in lines:
    dataPoints.append([float(x) for x in line.split(",")])
#reassure the our input file is valid for clustering
if len(dataPoints) <= k:
    print("Invalid Input!")
    quit()

#prepare clusters structure -- each index i in arr is the 0<=i<=k cluster
#clusters[i][0] will be the number of data points saved becide centroid
#clusters[i][1] is the centroid
#clusters[i][2] is the sum of points in that clusters, for recurring mean calculation
for i in range(k):
    clusters[i].append(0)
    clusters[i].append(list.copy(dataPoints[i]))
    clusters[i].append([0.0 for x in range(len(dataPoints[i]))])

#methods for main loop:
def calcEuclidianDistance(point, centroid):
    res = 0.0
    for x in range(len(point)):
        res += pow((point[x]-centroid[x]), 2)
    return res

def addToClusterElementsSum(point, clusterID, clusters):
    for i in range(len(point)):
        clusters[clusterID][2][i] += point[i]

def assignToCluster(point, clusters):
    minDist, clusterID = -1, -1
    for i in range(k):
        curCentroid = clusters[i][1]
        curDistance = calcEuclidianDistance(point, curCentroid)
        if (curDistance < minDist) or (minDist < 0): #smaller dist or first calc
            minDist = curDistance
            clusterID = i
    
    clusters[clusterID][0] += 1 #update num of elements
    addToClusterElementsSum(point, clusterID, clusters)

def calcEucNorm(point):
    res = 0.0
    for x in range(len(point)):
        res += pow(point[x], 2)
    res = math.sqrt(res)
    return res

def updateCentroidsGetIfConverged(clusters):
    con = True
    for i in range(k):
        newCentroid = []
        for j in range(len(clusters[i][2])):
            res = clusters[i][2][j] / clusters[i][0]
            newCentroid.append(res)
        normres = calcEuclidianDistance(newCentroid, clusters[i][1])
        deltaMuNorm = math.sqrt(normres)
        if deltaMuNorm >= 0.001:
            con = False
        clusters[i][1] = newCentroid
    #if no distantance is larger than epsilon then we reached convergence
    return con

convergence = False
#main loop:
counter = 0
while counter < maxIterations and not convergence:
    convergence = True
    for point in dataPoints:
        assignToCluster(point, clusters)
    convergence = updateCentroidsGetIfConverged(clusters)

    #re-init clusters for next iteration:
    for clus in clusters:
        clus[0] = 0
        clus[2] = [0.0 for x in clus[2]]
        
    counter += 1

#write to output file:
f = open(outputFile, 'w')
for i in range(k):
    for j in range(len(clusters[i][1])-1):
        f.write("{:.4f}".format(clusters[i][1][j]))
        f.write(",")
    f.write("{:.4f}".format(clusters[i][1][-1]))
    f.write("\n")
f.close()