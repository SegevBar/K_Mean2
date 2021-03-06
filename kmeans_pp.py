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
    if float(epsilon) < 0: 
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
fileOneDataPoints = pd.read_csv(inputFileOne, names = ["col" + str(i) for i in range(lenFOne)])
fileTwoDataPoints = pd.read_csv(inputFileTwo, names = ["col" + str(i) for i in range(lenFTwo)])
fileOneDataPoints = pd.DataFrame(fileOneDataPoints)
fileTwoDataPoints = pd.DataFrame(fileTwoDataPoints)

#merge data files by first column
mergedDataPoints = fileOneDataPoints.merge(fileTwoDataPoints,how="inner", on='col0')
mergedDataPoints = mergedDataPoints.sort_values(by=["col0"])
mergedDataPoints = mergedDataPoints.set_index('col0')

if (mergedDataPoints.empty or len(mergedDataPoints.columns) == 0):
    print("Invalid Input!")
    quit()

#prepare other required data structs
mergedDataPointsNP = mergedDataPoints.to_numpy()
distances = [-1.0 for i in range(len(mergedDataPoints))]
probs = [0.0 for i in range(len(mergedDataPoints))]
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
    for i in range(len(mergedDataPointsNP)):
        probs[i] = distances[i] / sum

#main stuff:
def kmeanspp():
    np.random.seed(0)

    #choose a random datapoint to be the first centroid
    indexes = [i for i in range(len(mergedDataPoints))]
    key_indexes = mergedDataPoints.index.to_list()
    randomIndex = (int)(np.random.choice(indexes))
    centroidsLoc[0] = int(key_indexes[randomIndex])
    centroids[0] = np.ndarray.copy(mergedDataPointsNP[randomIndex])

    #algorithm loop
    i = 1
    while (i != k):
        minDistance(i)
        calcProbability()
        randomIndex = (int)(np.random.choice(indexes, p = probs))
        centroidsLoc[i] = int(key_indexes[randomIndex])
        centroids[i] = np.ndarray.copy(mergedDataPointsNP[randomIndex])

        i += 1

#call Algorithm 1:
kmeanspp()

#set arguments for c extension use
dim = len(centroids[0])
dataPointsSize = len(mergedDataPointsNP)
epsilon = float(epsilon)

#transform to 1D list of data points for the c extension
dataPoints1D = []
for vec in mergedDataPointsNP:
    for i in range(dim):
        dataPoints1D.append(vec[i])

#transform to 1D list of centroids for the c extension
centroids1D = []
for centroid in centroids:
    for i in range(dim):
        centroids1D.append(centroid[i])

#use c module and call the fit() method
finalCentroids = np.array(mykmeanssp.fit(k, maxIterations, epsilon, dim, dataPointsSize, centroids1D, dataPoints1D))

print(*centroidsLoc, sep=",")
for centroid in finalCentroids:
    print(*["{:.4f}".format(num) for num in centroid], sep=",")
