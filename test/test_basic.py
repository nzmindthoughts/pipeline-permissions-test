#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Performs Basic Readiness Tests
'''

import sys
import logging
import os
import unittest
import re
import yaml
import json
import pathlib
from pathlib import Path
from pprint import pprint, pformat

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(name)s@%(lineno)d: %(message)s')
LOG = logging.getLogger(os.path.basename(__file__))
TEST_DIR = pathlib.Path(__file__).parents[0]
ROOT_DIR = pathlib.Path(TEST_DIR).parents[0]

class CloudFormationEquals(object):
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        return "Equals(%s)" % self.data

class CloudFormationRef(object):
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        return "Ref(%s)" % self.data

class CloudFormationGetAtt(object):
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        return "GetAtt(%s)" % self.data

class CloudFormationNot(object):
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        return "Not(%s)" % self.data

class CloudFormationSub(object):
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        return "Sub(%s)" % self.data

class CloudFormationOr(object):
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        return "Or(%s)" % self.data

class CloudFormationAnd(object):
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        return "And(%s)" % self.data

class CloudFormationCondition(object):
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        return "Condition(%s)" % self.data

class CloudFormationJoin(object):
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        return "Join(%s)" % self.data

class CloudFormationIf(object):
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        return "If(%s)" % self.data

class CloudFormationSelect(object):
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        return "Select(%s)" % self.data


class CloudFormationFindInMap(object):
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        return "FindInMap(%s)" % self.data

def create_cf_equals(loader,node):
    if isinstance(node, (yaml.nodes.SequenceNode)):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_scalar(node)
    return CloudFormationEquals(value)

def create_cf_or(loader,node):
    if isinstance(node, (yaml.nodes.SequenceNode)):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_scalar(node)
    return CloudFormationOr(value)

def create_cf_join(loader,node):
    if isinstance(node, (yaml.nodes.SequenceNode)):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_scalar(node)
    return CloudFormationJoin(value)

def create_cf_if(loader,node):
    if isinstance(node, (yaml.nodes.SequenceNode)):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_scalar(node)
    return CloudFormationIf(value)

def create_cf_and(loader,node):
    if isinstance(node, (yaml.nodes.SequenceNode)):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_scalar(node)
    return CloudFormationAnd(value)

def create_cf_cond(loader,node):
    if isinstance(node, (yaml.nodes.SequenceNode)):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_scalar(node)
    return CloudFormationCondition(value)

def create_cf_ref(loader,node):
    value = loader.construct_scalar(node)
    return CloudFormationRef(value)

def create_cf_getatt(loader, node):
    if isinstance(node, (yaml.nodes.SequenceNode)):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_scalar(node)
    return CloudFormationGetAtt(value)

def create_cf_not(loader, node):
    if isinstance(node, (yaml.nodes.SequenceNode)):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_scalar(node)
    return CloudFormationNot(value)

def create_cf_sub(loader, node):
    value = loader.construct_scalar(node)
    return CloudFormationSub(value)

def create_cf_select(loader, node):
    if isinstance(node, (yaml.nodes.SequenceNode)):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_scalar(node)
    return CloudFormationSelect(value)

def create_cf_findinmap(loader, node):
    if isinstance(node, (yaml.nodes.SequenceNode)):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_scalar(node)
    return CloudFormationFindInMap(value)

class Loader(yaml.Loader):
    pass

yaml.add_constructor(u'!Equals', create_cf_equals, Loader)
yaml.add_constructor(u'!Or', create_cf_or, Loader)
yaml.add_constructor(u'!If', create_cf_if, Loader)
yaml.add_constructor(u'!Select', create_cf_select, Loader)
yaml.add_constructor(u'!And', create_cf_and, Loader)
yaml.add_constructor(u'!Join', create_cf_join, Loader)
yaml.add_constructor(u'!Condition', create_cf_cond, Loader)
yaml.add_constructor(u'!Ref', create_cf_ref, Loader)
yaml.add_constructor(u'!GetAtt', create_cf_getatt, Loader)
yaml.add_constructor(u'!Not', create_cf_not, Loader)
yaml.add_constructor(u'!Sub', create_cf_sub, Loader)
yaml.add_constructor(u'!FindInMap', create_cf_findinmap, Loader)

def get_invalid_char_pos(s):
    r = []
    for i, c in enumerate(s):
        # ord(c) returns decimal number
        if ord(c) > 126:
            r.append(i)
        elif ord(c) < 32:
            r.append(i)
        else:
            pass
    return r

def get_indent_size(s):
    return len(s) - len(s.lstrip())

class BasicTestCase(unittest.TestCase):
    ''' Tests the readiness of the package. '''
    @classmethod
    def setUpClass(cls):
        ''' This functions runs only once, prior to all the setups and tests. '''
        LOG.info('Test directory: %s', TEST_DIR)
        LOG.info('Root directory: %s', ROOT_DIR)
        #LOG.debug('Completed setting up the class!')
        print('\n')

    @classmethod
    def tearDownClass(cls):
        ''' This functions runs only once prior to tearing down the class. '''
        print('\n')
        #LOG.debug('Completed tearing down the class!')

    @classmethod
    def setUp(cls):
        print('\n')
        ''' This functions runs for all of the tests in the class prior to running the test. '''
        #LOG.debug('Completed setting up the test!')

    @classmethod
    def tearDown(cls):
        print('\n')
        ''' This function runs for all of the tests in the class prior to tearing down the test. '''
        #LOG.debug('Completed tearing down the test!')

class ReadinessTestCase(BasicTestCase):
    '''Contains readiness test cases'''

    @staticmethod
    def get_files(root_dir):
        files = []
        for p in ROOT_DIR.rglob("*"):
            if not p.is_file():
                continue
            if p.is_symlink() or p.is_socket():
                continue
            file_dir = str(p.parents[0]).replace(str(ROOT_DIR) + '/', '')
            if str(p.parents[0]) == str(ROOT_DIR):
                file_dir = '.'
            if file_dir.startswith('.git') and p.name != 'config':
                continue
            if p.suffix in ['.pyc']:
                continue
            if p.name in ['__init__.py']:
                continue
            if p.stat().st_size == 0 and '.template' in p.name:
                continue
            files.append(p)
        return files

    def test_check_for_filename_compliance(self):
        '''Tests whether file and directory names comply with a naming convention.'''
        _is_failed = False
        LOG.info('%s: %s', self.id().split('.')[-1], self.shortDescription())
        files = self.get_files(ROOT_DIR)
        for f in files:
            file_dir = str(f.parents[0]).replace(str(ROOT_DIR) + '/', '')
            if str(f.parents[0]) == str(ROOT_DIR):
                file_dir = '.'
            allowed_filenames = [
                'README.md',
                'README.pdf',
                'README.j2',
                'CODEOWNERS',
                'Makefile',
                'service-catalog-item.template',
                'service-catalog.template',
                '.gitlab-ci.yml',
                'gitlab-ci.yml',
                'requirements.txt',
            ]
            allowed_dirnames = [
                '.',
                '.git',
                'assets/service-catalog',
                'assets/templates/docs',
                'assets/docs',
            ]
            if not re.match('[a-z0-9\._-]+$', f.name) and f.name not in allowed_filenames:
                LOG.error('%s - File name is not allowed', f.name)
                _is_failed = True
            if not re.match('[a-z0-9_/]+$', file_dir) and file_dir not in allowed_dirnames:
                LOG.error('%s - Directory name is not allowed', file_dir)
                _is_failed = True
            if _is_failed:
                continue
            LOG.info('%s/%s - COMPLIANT', file_dir, f.name)
        self.assertFalse(_is_failed, msg='Test failed')

    def test_linter_compliance(self):
        '''Tests whether the content of YAML and JSON files pass linter.'''
        _is_failed = False
        LOG.info('%s: %s', self.id().split('.')[-1], self.shortDescription())
        files = self.get_files(ROOT_DIR)
        for f in files:
            file_dir = str(f.parents[0]).replace(str(ROOT_DIR) + '/', '')
            if str(f.parents[0]) == str(ROOT_DIR):
                file_dir = '.'
            if f.suffix not in ['.json', '.yaml', '.yml', '.template']:
                LOG.info('%s/%s - SKIP', file_dir, f.name)
                continue
            data = None
            try:
                if f.suffix == '.json':
                    with open(f, 'r') as fh:
                        data = json.load(fh)
                else:
                    with open(f, 'r') as fh:
                        data = yaml.load(fh, Loader=Loader)
                if not data:
                    _is_failed = True

            except Exception as err:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                LOG.error('%s/%s - FAILED - %s %s', file_dir, f.name, exc_type, err)
                _is_failed = True
                continue
            LOG.info('%s/%s - PASS', file_dir, f.name)
        self.assertFalse(_is_failed, msg='Test failed')

    def test_managed_resource_types(self):
        '''Tests whether the AWS CloudFormation resource are of supported types.'''
        _is_failed = False
        supported_resource_types = [
            'AWS::EC2::SecurityGroup',
            'AWS::EC2::SecurityGroupEgress',
            'AWS::EC2::SecurityGroupIngress',
            'AWS::EC2::NetworkAcl',
            'AWS::EC2::NetworkAclEntry',
            'AWS::EC2::SubnetNetworkAclAssociation',
            'AWS::IAM::User',
            'AWS::IAM::Role',
            'AWS::IAM::Group',
            'AWS::IAM::Policy',
            'AWS::IAM::AccessKey',
            'AWS::KMS::Key',
            'AWS::KMS::Alias',
            'AWS::CloudWatch::Alarm',
            'AWS::IAM::InstanceProfile',
            'AWS::Logs::MetricFilter',
            'AWS::Config::ConfigRule',
            'AWS::Logs::LogGroup',
            'AWS::Events::Rule',
            'AWS::Lambda::Function',
            'Custom::IdentityProvider',
            'Custom::SmtpPassword',
            'Custom::SmtpUsername',
            'AWS::IAM::ManagedPolicy',
            'AWS::SSM::Parameter',
            'AWS::LakeFormation::DataLakeSettings',
            'AWS::Glue::Connection',
            'AWS::IAM::ServiceLinkedRole',
            'AWS::Route53::HostedZone',
            'AWS::Route53::RecordSet',
            'AWS::Route53::RecordSetGroup',
            'AWS::EC2::VPCEndpoint',
            'AWS::SecretsManager::Secret'
        ]
        LOG.info('%s: %s', self.id().split('.')[-1], self.shortDescription())
        files = self.get_files(ROOT_DIR)
        for f in files:
            file_dir = str(f.parents[0]).replace(str(ROOT_DIR) + '/', '')
            if str(f.parents[0]) == str(ROOT_DIR):
                file_dir = '.'
            if f.suffix not in ['.template']:
                continue
            if 'templates' not in file_dir:
                continue
            LOG.info('%s/%s - ok', file_dir, f.name)
            cf = None
            try:
                with open(f, 'r') as fh:
                    cf = yaml.load(fh, Loader=Loader)
                #LOG.info('%s', pformat(cf))
                if 'Resources' not in cf:
                    raise Exception('ManagedResourceError', 'No Resources found')
                for k in cf['Resources']:
                    if 'Type' not in cf['Resources'][k]:
                        raise Exception('ManagedResourceError', 'Resource %s has no Type' % (k))
                    resource_type = cf['Resources'][k]['Type']
                    if resource_type not in supported_resource_types:
                        raise Exception('ManagedResourceError', 'Resource %s has unsupported Type %s' % (k, resource_type))

            except Exception as err:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                LOG.error('%s/%s - FAILED - %s %s', file_dir, f.name, exc_type, err)
                _is_failed = True
                continue
            LOG.info('%s/%s - PASS', file_dir, f.name)
        self.assertFalse(_is_failed, msg='Test failed')


    def test_duplicate_resources(self):
        '''Tests whether the AWS CloudFormation templates contain duplicate resources.'''
        _is_failed = False
        LOG.info('%s: %s', self.id().split('.')[-1], self.shortDescription())
        required_template_sections = [
            'AWSTemplateFormatVersion',
            'Description',
            'Parameters',
            'Resources',
        ]
        optional_template_sections = [
            'Conditions',
            'Outputs',
            'Mappings',
        ]
        files = self.get_files(ROOT_DIR)
        for f in files:
            _is_file_failed = False
            file_dir = str(f.parents[0]).replace(str(ROOT_DIR) + '/', '')
            if str(f.parents[0]) == str(ROOT_DIR):
                file_dir = '.'
            if f.suffix not in ['.template']:
                continue
            if 'templates' not in file_dir:
                continue
            LOG.info('%s/%s - found', file_dir, f.name)
            db = {}
            try:
                lines = None
                with open(f, 'r') as fh:
                    lines = fh.readlines()
                section = None
                for i, line in enumerate(lines):
                    line = line.replace('\n', '')
                    if re.match('\s*#', line):
                        continue
                    if re.search('\s+$', line) and line != '\n':
                        LOG.error('%s/%s: line %d - trailing whitespace ("%s")', file_dir, f.name, (i + 1), line)
                        _is_file_failed = True
                    invalid_chars = get_invalid_char_pos(line)
                    if invalid_chars:
                        LOG.error('%s/%s: line %d - invalid characters, positions: %s ("%s")', file_dir, f.name, (i + 1), invalid_chars, line)
                        _is_file_failed = True
                    indent = get_indent_size(line)
                    if indent == 0:
                        section = line.strip().split(':')[0]
                        if section not in ['', '---']:
                            if section not in db:
                                db[section] = {}
                    elif indent == 2 and section:
                        resource = line.strip().split(':')[0]
                        if resource not in db[section]:
                            db[section][resource] = []
                        db[section][resource].append(i)
                LOG.info('%s/%s - %d lines', file_dir, f.name, len(lines))
            except Exception as err:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                LOG.error('%s/%s - FAILED - %s %s', file_dir, f.name, exc_type, err)
                _is_failed = True
                continue

            for k in required_template_sections:
                if k not in db:
                    _is_file_failed = True
                    LOG.error('%s/%s: section %s not found in CFN template', file_dir, f.name, k)

            for section in db:
                if section not in required_template_sections and section not in optional_template_sections:
                    _is_file_failed = True
                    LOG.error('%s/%s: section %s is not a valid CFN template section', file_dir, f.name, section)
                    continue
                for resource in db[section]:
                    if len(db[section][resource]) > 1:
                        _is_file_failed = True
                        LOG.error('%s/%s: duplicate resource found, name: %s, lines: %s', file_dir, f.name, resource, db[section][resource])

            if _is_file_failed:
                LOG.error('%s/%s - FAILED', file_dir, f.name)
                _is_failed = True
                continue
            LOG.info('%s/%s - PASS', file_dir, f.name)
        self.assertFalse(_is_failed, msg='Test failed')

    def test_managed_resource_fields(self):
        '''Tests whether the fields of AWS CloudFormation resources are compliance.'''
        _is_failed = False
        LOG.info('%s: %s', self.id().split('.')[-1], self.shortDescription())
        required_resource_props = {
            'AWS::IAM::User': {
                'required_props': ['UserName', 'Tags', 'Path', 'Groups'],
                'required_tags': [{
                    'Key': 'secops:tags:managed_by',
                    'Value': 'AWS Managed Security Pipeline',
                }]
            },
            'AWS::IAM::Role': {
                'required_props': ['RoleName', 'Description', 'Path', 'AssumeRolePolicyDocument'],
                'required_tags': [{
                    'Key': 'secops:tags:managed_by',
                    'Value': 'AWS Managed Security Pipeline',
                }]
            },
            'AWS::IAM::Group': {
                'required_props': ['Path', 'GroupName'],
            },
            'AWS::IAM::Policy': {
                'required_props': ['PolicyName', 'PolicyDocument'],
            },
            'AWS::IAM::AccessKey': {
                'required_props': ['UserName', 'Status'],
            },
            'AWS::KMS::Key': {
                'required_props': ['Description', 'EnableKeyRotation', 'Enabled', 'KeyPolicy'],
                'required_tags': [{
                    'Key': 'secops:tags:managed_by',
                    'Value': 'AWS Managed Security Pipeline',
                }]
            },
            'AWS::KMS::Alias': {
                'required_props': ['AliasName', 'TargetKeyId'],
            },
            'AWS::EC2::NetworkAcl': {
                'required_props': ['VpcId'],
            },
            'AWS::EC2::NetworkAclEntry': {
                'required_props': ['NetworkAclId', 'Protocol', 'RuleAction', 'RuleNumber'],
            },
            'AWS::EC2::SubnetNetworkAclAssociation': {
                'required_props': ['NetworkAclId', 'SubnetId'],
            },
        }
        files = self.get_files(ROOT_DIR)
        for f in files:
            _is_file_failed = False
            file_dir = str(f.parents[0]).replace(str(ROOT_DIR) + '/', '')
            if str(f.parents[0]) == str(ROOT_DIR):
                file_dir = '.'
            if f.suffix not in ['.template']:
                continue
            if 'templates' not in file_dir:
                continue
            LOG.info('%s/%s - ok', file_dir, f.name)
            cf = None
            try:
                with open(f, 'r') as fh:
                    cf = yaml.load(fh, Loader=Loader)
                #LOG.info('%s', pformat(cf))
                if 'Resources' not in cf:
                    raise Exception('ManagedResourceError', 'No Resources found')
                for k in cf['Resources']:
                    resource = cf['Resources'][k]
                    if 'Type' not in resource:
                        raise Exception('ManagedResourceError', 'Resource %s has no Type' % (k))
                    resource_type = resource['Type']
                    if 'Properties' not in resource:
                        LOG.error('%s/%s: Resource %s has no Properties, Resource:\n%s',
                                file_dir, f.name, k, pformat(resource))
                        _is_file_failed = True
                        continue
                    resource_props = resource['Properties']
                    if resource_type in required_resource_props:
                        if 'required_props' in required_resource_props[resource_type]:
                            for resource_prop in required_resource_props[resource_type]['required_props']:
                                if resource_prop in resource_props:
                                    continue
                                LOG.error('%s/%s: Resource %s has no %s Property, Resource:\n%s',
                                        file_dir, f.name, k, resource_prop, pformat(resource))
                                _is_file_failed = True
                                continue
                        if 'required_tags' in required_resource_props[resource_type]:
                            for required_tag in required_resource_props[resource_type]['required_tags']:
                                required_tag_found = False
                                if 'Tags' in resource_props:
                                    for tag in resource_props['Tags']:
                                        if tag['Key'] != required_tag['Key']:
                                            continue
                                        if tag['Value'] != required_tag['Value']:
                                            continue
                                        required_tag_found = True
                                if not required_tag_found:
                                    _is_file_failed = True
                                    LOG.error('%s/%s: required tag not found in %s, key: %s, value: %s',
                                        file_dir, f.name, k, required_tag['Key'], required_tag['Value'])


            except Exception as err:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                LOG.error('%s/%s - FAILED - %s %s', file_dir, f.name, exc_type, err)
                _is_failed = True
                continue
            if _is_file_failed:
                LOG.error('%s/%s - FAILED', file_dir, f.name)
                _is_failed = True
                continue
            LOG.info('%s/%s - PASS', file_dir, f.name)
        self.assertFalse(_is_failed, msg='Test failed')

if __name__ == '__main__':
    unittest.main()