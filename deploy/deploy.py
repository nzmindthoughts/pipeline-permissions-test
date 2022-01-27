import sys
import os
import json
from pathlib import Path
from time import sleep

import boto3
import botocore
import logging
import argparse

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
STACK_EXECUTION_ROLE_NAME = 'GALocalSecurityPipelineStackExecutionRole'
SUCCESS_STATUSES = [
    'CREATE_COMPLETE',
    'UPDATE_COMPLETE'
]
FAILURE_STATUSES = [
    'CREATE_FAILED',
    'ROLLBACK_IN_PROGRESS',
    'ROLLBACK_FAILED',
    'ROLLBACK_COMPLETE',
    'DELETE_IN_PROGRESS',
    'DELETE_FAILED',
    'DELETE_COMPLETE',
    'UPDATE_FAILED',
    'UPDATE_ROLLBACK_FAILED',
    'UPDATE_ROLLBACK_COMPLETE'
]
CF_CHECK_PERIOD_SECONDS = 30
TIMEOUT_SECONDS = 900


client = boto3.client('cloudformation')
s3client = boto3.client('s3')

parser = argparse.ArgumentParser(description='Accept AWS account number')
parser.add_argument('--account_number', type=str, help='AWS account in which templates will be deployed', required=True)
args = vars(parser.parse_args())

def get_json_attribute(file,attributename):
    with open(file, 'r') as myfile:
        data = myfile.read()
    obj = json.loads(data)
    value = obj['Parameters'][attributename]
    return value

def load_template(yamlfile):
    with open(yamlfile, 'r') as myyamlfile:
        yamldata = myyamlfile.read()
    return yamldata

def create_parameter_list(parameterfile):
    parameterlist = []
    with open(parameterfile, 'r') as myparameterfile:
        paramdata = myparameterfile.read()
    paramobj = json.loads(paramdata)
    for x in paramobj['Parameters']:
        paramkey = x
        paramvalue = paramobj['Parameters'][paramkey]
        entry = {
                'ParameterKey': paramkey,
                'ParameterValue': paramvalue,
                'UsePreviousValue': False
            }
        parameterlist.append(entry)
    return parameterlist

def get_security_templates(template_dir):
    files = []
    for p in template_dir.glob("*"):
        if p.suffix in ['.yaml', '.yml', '.template'] and p.stat().st_size != 0:
            files.append(p)
    return files

def get_file_name(file):
    file = str(file)
    file_name =file.split('/')[-1]
    return file_name

def get_file_names(file_list):
    file_names = []
    for f in file_list:
        filename = get_file_name(f)
        file_names.append(filename)
    return file_names

def get_stack(stackname):
    response = client.describe_stacks(StackName=stackname)
    status = response['Stacks'][0]['StackStatus']
    return status

def get_cf_bucket():
    bucketlist = s3client.list_buckets()
    buckets = bucketlist['Buckets']
    # bucket = ''
    for b in buckets:
        if b['Name'].startswith('cf-templates-') and b['Name'].endswith('us-east-1'):
            bucket = b['Name']
    return bucket

def get_file_size(file):
    size = file.stat().st_size
    return size

def upload_template(template,bucket,filename):
    s3client.put_object(Body=template,Bucket=bucket,Key=filename)


def create_stack(stackname,parameters,capability,accountid,templatestring):
    stackcreateresponse = client.create_stack(
        StackName=stackname,
        TemplateBody=templatestring,
        Parameters=parameters,
        Capabilities=[capability],
        RoleARN='arn:aws:iam::'+accountid+':role/managed/'+STACK_EXECUTION_ROLE_NAME,
        OnFailure='DELETE'
    )
    return stackcreateresponse

def create_stack_s3(stackname,parameters,capability,accountid,templateurl):
    stackcreateresponse = client.create_stack(
        StackName=stackname,
        TemplateURL=templateurl,
        Parameters=parameters,
        Capabilities=[capability],
        RoleARN='arn:aws:iam::'+accountid+':role/managed/'+STACK_EXECUTION_ROLE_NAME,
        OnFailure='DELETE'
    )
    return stackcreateresponse

def update_stack(stackname,parameters,capability,accountid,templatestring):
    stackupdateresponse = client.update_stack(
        StackName=stackname,
        TemplateBody=templatestring,
        Parameters=parameters,
        Capabilities=[capability],
        RoleARN='arn:aws:iam::'+accountid+':role/managed/'+STACK_EXECUTION_ROLE_NAME,
        DisableRollback=False
    )
    return stackupdateresponse

def update_stack_s3(stackname,parameters,capability,accountid,templateurl):
    stackupdateresponse = client.update_stack(
        StackName=stackname,
        TemplateURL=templateurl,
        Parameters=parameters,
        Capabilities=[capability],
        RoleARN='arn:aws:iam::'+accountid+':role/managed/'+STACK_EXECUTION_ROLE_NAME,
        DisableRollback=False
    )
    return stackupdateresponse
    
def main():
    accountnumber = args['account_number']
    cf_bucket = get_cf_bucket()
    appid = get_json_attribute(str(CONFIG_DIR)+'/'+CONFIG_FILE_NAME, 'AppId')
    parameter_list = create_parameter_list(str(CONFIG_DIR)+'/'+CONFIG_FILE_NAME)
    logger.info('Getting CloudFormation templates')
    templates = get_security_templates(TEMPLATE_DIR)
    filenames = get_file_names(templates)
    create_list = []
    update_list = []
    for f in filenames:
        try:
            filenameprefix = f.split('.')[0]
            stackname = STACK_PREFIX + '-' + filenameprefix + '-' + appid
            logger.info('Checking if stack: %s already exists' % stackname)
            get_stack(stackname)
            logger.info('Stack: %s found!' % stackname)
            update_list.append({'Template': f, 'StackName': stackname})
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ValidationError':
                logger.warning(error.response['Error']['Message'])
                create_list.append({'Template': f, 'StackName': stackname})
            else:
                raise error
    logger.info('Deploying CloudFormation templates')
    for creation in create_list:
        active = True
        count = 1
        max_count = TIMEOUT_SECONDS / CF_CHECK_PERIOD_SECONDS
        templatename = creation['Template']
        stackname = creation['StackName']
        templatecapability = 'CAPABILITY_NAMED_IAM'
        templatelocation = str(TEMPLATE_DIR) + '/' + templatename
        cf_template_yaml = load_template(templatelocation)
        try:
            templatefileposix = Path(templatelocation)
            size = get_file_size(templatefileposix)
            if size > 51200:
                logger.info('%s file size is larger than quota. Uploading to %s' % (templatename, cf_bucket))
                upload_template(cf_template_yaml,cf_bucket,templatename)
                s3objectlocation = 'https://'+cf_bucket+'.s3.amazonaws.com/'+templatename
                createtemplateresponse = create_stack_s3(stackname,parameter_list,templatecapability,accountnumber,s3objectlocation)
            else:
                createtemplateresponse = create_stack(stackname,parameter_list,templatecapability,accountnumber,cf_template_yaml)
            logger.info('Creation of stack: %s in progress...' % createtemplateresponse['StackId'])
        except botocore.exceptions.ClientError as error:
            raise error
            active = False
        while active and count <= max_count:
            sleep(CF_CHECK_PERIOD_SECONDS)
            stackstatus = get_stack(stackname)
            if stackstatus in SUCCESS_STATUSES:
                logger.info('Creation of stack: %s complete.' % createtemplateresponse['StackId'])
                active = False
            elif stackstatus in FAILURE_STATUSES:
                logger.error('Failed to create stack: %s' % createtemplateresponse['StackId'])
                active = False
            else:
                count +=1
                if count < max_count:
                    logger.info('Creation of stack: %s still in progress...' % createtemplateresponse['StackId'])
                elif count >= max_count:
                    logger.error('Creation of stack: %s timed out.' % createtemplateresponse['StackId'])
    for update in update_list:
        active = True
        count = 1
        max_count = TIMEOUT_SECONDS / CF_CHECK_PERIOD_SECONDS
        templatename = update['Template']
        stackname = update['StackName']
        templatecapability = 'CAPABILITY_NAMED_IAM'
        templatelocation = str(TEMPLATE_DIR) + '/' + templatename
        cf_template_yaml = load_template(templatelocation)
        try:
            templatefileposix = Path(templatelocation)
            size = get_file_size(templatefileposix)
            if size > 51200:
                logger.info('%s file size is larger than quota. Uploading to %s' % (templatename, cf_bucket))
                upload_template(cf_template_yaml,cf_bucket,templatename)
                s3objectlocation = 'https://'+cf_bucket+'.s3.amazonaws.com/'+templatename
                updatetemplateresponse = update_stack_s3(stackname,parameter_list,templatecapability,accountnumber,s3objectlocation)
            else:
                updatetemplateresponse = update_stack(stackname,parameter_list,templatecapability,accountnumber,cf_template_yaml)
            logger.info('Update of stack: %s in progress...' % updatetemplateresponse['StackId'])
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ValidationError' and error.response['Error']['Message'] == 'No updates are to be performed.':
                logger.info('No updates required for stack: %s' % stackname)
                active = False
            else:
                raise error
                active = False
        while active and count <= max_count:
            sleep(CF_CHECK_PERIOD_SECONDS)
            stackstatus = get_stack(stackname)
            if stackstatus in SUCCESS_STATUSES:
                logger.info('Update of stack: %s complete.' % updatetemplateresponse['StackId'])
                active = False
            elif stackstatus in FAILURE_STATUSES:
                logger.error('Failed to update stack: %s' % updatetemplateresponse['StackId'])
                active = False
            else:
                count +=1
                if count < max_count:
                    logger.info('Update of stack: %s still in progress...' % updatetemplateresponse['StackId'])
                elif count >= max_count:
                    logger.error('Update of stack: %s timed out.' % updatetemplateresponse['StackId'])
                

if __name__ == "__main__":
    main()