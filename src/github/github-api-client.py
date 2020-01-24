'''
Created on 22 ene. 2020

@author: Alarcos
'''

import requests
import json
import pymongo
from pymongo import MongoClient
from objdict import ObjDict
import configparser

config = configparser.ConfigParser()
config.read('..\..\ConfigFile.ini')


MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'sonar-git'
COLLECTION_REPOS = 'repos'
COLLECTION_COMMITS = 'commits'

####
# inputs
####
username = config['github.com']['user']
token = config['github.com']['token']

repos_url = 'https://api.github.com/repos/{}/{}/commits?page={}&per_page=100'


def importCommits(user, project):
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collRepos = connection[DB_NAME][COLLECTION_REPOS]
    collCommits = connection[DB_NAME][COLLECTION_COMMITS]
    collCommits.drop();
    
    hasMorePages = True
    page = 1;
    while hasMorePages == True:
        url = repos_url.format(user, project, page)
        page += 1
        query = {'username': username, 'token' : token, 'since' : '2010-01-01T00:00:00Z'}
        r = requests.get(url, params=query)
        commits_dict = r.json()
        # print the commits
        # print(str(commits_dict).encode('utf-8'))
        
        if len(commits_dict) > 0: 
            collCommits.insert_many(commits_dict)
            for commit in commits_dict:
                print (str(commit).encode('utf-8'))
        else:
            hasMorePages = False


def main():
    # importCommits('ricpdc', 'archirev')
    importCommits('monicahq', 'monica')
    
    print('\End of program!')

    
main()
    
# make more requests using "gh_session" to create repos, list issues, etc.
