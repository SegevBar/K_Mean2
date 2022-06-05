import math
from random import randint
import sys
import pandas as pd
import numpy as np
import mykmeanssp

def validateArgs(k, epsilon, maxIterations = 300):
    if '.' in str(k) or int(k) <= 0:
        print("Invalid Input!")
        quit()
    if maxIterations != 300:
        if '.' in maxIterations or int(maxIterations) < 0:
            print("Invalid Input!")
            quit()
    if int(epsilon) < 0: ##TO SELF - Check if I need to add more testings
        print("Invalid Input!")
        quit()
    return int(maxIterations)

#get k
try:
    k = int(sys.argv[1])
except:
    print("Invalid Input!")
    quit()

#read the input file names and get the epsilon and max iterations
if len(sys.argv) == 6:
    maxIterations = sys.argv[2]
    epsilon = sys.argv[3]
    maxIterations = validateArgs(k, epsilon, maxIterations)
    inputFileOne = sys.argv[4]
    inputFileTwo = sys.argv[5]
elif len(sys.argv) == 5:
    epsilon = sys.argv[2]
    inputFileOne = sys.argv[3]
    inputFileTwo = sys.argv[4]
    maxIterations = validateArgs(k, epsilon)
else:
    print("Invalid Input!")
    quit()

#prepare data structs
#clusters = [[] for i in range(k)]
#dataPoints = []

#open input files and save their lengths
fOne = open(inputFileOne, 'r')
fTwo = open(inputFileTwo, 'r')
lenFOne = len(fOne.readline().split(","))
lenFTwo = len(fTwo.readline().split(","))
fOne.close
fTwo.close

#convert input files to dataFrames and set columns titles
fileOneDataPoints = pd.read_csv(fOne, names = ["col" + str(i) for i in range(lenFOne)])
fileTwoDataPoints = pd.read_csv(fTwo, names = ["col" + str(i) for i in range(lenFTwo)])
fileOneDataPoints = pd.DataFrame(fileOneDataPoints)
fileTwoDataPoints = pd.DataFrame(fileTwoDataPoints)

#merge data files by first column
mergedDataPoints = fileOneDataPoints.merge(fileTwoDataPoints, on='col0')
mergedDataPoints.sort_values(by='col0')
mergedDataPoints.set_index('col0')

#prepare other required data structs
distances = [-1.0 for i in range(len(mergedDataPoints))]
probs = [0.0 for i in range(len(mergedDataPoints))]
mergedDataPointsNP = mergedDataPoints.to_numpy()
centroids = np.array([[0.0 for i in range(len(mergedDataPointsNP[0]))] for i in range(k)])
centroidsLoc = [0 for i in range(k)]

#reassure the our input file(s) is valid for clustering
if len(mergedDataPointsNP) <= k:
    print("Invalid Input!")
    quit()

#methods for main loop:

def minDistance(D):
    for idx in range(len(mergedDataPointsNP)):
        curDistance = pow(np.linalg.norm(mergedDataPointsNP[idx] - centroids[D-1]), 2)
        
        if curDistance < distances[idx] or distances[idx] == -1.0:
            distances[idx] = curDistance

def calcProbability():
    sum = 0.0
    for dist in distances:
        sum += dist
    for i in range(len(distances)):
        probs[i] = distances[i] / sum

#main stuff:
def kmeanspp():
    np.random.seed(0)

    #choose a random datapoint to be the first centroid
    randomIndex = (int)(np.random.choice(mergedDataPoints.index))
    centroidsLoc[0] = randomIndex
    centroids[0] = np.ndarray.copy(mergedDataPointsNP[randomIndex])
    
    #algorithm loop
    i = 1
    while (i != k):
        minDistance(i)
        calcProbability()
        randomIndex = (int)(np.random.choice(mergedDataPoints.index, p = probs))
        centroidsLoc[i] = randomIndex
        centroids[i] = np.ndarray.copy(mergedDataPointsNP[randomIndex])

        i += 1

#call Algorithm 1:
kmeanspp()

#set arguments for c extension use
dim = len(centroids[0])
dataPointsSize = len(mergedDataPointsNP)

#transform to 1D list of data points for the c extension
dataPoints1D = []
for vec in mergedDataPointsNP:
    for i in range(dim):
        dataPoints1D.append(vec[i])

for centroid in centroidsLoc:
    for j in range(dim):
        print(dataPoints1D[centroid+j])
        print(" ,")
    print("\n")

#use c module and call the fit() method
finalCentroids = np.array(mykmeanssp.fit(k, maxIterations, dim, dataPointsSize, centroidsLoc, dataPoints1D))

print(*centroidsLoc, sep=",")
for centroid in finalCentroids:
    print(*[np.round(num, decimals=4) for num in centroid], sep=",")
