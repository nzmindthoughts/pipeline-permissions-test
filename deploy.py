import boto3
import botocore
import logging

# Set up our logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

client = boto3.client('cloudformation')

stacknameexample = 'managed-pipeline'

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
    try:
        logger.info('Checking if stack already exists')
        get_stack(stacknameexample)
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'ValidationError':
            logger.warning(error.response['Error']['Message'])
        else:
            raise error