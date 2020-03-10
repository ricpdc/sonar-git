'''
Created on 22 ene. 2020

@author: Alarcos
'''

import requests
import json
import pymongo
import time
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
COLLECTION_COMMITS_INFO = 'commits_info'

####
# inputs
####
username = config['github.com']['user']
token = config['github.com']['token']
client_id = config['github.com']['client_id']
client_secret = config['github.com']['client_secret']

repos_url = 'https://api.github.com/repos/{}/{}/commits?page={}&per_page=100'
commit_info_url = 'https://api.github.com/repos/{}/{}/commits/{}'


def importCommits(user, project):
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collRepos = connection[DB_NAME][COLLECTION_REPOS]
    collCommits = connection[DB_NAME][COLLECTION_COMMITS]
    collCommitsInfo = connection[DB_NAME][COLLECTION_COMMITS_INFO]
    
    hasMorePages = True
    page = 1;
    while hasMorePages == True:
        remaining = checkRateLimit()
        if remaining < 500:
            print('\n\n\nWaiting for rate limit....\n\n')
            time.sleep(1200)
        url = repos_url.format(user, project, page)
        page += 1
        query = {'client_id': client_id, 'client_secret' : client_secret, 'since' : '2010-01-01T00:00:00Z'}
        r = requests.get(url, params=query)
        commits_dict = r.json()
        # print the commits
        #print(str(commits_dict).encode('utf-8'))
        
        if len(commits_dict) > 0: 
            #collCommits.insert_many(commits_dict)
            for commit in commits_dict:
                if 'sha' in commit:
                    sha=commit['sha']
                else:
                    print('\n\nError commit without sha. Commits Dict: ' + str(commits_dict))
                    if commit is not None:
                        print(str(commit).encode('utf-8'))
                    continue
                #print('\n'+sha)
                url_info = commit_info_url.format(user, project, str(sha))
                #print(url_info)
                query = {'client_id': client_id, 'client_secret' : client_secret}
                r2 = requests.get(url_info, params=query)
                commit_info = r2.json()

                if 'stats' in commit_info:
                    commit['stats'] = commit_info['stats']
                if 'files' in commit_info:
                    commit['files'] = commit_info['files']
                commit['projectId'] = project;
                #print(str(commit).encode('utf-8'))
                collCommits.insert_one(commit)
                #print (str(commit).encode('utf-8'))
                time.sleep(0.2)
                
        else:
            hasMorePages = False


def checkRateLimit():
    url = 'https://api.github.com/rate_limit'
    query = {'client_id': client_id, 'client_secret' : client_secret}
    r = requests.get(url, params=query)
    rate_limit = r.json()
    remaining = rate_limit['resources']['core']['remaining']
    print('request remaining: ' + str(remaining))
    return remaining


def main():
    # importCommits('ricpdc', 'archirev')
#     githubProjects = [['monicahq', 'monica'], ['simgrid', 'simgrid'], ['SonarSource', 'sonarqube'], ['apache', 'jmeter']]
    #githubProjects = [['jacoco', 'jacoco'], ['ant-media', 'Ant-Media-Server'], ['apache', 'sling-org-apache-sling-scripting-jsp'], ['dernasherbrezon', 'jradio']]
    
    checkRateLimit();
    
#     githubProjects = [['monicahq', 'monica'], ['simgrid', 'simgrid'], ['SonarSource', 'sonarqube'], ['apache', 'jmeter'], ['jacoco', 'jacoco'], ['ant-media', 'Ant-Media-Server'], ['apache', 'sling-org-apache-sling-scripting-jsp'], ['dernasherbrezon', 'jradio']]
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collRepos = connection[DB_NAME][COLLECTION_REPOS]
    collCommits = connection[DB_NAME][COLLECTION_COMMITS]
    collCommitsInfo = connection[DB_NAME][COLLECTION_COMMITS_INFO]
#     collRepos.drop();
#     collCommits.drop();
#     collCommitsInfo.drop();
#     
    
    #['SonarSource', 'sonar-dotnet'], 
    githubProjects = [['esig', 'dss'], ['apache', 'sling-org-apache-sling-scripting-sightly-compiler'], ['apache', 'sling-org-apache-sling-app-cms'], ['payara', 'Payara']]
    
    for project in githubProjects:
        importCommits(project[0], project[1])
    
    print('\n\nEnd of program!')

    
main()
    
# make more requests using "gh_session" to create repos, list issues, etc.
