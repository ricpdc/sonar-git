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
COLLECTION_REPOS = 'repos'
COLLECTION_COMMITS = 'commits'

####
# inputs
####
username = 'ricpdc'
token = '3347e6495fb0fa8a1facf8fcc67d548578e0649d'

repos_url = 'https://api.github.com/user/repos'

gh_session = requests.Session()
gh_session.auth = (username, token)


def importCommits(user, project):
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collRepos = connection[DB_NAME][COLLECTION_REPOS]
    collCommits= connection[DB_NAME][COLLECTION_COMMITS]
    
    url = 'https://api.github.com/repos/' + user + '/' + project + '/commits'
    query = {'username': 'ricpdc', 'token' : '3347e6495fb0fa8a1facf8fcc67d548578e0649d'}
    r = requests.get(url, auth=gh_session.auth, params=query)
    commitsDict = r.json()
    print(commitsDict)
    # print the repo names
    collCommits.insert_many(commitsDict)
#     for repo in commitsDict:
#         print (repo)


def main():
    importCommits('ricpdc', 'archirev')

    
main()
    
# make more requests using "gh_session" to create repos, list issues, etc.
