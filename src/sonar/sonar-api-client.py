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
    
    collMetrics.drop();
    collProject.drop();
    
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
    
    measures_dict = measuresComponent();
    projectId = measures_dict['component'].get('id');
    
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collMetrics = connection[DB_NAME][COLLECTION_METRICS]
    collMetrics.drop();
    
   
    url = 'https://sonarcloud.io/api/measures/search_history'
    query = {'component': ''+componentName, 'p': '1', 'ps': '1000', 'metrics': ','.join(getAllMetricsKeys()), 'from': '2017-01-01T00:00:00+0000', 'to': '2021-01-01T00:00:00+0000'}
    r = requests.get(url, params=query)
    measures_dict = r.json()
    print(measures_dict)
        
    #insert measures by adding project id    
    for measure in measures_dict['measures']:
        measure['projectId'] = projectId
        collMetrics.insert_one(measure)
        #print(measure)



def getAllMetricsKeys():
    url = 'https://sonarcloud.io/api/metrics/search'
    query = {'ps': '500'}
    r = requests.get(url, params=query)
    metrics_dict = r.json()
    print(metrics_dict)
    keys = []
    validTypes = ['INT', 'FLOAT', 'PERCENT', 'BOOL', 'MILLISEC', 'DATA', 'LEVEL', 'DISTRIB', 'RATING', 'WORK_DUR']
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
  

def main ():
    #getAllMetricsKeys()
    measuresComponentHistory('monica')



main();   