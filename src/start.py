import json
import os

from utils import Jenkins, str_to_bool, GithubAction

JENKINS_URL = os.getenv('INPUT_JENKINS_URL')
if not JENKINS_URL:
    GithubAction.error('JENKINS_URL required.')

JENKINS_USER = os.getenv('INPUT_JENKINS_USER')
if not JENKINS_USER:
    GithubAction.error('JENKINS_USER required.')

JENKINS_TOKEN = os.getenv('INPUT_JENKINS_TOKEN')
if not JENKINS_TOKEN:
    GithubAction.error('JENKINS_TOKEN required.')

JOB_NAME = os.getenv('INPUT_JOB_NAME')
if not JOB_NAME:
    GithubAction.error('JOB_NAME required.')

JOB_PARAMS = json.loads(os.getenv('INPUT_JOB_PARAMS', '{}'))

WAIT_FOR_BUILD = str_to_bool(os.getenv('INPUT_ASYNC', 'false')) is False
DEBUG = str_to_bool(os.getenv('INPUT_DEBUG', 'false'))
TIMEOUT = int(os.getenv('INPUT_JOB_TIMEOUT', 60))

SLEEP = 1

jenkins = Jenkins(JENKINS_URL, JENKINS_USER, JENKINS_TOKEN, DEBUG, TIMEOUT, SLEEP)
jenkins.run_job(JOB_NAME, JOB_PARAMS, WAIT_FOR_BUILD)
