'''
Created on 22 ene. 2020

@author: Alarcos
'''



import requests
import json
import pymongo
from pymongo import MongoClient
from objdict import ObjDict

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'sonar-git'
COLLECTION_PROJECTS = 'projects'
COLLECTION_METRICS = 'measures'
COLLECTION_ISSUES = 'issues'
COLLECTION_PROJECTS_ANALYSES = "analyses"


def measuresComponentTree():
    url = 'https://sonarcloud.io/api/measures/component_tree'
    query = {'component': 'monica', 'metricKeys': 'sqale_index', 'ps': 100, 'p': 1}
    r = requests.get(url, params=query)
    measures_dict = r.json()
    print(measures_dict)
    for row in measures_dict:
        print(row)



def measuresComponent():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collProject = connection[DB_NAME][COLLECTION_PROJECTS]
    collMetrics = connection[DB_NAME][COLLECTION_METRICS]
    
    
    url = 'https://sonarcloud.io/api/measures/component'
    query = {'component': 'monica', 'metricKeys': 'ncloc,complexity,violations'}
    r = requests.get(url, params=query)
    measures_dict = r.json()
    print(measures_dict)
    
    #extract, create and insert a dict with project information
    data = ObjDict()
    data.id = measures_dict['component'].get('id') 
    data.key = measures_dict['component'].get('key')
    data.name = measures_dict['component'].get('name')
    data.description = measures_dict['component'].get('description')
    data.qualifier = measures_dict['component'].get('qualifier')
    data.language = measures_dict['component'].get('language', '')
    data.path = measures_dict['component'].get('path', '')
    collProject.insert_one(data)
    print(data);
    
    #insert measures by adding project id    
    for measure in measures_dict['component']['measures']:
        measure['projectId'] = data.id
        collMetrics.insert_one(measure)
        print(measure)
    
    return measures_dict
    
keys = 'new_technical_debt,blocker_violations,bugs,classes,code_smells,cognitive_complexity,comment_lines,comment_lines_data,comment_lines_density,class_complexity,file_complexity,function_complexity,complexity_in_classes,complexity_in_functions,branch_coverage,new_branch_coverage,conditions_to_cover,new_conditions_to_cover,confirmed_issues,coverage,new_coverage,critical_violations,complexity,last_commit_date,development_cost,new_development_cost,directories,duplicated_blocks,new_duplicated_blocks'    
    
def measuresComponentHistory(componentName):
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collMetrics = connection[DB_NAME][COLLECTION_METRICS]
    
   
    url = 'https://sonarcloud.io/api/measures/search_history'
    query = {'component': ''+componentName, 'p': '1', 'ps': '1000', 'metrics': ','.join(getAllMetricsKeys()), 'from': '2010-01-01T00:00:00+0000', 'to': '2021-01-01T00:00:00+0000'}
    r = requests.get(url, params=query)
    measures_dict = r.json()
    print(measures_dict)
        
    #insert measures by adding project id    
    for measure in measures_dict['measures']:
        measure['projectId'] = componentName
        collMetrics.insert_one(measure)
        #print(measure)

def issuesComponent(componentName):
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collIssues = connection[DB_NAME][COLLECTION_ISSUES]
    
   
    url = 'https://sonarcloud.io/api/issues/search'
    query = {'componentKeys': ''+componentName, 'p': '1', 'ps': '500'}
    r = requests.get(url, params=query)
    issues_dict = r.json()
    print(issues_dict)
        
    #insert measures by adding project id    
    for issue in issues_dict['issues']:
        issue['projectId'] = componentName
        collIssues.insert_one(issue)
        #print(issue)


def getAllMetricsKeys():
    url = 'https://sonarcloud.io/api/metrics/search'
    query = {'ps': '500'}
    r = requests.get(url, params=query)
    metrics_dict = r.json()
    print(metrics_dict)
    keys = []
    validTypes = ['INT', 'FLOAT', 'PERCENT', 'BOOL', 'MILLISEC', 'LEVEL', 'DISTRIB', 'RATING', 'WORK_DUR']
    for metric in metrics_dict['metrics']:
        print(metric)
        key = metric['key']
        metricType = metric['type']
        if metricType in validTypes :
            keys.append(key)
    res = [ sub['key'] for sub in metrics_dict['metrics'] ] 
    print(keys)
    print(','.join(keys))
    return keys
  
  
  
def getProject(projectName):
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collProject = connection[DB_NAME][COLLECTION_PROJECTS]
    
    url = 'https://sonarcloud.io/api/projects/search'
    query = {'projects': projectName}
    r = requests.get(url, params=query)
    project_dict = r.json()
    print(project_dict)
    
    project = project_dict['components'][0]   
    collProject.insert_one(project)
    print(project);
        
    return project

def getProjectAnalyses(projectName):
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collProjectAnalyses = connection[DB_NAME][COLLECTION_PROJECTS_ANALYSES]
    
    url = 'https://sonarcloud.io/api/project_analyses/search'
    query = {'project': projectName}
    r = requests.get(url, params=query)
    project_dict = r.json()
    print(project_dict)
    
    for analysis in project_dict['analyses']:
        analysis['projectId'] = projectName
        collProjectAnalyses.insert_one(analysis)   


def main ():
    #getAllMetricsKeys()
    sonarProjects = ['monica', 'simgrid_simgrid']
    
    
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collProjectAnalyses = connection[DB_NAME][COLLECTION_PROJECTS_ANALYSES]
    collProjectAnalyses.drop();
    collProject = connection[DB_NAME][COLLECTION_PROJECTS]
    collProject.drop();
    collMetrics = connection[DB_NAME][COLLECTION_METRICS]
    collMetrics.drop();
    collIssues = connection[DB_NAME][COLLECTION_ISSUES]
    collIssues.drop();
    
    for project in sonarProjects:
        getProjectAnalyses(project)
        measuresComponentHistory(project)
        issuesComponent(project)



main();   