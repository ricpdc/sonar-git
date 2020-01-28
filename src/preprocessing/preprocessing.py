'''
Created on 28 ene. 2020

@author: Alarcos
'''


import csv
import json
import pymongo
from pymongo import MongoClient
from objdict import ObjDict
import datetime


MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'sonar-git'
COLLECTION_COMMITS = 'commits'
COLLECTION_PROJECTS = 'projects'
COLLECTION_METRICS = 'measures'
COLLECTION_ISSUES = 'issues'
COLLECTION_PROJECTS_ANALYSES = "analyses"



def preprocessGit():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collCommits = connection[DB_NAME][COLLECTION_COMMITS]
    
    analysisDates = getAnalysisDates();
    print(analysisDates)
    
    date1 = analysisDates[0]['date']
    lastdate = analysisDates[len(analysisDates)-1]['date']
    print(lastdate)
    
    date2= datetime.datetime.now().isoformat()
    
    
    for i in range(1, len(analysisDates)):
        version = analysisDates[i-1]['events'][0]['name']
        print('>= {} and < {} : {}'.format(date1, date2, version))
        commits = collCommits.find({'commit.committer.date': {'$gte': date1, '$lt': date2}})
        print(len(list(commits)))
        date2 = date1;
        date1 = analysisDates[i]['date']
    version = analysisDates[len(analysisDates)-1]['events'][0]['name']
    print('>= {} and < {} : {}'.format(date1, date2, version)) 
    commits = collCommits.find({'commit.committer.date': {'$gte': date1, '$lt': date2}})
    print(len(list(commits)))  
    
    
    
    collCommits
    

def getAnalysisDates():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collAnalyses = connection[DB_NAME][COLLECTION_PROJECTS_ANALYSES]
     
    analysisDates = collAnalyses.find({"events.category": "VERSION"}, {"_id":0, "date": 1, "events.name": 1})
#     print(list(analysisDates))
#     for a in analysisDates:
#         print(a)
    return list(analysisDates)


def main():
    preprocessGit()

main()