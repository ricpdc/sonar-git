'''
Created on 28 ene. 2020

@author: Alarcos
'''

import csv
import json
import pymongo
import statistics as stats
from pymongo import MongoClient
from objdict import ObjDict
import datetime
from dateutil.relativedelta import relativedelta

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'sonar-git'
COLLECTION_COMMITS = 'commits'
COLLECTION_PROJECTS = 'projects'
COLLECTION_METRICS = 'measures'
COLLECTION_ISSUES = 'issues'
COLLECTION_PROJECTS_ANALYSES = "analyses"


def dataToCsv(csvWriter, projectId, version, date1, date2, lastdate):
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collCommits = connection[DB_NAME][COLLECTION_COMMITS]
    collMeasures = connection[DB_NAME][COLLECTION_METRICS]
    
    # print('> {} and <= {} : {}'.format(date1, date2, version))
    commitsVersion = collCommits.find({'commit.committer.date':{'$gt':date1, '$lte':date2}})
    commitsVersion = list(commitsVersion)
    commitsAccumulated = collCommits.find({'commit.committer.date':{'$gt':lastdate, '$lt':date2}})
    commitsAccumulated = list(commitsAccumulated)
    # print('version: {}, accumulated: {}'.format(len(list(commitsVersion)), len(list(commitsAccumulated))))
    
    pipeline = [
    {"$match":  {'commit.committer.date': {'$gt':date1, '$lte':date2}}},
    {"$group": { '_id': "$commit.author.name", 'count': { '$sum': 1 } } }]
    commiters = collCommits.aggregate(pipeline)
    commiters = list(commiters);
    
    percentageCommiters = []
    for c in commiters:
        percentageCommiters.append(c['count'] / len(commitsVersion))
    harmonicMeanCommiters = stats.harmonic_mean(percentageCommiters)
    
#     print(len(commiters))
#     print(str(commiters).encode('utf-8'))
    
    changes = 0
    additions = 0
    deletions = 0
    files = set([])
    for c in commitsVersion:
        changes += c['stats']['total']
        additions += c['stats']['additions']
        deletions += c['stats']['deletions']
        for f in list(c['files']):
            files.add(f['filename'])

    collMeasures.find({'project' : projectId})
    
    csvWriter.writerow([projectId, version, date1, date2, len(commitsVersion), len(commitsAccumulated), len(commiters), str(harmonicMeanCommiters), changes, additions, deletions, len(files)])
    
#     for commit in commitsVersion:
#         print(str(commit).encode('utf-8'))


def preprocess(projectId):
    analysisDates = getAnalysisDates(projectId);
    # print(analysisDates)
    
    with open('sonar-git.csv', mode='w', newline='') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvWriter.writerow(['project', 'version', 'from', 'to', 'commits', 'accumulated_commits', 'committers', 'commiters_weigth', 'changes', 'additions', 'deletions', 'changed_files'])
    
        date1 = analysisDates[0]['date']
        lastdate = analysisDates[len(analysisDates) - 1]['date']
        date2 = datetime.datetime.now().isoformat()
        
        for i in range(1, len(analysisDates)):
            date2 = date1;
            date1 = analysisDates[i]['date']
            version = analysisDates[i - 1]['events'][0]['name']
            dataToCsv(csvWriter, projectId, version, date1, date2, lastdate)
        
        version = analysisDates[len(analysisDates) - 1]['events'][0]['name']
        date2 = date1
        date1 = (datetime.datetime.now() - relativedelta(years=10)).isoformat()
        dataToCsv(csvWriter, projectId, version, date1, date2, lastdate)
    

def getAnalysisDates(projectId):
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collAnalyses = connection[DB_NAME][COLLECTION_PROJECTS_ANALYSES]
     
    analysisDates = collAnalyses.find({"events.category": "VERSION", "projectId": projectId}, {"_id":0, "date": 1, "events.name": 1})
#     print(list(analysisDates))
#     for a in analysisDates:
#         print(a)
    return list(analysisDates)


def main():
    preprocess('monica')


main()
