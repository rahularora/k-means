from __future__ import division
from pprint import pprint
import os
import re
import math
import random
import numpy
from heapq import heappush,heappop

currentfilePath = os.path.realpath(__file__)
dirPath = currentfilePath.split("/")
dirPath[-1] = "test/"
dirPath = "/".join(dirPath)

rssPoints = []

def normalizeVector(vector):
  squaresum = 0
  for index in range(0,len(vector)):
    squaresum = squaresum + vector[index]*vector[index]
  for index in range(0,len(vector)):
    vector[index] = vector[index]/math.sqrt(squaresum)
    
  return vector

class Parser:
  stopwords=[] 

  def __init__(self,):
    self.stopwords = ['and', 'is', 'it', 'an', 'as', 'are', 'have', 'in', 'their', 'said', 'from', 'for', 'also', 'by', 'to', 'other', 'which', 'new', 'has', 'was', 
                           'more', 'be', 'we', 'that', 'but', 'they', 'not', 'with', 'than', 'a', 'on', 'these', 'of', 'could', 'this', 'so', 'can', 'at', 'the', 'or', 'first'] 

  def clean(self, string):
    string = string.replace(".","")
    string = string.replace("\s+"," ")
    string = string.lower()
    return string

  def removeStopWords(self,list):
    wordList = []
    for word in list:
      if word not in self.stopwords:
        wordList.append(word)
    return wordList

  def removeNumbers(self, list):
    tempList = []
    for word in list:
      if re.search('^[a-zA-Z]+', word):
        tempList.append(word)
    return tempList
  
  def tokenise(self, string):
    string = self.clean(string)
    words = string.split(" ")	
    words = self.removeNumbers(words)
    return words
  
  def removeDuplicates(self,list):
    return set((item for item in list))


class VectorSpace:
  documentVectors = []

  #Mapping of vector index to keyword
  vectorKeywordIndex=[]
  
  #Unique VocabularyList
  uniqueVocabularyList=[]

  #Tidies terms
  parser=None

  def __init__(self, documents):
    self.documentVectors=[]
    self.parser = Parser()
    self.build(documents)

  def build(self,documents):
    self.vectorKeywordIndex = self.getVectorKeywordIndex(documents)
    #for keyword in self.vectorKeywordIndex:
      #print keyword, self.vectorKeywordIndex[keyword]
    self.documentVectors = [self.makeVector(document) for document in documents]

  def getVectorKeywordIndex(self, documentList):
    vocabularyString = " ".join(documentList)
			
    vocabularyList = self.parser.tokenise(vocabularyString)
    vocabularyList = self.parser.removeStopWords(vocabularyList)
    self.uniqueVocabularyList = self.parser.removeDuplicates(vocabularyList)
    print len(self.uniqueVocabularyList)
    vectorIndex={}
    offset=0
    for word in self.uniqueVocabularyList:
      vectorIndex[word]=offset
      offset+=1
    return vectorIndex  

  def makeVector(self, wordString):
    vector = [0] * len(self.vectorKeywordIndex)
    wordList = self.parser.tokenise(wordString)
    wordList = self.parser.removeStopWords(wordList)
    for word in wordList:
      vector[self.vectorKeywordIndex[word]] += 1; #Use simple Term Count Model
     
    squaresum = 0
    for index in range(0,len(vector)):
      if vector[index] != 0:
        vector[index] = 1 + math.log10(vector[index])
    
    vector = normalizeVector(vector)
      
    return vector

  def __str__(self):
    x = ""
    for v in self.documentVectors:
      x = x + str(v) + " "
    return x
  
  def getDocumentVectors(self):
    return self.documentVectors
    
  def getVectorKeywordIndexList(self):
    return self.vectorKeywordIndex

def findRandomCentroids(dVectors, k):
  centroids = []
  randList = []
  randIndex = random.randint(0, len(dVectors)-1) 
  randList.append(randIndex)
  while k>0:
    while randIndex in randList:
      randIndex = random.randint(0, len(dVectors)-1) 
      
    randList.append(randIndex)
    centroids.append(dVectors[randIndex])
    k = k-1
    
  return centroids

def kmeans(centroids,dVectors, k):
  centroids = centroids[0:k]
  terms = len(dVectors[0])
  #centroids = [dVectors[3],dVectors[1]]
  #centroids = [dVectors[25],dVectors[50]]
  
  count = 0
  oldRss = []
  while(count<100):
    dVectorsDict = {}
    clusters = {}
    for i in range(0,len(dVectors)):
      temp = []
      for j in range(0,len(centroids)):
        dotProduct = numpy.dot(centroids[j],dVectors[i])
        heappush(temp, (-dotProduct, j))
      dVectorsDict[i] = temp
  
    #print centroids
    
    for dVectorKey in dVectorsDict:
      temp = dVectorsDict[dVectorKey]
      distance,clusterNo = heappop(temp)
      #print dVectorKey, clusterNo
      if clusterNo not in clusters:
        clusters[clusterNo] = []
      clusters[clusterNo].append(dVectorKey)
    
    for clusterNo in clusters:
      #print clusterNo, len(clusters[clusterNo])
      clustorDocs = clusters[clusterNo]
      centroid = []
      for i in range(0,terms):
        asum = 0
        for doc in clustorDocs:
          asum = asum + dVectors[doc][i]
        centroid.append(asum/len(clustorDocs))
      centroids[clusterNo] = normalizeVector(centroid)    

    rss = [x for x in range(0,k)]
    for clusterNo in clusters:
      centroidVector = centroids[clusterNo]
      clustorDocs = clusters[clusterNo]
      rss[clusterNo] = 0
      for doc in clustorDocs:
        dotProduct = numpy.dot(centroidVector,dVectors[doc])
        rss[clusterNo]= rss[clusterNo] + 2*(1-dotProduct)

    if oldRss == rss:
      #for clusterNo in clusters:
      #  print clusterNo, len(clusters[clusterNo])
      #print rss
      print count
      print sum(rss)
      rssPoints.append(sum(rss))
      break
      
    oldRss = rss
    #print sum(rss)
    
    #for j in range(0,len(centroids)):
    #  for i in range(0,len(dVectors)):
    #    dotProduct = numpy.dot(centroids[j],DocumentVectors[i])
    #  heappush(temp, (-dotProduct, j))


    #print centroids
    count = count + 1

if __name__ == '__main__':
  documents = []
  filePathList = []
  for x in range(0,100):
    if x<10:
      x = "0" + str(x)
    else:
      x = str(x)
    filePath = dirPath + "file" + x + ".txt" 
    filePathList.append(filePath)
  
  for file in filePathList:
    #print file
    f = open(file,"r")
    documents.append(f.read())
  
  vectorSpace= VectorSpace(documents)
  documentVectors = vectorSpace.getDocumentVectors()
  #print DocumentVectors
  #for dVector in DocumentVectors:
  #  print dVector
  
  kFactorList = [x for x in range(2,16)]
  centroids = findRandomCentroids(documentVectors, 15)
  for kFactor in kFactorList:
    print "For k : ", str(kFactor)
    kmeans(centroids,documentVectors, kFactor)


