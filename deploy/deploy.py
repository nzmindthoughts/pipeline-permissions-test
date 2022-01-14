import sys
import os
# import unittest
# import re
# import yaml
import json
from pathlib import Path
# from pprint import pprint, pformat

import boto3
import botocore
import logging

# Set up our logger
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='[%(asctime)s] %(levelname)s %(name)s@%(lineno)d: %(message)s')
logger = logging.getLogger(os.path.basename(__file__))

DEPLOY_DIR = Path(__file__).parents[0]
ROOT_DIR = Path(DEPLOY_DIR).parents[0]
TEMPLATE_DIR = ROOT_DIR / 'templates'
# PARAMETER_DIR = ROOT_DIR / 'parameters'
CONFIG_DIR = ROOT_DIR / 'config'
CONFIG_FILE_NAME = 'default.json'
STACK_PREFIX = 'managed-security-pipeline'


client = boto3.client('cloudformation')

def get_json_attribute(file,attributename):
    with open(file, 'r') as myfile:
        data = myfile.read()
    obj = json.loads(data)
    value = obj['Parameters'][attributename]
    return value

def get_security_templates(template_dir):
    files = []
    for p in template_dir.glob("*"):
        if p.suffix in ['.yaml', '.yml', '.template'] and p.stat().st_size != 0:
            files.append(p)
    return files

def get_file_name(file):
    file = str(file)
    file_name =file.split('\\')[-1] #change slash direction for linux
    return file_name

def get_file_names(file_list):
    file_names = []
    for f in file_list:
        filename = get_file_name(f)
        file_names.append(filename)
    return file_names



def get_stack(stackname):
    response = client.describe_stacks(StackName=stackname)
    return response

def create_stack(stackname):
    response = client.create_stack(
        StackName=stackname,
        TemplateBody='string', #yamlencoded
        Parameters=[ #need to figure out how to pass this in
            {
                'ParameterKey': 'string',
                'ParameterValue': 'string',
                'UsePreviousValue': True|False,
                'ResolvedValue': 'string'
            },
        ],
        Capabilities=[ #set named iam capability for iam template
            'CAPABILITY_IAM'|'CAPABILITY_NAMED_IAM'|'CAPABILITY_AUTO_EXPAND',
        ],
        RoleARN='string',
        OnFailure='DELETE',
        Tags=[ #see what tags are needed
            {
                'Key': 'string',
                'Value': 'string'
            },
        ]
    )

def update_stack():
    response = client.update_stack(
        StackName='string',
        TemplateBody='string',
        TemplateURL='string',
        UsePreviousTemplate=True|False,
        StackPolicyDuringUpdateBody='string',
        StackPolicyDuringUpdateURL='string',
        Parameters=[
            {
                'ParameterKey': 'string',
                'ParameterValue': 'string',
                'UsePreviousValue': True|False,
                'ResolvedValue': 'string'
            },
        ],
        Capabilities=[
            'CAPABILITY_IAM'|'CAPABILITY_NAMED_IAM'|'CAPABILITY_AUTO_EXPAND',
        ],
        ResourceTypes=[
            'string',
        ],
        RoleARN='string',
        RollbackConfiguration={
            'RollbackTriggers': [
                {
                    'Arn': 'string',
                    'Type': 'string'
                },
            ],
            'MonitoringTimeInMinutes': 123
        },
        StackPolicyBody='string',
        StackPolicyURL='string',
        NotificationARNs=[
            'string',
        ],
        Tags=[
            {
                'Key': 'string',
                'Value': 'string'
            },
        ],
        DisableRollback=True|False,
        ClientRequestToken='string'
    )
    

if __name__ == "__main__":
    appid = get_json_attribute(str(CONFIG_DIR)+'\\'+CONFIG_FILE_NAME, 'AppId')
    logger.info('Getting CloudFormation templates')
    templates = get_security_templates(TEMPLATE_DIR)
    filenames = get_file_names(templates)
    for f in filenames:
        try:
            filenameprefix = f.split('.')[0]
            stackname = STACK_PREFIX + '-' + filenameprefix + '-' + appid
            logger.info('Checking if stack: %s already exists' % stackname)
            get_stack(stackname)
            logger.info('Stack: %s found!' % stackname)
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ValidationError':
                logger.warning(error.response['Error']['Message'])
            else:
                raise error