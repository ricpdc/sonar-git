'''
Created on 28 ene. 2020

@author: Alarcos
'''

import csv
import json
import pymongo
import statistics as stats
import math
from pymongo import MongoClient
from objdict import ObjDict
import datetime
from dateutil.relativedelta import relativedelta
import dateutil.parser
import sys
sys.path.append("../sonar")
from sonar_api_client import getAllMetricsKeys 

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'sonar-git'
COLLECTION_COMMITS = 'commits'
COLLECTION_PROJECTS = 'projects'
COLLECTION_METRICS = 'measures'
COLLECTION_ISSUES = 'issues'
COLLECTION_PROJECTS_ANALYSES = "analyses"


def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

def dataToCsv(csvWriter, projectGitHub, projectSonar, version, date1, date2, lastdate, metrics):
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collCommits = connection[DB_NAME][COLLECTION_COMMITS]
    collMeasures = connection[DB_NAME][COLLECTION_METRICS]
    
    print('> {} and <= {} : {} {}'.format(date1, date2, projectGitHub, version))
    commitsVersion = collCommits.find({"projectId": projectGitHub, 'commit.committer.date':{'$gt':date1, '$lte':date2}})
    commitsVersion = list(commitsVersion)
    
    versionDays = abs(dateutil.parser.isoparse(date2) - dateutil.parser.isoparse(date1)).days + 1
    commitsPerDay = len(commitsVersion)/versionDays
    commitsPerDay = round_up(commitsPerDay, 4)
    
    commitsAccumulated = collCommits.find({"projectId": projectGitHub, 'commit.committer.date':{'$gt':lastdate, '$lt':date2}})
    commitsAccumulated = list(commitsAccumulated)
    print('version: {}, accumulated: {}'.format(len(list(commitsVersion)), len(list(commitsAccumulated))))
    
    pipeline = [
    {"$match":  {"projectId": projectGitHub, 'commit.committer.date': {'$gt':date1, '$lte':date2}}},
    {"$group": { '_id': "$commit.author.name", 'count': { '$sum': 1 } } }]
    commiters = collCommits.aggregate(pipeline)
    commiters = list(commiters);
    
    percentageCommiters = []
    for c in commiters:
        percentageCommiters.append(c['count'] / len(commitsVersion))
    #print(len(percentageCommiters))
    harmonicMeanCommiters = 0
    if len(percentageCommiters) != 0:
        harmonicMeanCommiters = stats.harmonic_mean(percentageCommiters)
        harmonicMeanCommiters = round_up(harmonicMeanCommiters, 4)
    
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
    
    changesByCommit = 0
    if len(commitsVersion) != 0:
        changesByCommit = round_up(changes / len(commitsVersion), 4)
    
    csvRow = [projectGitHub, version, date1, date2, versionDays, len(commitsVersion), commitsPerDay, len(commitsAccumulated), len(commiters), str(harmonicMeanCommiters), changes, changesByCommit, additions, deletions, len(files)]
    
    for metric in metrics:
        measures = collMeasures.find({'projectId' : projectSonar, 'metric': metric }, {'metric': 1, '_id' : 0, 'history': {'$elemMatch': {'date': date2} }})
        value = 0;
        if measures.count() > 0 and measures[0] is not None and 'history' in measures[0] and 'value' in measures[0]['history'][0]:
            value = measures[0]['history'][0]['value']
        csvRow.append(value)
    
    csvWriter.writerow(csvRow)
    
#     for commit in commitsVersion:
#         print(str(commit).encode('utf-8'))


def preprocess(projectGitHub, projectSonar, csvWriter):
    analysisDates = getAnalysisDates(projectSonar);
    # print(analysisDates)
    metrics = getAllMetricsKeys()

    date1 = analysisDates[0]['date']
    lastdate = analysisDates[len(analysisDates) - 1]['date']
    date2 = datetime.datetime.now().isoformat()
    
    for i in range(1, len(analysisDates)):
        date2 = date1;
        date1 = analysisDates[i]['date']
        version = analysisDates[i - 1]['projectVersion']
        dataToCsv(csvWriter, projectGitHub, projectSonar, version, date1, date2, lastdate, metrics)
    
#     version = analysisDates[len(analysisDates) - 1]['projectVersion']
#     date2 = date1
#     date1 = (datetime.datetime.now() - relativedelta(years=10)).isoformat()
#     dataToCsv(csvWriter, projectGitHub, projectSonar, version, date1, date2, lastdate, metrics)
    

def getAnalysisDates(projectId):
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collAnalyses = connection[DB_NAME][COLLECTION_PROJECTS_ANALYSES]
     
    analysisDates = collAnalyses.find({"events.category": "VERSION", "projectId": projectId}, {"_id":0, "date": 1, "projectVersion": 1})
#     print(list(analysisDates))
#     for a in analysisDates:
#         print(a)
    return list(analysisDates)


def main():
    projects = [['monica', 'monica'], ['simgrid', 'simgrid_simgrid'], ['sonarqube', 'org.sonarsource.sonarqube:sonarqube'], ['jmeter', 'JMeter'], 
                ['jacoco', 'org.jacoco:org.jacoco.build'], ['Ant-Media-Server', 'io.antmedia:ant-media-server'], ['jradio', 'ru.r2cloud:jradio'],
                ['sonar-dotnet', 'sonaranalyzer-dotnet'], ['dss', 'eu.europa.ec.joinup.sd-dss:sd-dss'], ['sling-org-apache-sling-scripting-sightly-compiler', 'apache_sling-org-apache-sling-scripting-sightly-compiler'],
                ['sling-org-apache-sling-app-cms', 'apache_sling-org-apache-sling-app-cms'], ['Payara', 'fish.payara.server:payara-aggregator'],
                ['sling-org-apache-sling-scripting-jsp', 'apache_sling-org-apache-sling-scripting-jsp']]
                
    
    
    with open('sonar-git.csv', mode='w', newline='') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        metrics = getAllMetricsKeys()
        headerFields = ['project', 'version', 'from', 'to', 'days', 'commits', 'commitsPerDay', 'accumulated_commits', 'committers', 'committers_weight', 'changes', 'changes_by_commit', 'additions', 'deletions', 'changed_files']
        
        for m in metrics:
            headerFields.append(m)
                
        csvWriter.writerow(headerFields)            
        
        for project in projects:
            preprocess(project[0], project[1], csvWriter)


main()
