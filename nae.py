# -*- coding: utf-8 -*-

# This code is part of Ansible, but is an independent component

# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.


# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from requests_toolbelt import MultipartEncoder
from datetime import datetime
import base64
import json
import os
import gzip
from copy import deepcopy
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_bytes, to_native


def nae_argument_spec():
    return dict(
        host=dict(type='str', required=True, aliases=['hostname']),
        port=dict(type='int', required=True),
        username=dict(type='str', default='admin', aliases=['user']),
        password=dict(type='str', no_log=True),
    )


class NAEModule(object):
    def __init__(self, module):
        self.module = module
        self.resp = {}
        self.params = module.params
        self.result = dict(changed=False)
        self.assuranceGroups = {}
        self.files = {}
        self.assuranceGroups = []
        self.session_cookie = ""
        self.error = dict(code=None, text=None)
        self.version = ""
        self.http_headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,it;q=0.7',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Host': self.params.get('host'),
            'Content-Type': 'application/json;charset=utf-8',
            'Connection': 'keep-alive'}
        self.login()

    def login(self):
        url = 'https://%(host)s:%(port)s/api/v1/whoami' % self.params
        resp, auth = fetch_url(self.module, url,
                               data=None,
                               method='GET')

        if auth.get('status') != 200:
            if ('filename' in self.params):
                self.params['file'] = self.params['filename']
                del self.params['filename']
            self.module.exit_json(
                msg=json.loads(
                    auth.get('body'))['messages'][0]['message'],
                **self.result)

        url = 'https://%(host)s:%(port)s/api/v1/login' % self.params
        user_credentials = json.dumps({"username": self.params.get(
            'username'), "password": self.params.get('password'), "domain": 'Local'})
        self.http_headers['Cookie'] = resp.headers.get('Set-Cookie')
        self.session_cookie = resp.headers.get('Set-Cookie')
        self.http_headers['X-NAE-LOGIN-OTP'] = resp.headers.get(
            'X-NAE-LOGIN-OTP')
        resp, auth = fetch_url(self.module, url,
                               headers=self.http_headers,
                               data=user_credentials,
                               method='POST')

        if auth.get('status') != 200:
            if ('filename' in self.params):
                self.params['file'] = self.params['filename']
                del self.params['filename']
            self.module.exit_json(
                msg=json.loads(
                    auth.get('body'))['messages'][0]['message'],
                **self.result)

        self.http_headers['X-NAE-CSRF-TOKEN'] = resp.headers['X-NAE-CSRF-TOKEN']

        # # Update with the authenticated Cookie
        self.http_headers['Cookie'] = resp.headers.get('Set-Cookie')

        # Remove the LOGIN-OTP from header, it is only needed at the beginning
        self.http_headers.pop('X-NAE-LOGIN-OTP', None)
        # self.result['response'] = data

    def fail_json(self, msg, **kwargs):

        # Return error information, if we have it
        if self.error.get('code') is not None and self.error.get(
                'text') is not None:
            self.result['error'] = self.error

        if 'state' in self.params:
            if self.params.get('state') in ('absent', 'present'):
                if self.params.get('output_level') in ('debug', 'info'):
                    self.result['previous'] = self.existing

            # Return the gory details when we need it
            if self.params.get('output_level') == 'debug':
                if self.imdata is not None:
                    self.result['imdata'] = self.imdata
                    self.result['totalCount'] = self.totalCount

        if self.params.get('output_level') == 'debug':
            if self.url is not None:
                if 'state' in self.params:
                    self.result['filter_string'] = self.filter_string
                self.result['method'] = self.method
                # self.result['path'] = self.path  # Adding 'path' in result
                # causes state: absent in output
                self.result['response'] = self.response
                self.result['status'] = self.status
                self.result['url'] = self.url

        if 'state' in self.params:
            if self.params.get('output_level') in ('debug', 'info'):
                self.result['sent'] = self.config
                self.result['proposed'] = self.proposed

        self.result.update(**kwargs)
        self.module.fail_json(msg=msg, **self.result)

    def get_all_assurance_groups(self):
        url = 'https://%(host)s:%(port)s/api/v1/config-services/assured-networks/aci-fabric/' % self.params
        resp, auth = fetch_url(self.module, url,
                               headers=self.http_headers,
                               data=None,
                               method='GET')

        if auth.get('status') != 200:
            if ('filename' in self.params):
                self.params['file'] = self.params['filename']
                del self.params['filename']
            self.module.exit_json(
                msg=json.loads(
                    auth.get('body'))['messages'][0]['message'],
                **self.result)

        #r = gzip.decompress(resp.read())
        self.assuranceGroups = json.loads(resp.read())['value']['data']

    def get_assurance_group(self, name):
        self.get_all_assurance_groups()
        for ag in self.assuranceGroups:
            if ag['unique_name'] == name:
                return ag
        return None

    def get_pre_change_analyses(self):
        self.params['fabric_id'] = str(
            self.get_assurance_group(
                self.params.get('ag_name'))['uuid'])
        url = 'https://%(host)s:%(port)s/nae/api/v1/config-services/prechange-analysis?fabric_id=%(fabric_id)s' % self.params
        resp, auth = fetch_url(self.module, url,
                               headers=self.http_headers,
                               data=None,
                               method='GET')
        # self.result['resp'] = resp.headers.get('Set-Cookie')
        # self.module.fail_json(msg="err", **self.result)
        if auth.get('status') != 200:
            if ('filename' in self.params):
                self.params['file'] = self.params['filename']
                del self.params['filename']
            self.module.exit_json(
                msg=json.loads(
                    auth.get('body'))['messages'][0]['message'],
                **self.result)

        r = gzip.decompress(resp.read())
        return json.loads(r)['value']['data']

    def show_pre_change_analyses(self):
        result = self.get_pre_change_analyses()
        for x in result:
            if 'description' not in x:
                x['description'] = ""
            if 'job_id' in x:
                del x['job_id']
            if 'fabric_uuid' in x:
                del x['fabric_uuid']
            if 'base_epoch_id' in x:
                del x['base_epoch_id']
            if 'base_epoch_collection_time_rfc3339':
                del x['base_epoch_collection_time_rfc3339']
            if 'pre_change_epoch_uuid' in x:
                del x['pre_change_epoch_uuid']
            if 'analysis_schedule_id' in x:
                del x['analysis_schedule_id']
            if 'epoch_delta_job_id' in x:
                del x['epoch_delta_job_id']
            if 'enable_download' in x:
                del x['enable_download']
            if 'allow_unsupported_object_modification' in x:
                del x['allow_unsupported_object_modification']
            if 'changes' in x:
                del x['changes']
            if 'change_type' in x:
                del x['change_type']
            if 'uploaded_file_name' in x:
                del x['uploaded_file_name']
            if 'stop_analysis' in x:
                del x['stop_analysis']
            if 'submitter_domain' in x:
                del x['submitter_domain']

            m = str(x['base_epoch_collection_timestamp'])[:10]
            dt_object = datetime.fromtimestamp(int(m))
            x['base_epoch_collection_timestamp'] = dt_object

            m = str(x['analysis_submission_time'])[:10]
            dt_object = datetime.fromtimestamp(int(m))
            x['analysis_submission_time'] = dt_object
        self.result['Analyses'] = result
        return result

    def get_pre_change_analysis(self):
        ret = self.get_pre_change_analyses()
        # self.result['ret'] = ret
        for a in ret:
            if a['name'] == self.params.get('name'):
                # self.result['analysis'] = a
                return a
        return None

    def get_pre_change_result(self):
        if self.get_assurance_group(self.params.get('ag_name')) is None:
            self.module.exit_json(msg='No such Assurance Group exists on this fabric.')
        self.params['fabric_id'] = str(
            self.get_assurance_group(
                self.params.get('ag_name'))['uuid'])
        if self.get_pre_change_analysis() is None:
            self.module.exit_json(msg='No such Pre-Change Job exists.')
        if self.params['state'] == 'verify':
            status = None
            while status != "COMPLETED":
                try:
                    status = str(self.get_pre_change_analysis()['analysis_status'])
                    if status == "COMPLETED":
                        self.params['epoch_delta_job_id'] = str(self.get_pre_change_analysis()['epoch_delta_job_id'])
                        break
                except:
                    pass
        else:
            job_is_done = str(self.get_pre_change_analysis()['analysis_status'])
            if job_is_done != "COMPLETED":
                self.module.exit_json(msg='Pre-Change Job has not yet completed.', **self.result)
        self.params['epoch_delta_job_id'] = str(self.get_pre_change_analysis()['epoch_delta_job_id'])
        url = 'https://%(host)s:%(port)s/nae/api/v1/epoch-delta-services/assured-networks/%(fabric_id)s/job/%(epoch_delta_job_id)s/health/view/aggregate-table?category=ADC,CHANGE_ANALYSIS,TENANT_ENDPOINT,TENANT_FORWARDING,TENANT_SECURITY,RESOURCE_UTILIZATION,SYSTEM,COMPLIANCE&epoch_status=EPOCH2_ONLY&severity=EVENT_SEVERITY_CRITICAL,EVENT_SEVERITY_MAJOR,EVENT_SEVERITY_MINOR,EVENT_SEVERITY_WARNING,EVENT_SEVERITY_INFO' % self.params
        resp, auth = fetch_url(self.module, url,
                               headers=self.http_headers,
                               data=None,
                               method='GET')
        if auth.get('status') != 200:
            self.module.exit_json(
                msg=json.loads(
                    auth.get('body'))['messages'][0]['message'],
                **self.result)
        result = json.loads(resp.read())['value']['data']
        for x in result:
            if int(x['count']) > 0:
                if(str(x['category']) == "COMPLIANCE" and str(x['epoch2_details']['severity']) == "EVENT_SEVERITY_INFO"):
                    return "Pre-change analysis '%(name)s' passed." % self.params
                self.result['Later_Epoch_Smart_Events'] = result
                self.module.fail_json(
                     msg="Pre-change analysis failed. The above smart events have been detected for later epoch only.",
                     **self.result)
                return False
        return "Pre-change analysis '%(name)s' passed." % self.params

    def create_pre_change_from_manual_changes(self):
        self.params['file'] = None
        # change_list = []
        # change_list.append(self.params['changes'])
        # changes = json.dumps(change_list)
        # self.params['changes'] = changes
        self.send_pre_change_payload()

    def create_pre_change_from_file(self):
        assert os.path.exists(self.params.get(
            'file')), "File not found, " + str(self.params.get('file'))
        self.params['filename'] = self.params.get('file')
        f = open(self.params.get('file'), "rb")
        config = []
        self.params['file'] = f
        self.params['changes'] = str(config)
        self.send_pre_change_payload()

    def delete_pre_change_analysis(self):
        if self.get_pre_change_analysis() is None:
            self.module.exit_json(msg='No such Pre-Change Job exists.')
        self.params['job_id'] = str(self.get_pre_change_analysis()['job_id'])

        url = 'https://%(host)s:%(port)s/nae/api/v1/config-services/prechange-analysis/%(job_id)s' % self.params
        resp, auth = fetch_url(self.module, url,
                               headers=self.http_headers,
                               data=None,
                               method='DELETE')

        if auth.get('status') != 200:
            if ('filename' in self.params):
                self.params['file'] = self.params['filename']
                del self.params['filename']
            self.module.exit_json(
                msg=json.loads(
                    auth.get('body'))['messages'][0]['message'],
                **self.result)

        self.result['msg'] = json.loads(resp.read())['value']['data']

    def get_epochs(self):
        self.params['fabric_id'] = str(
            self.get_assurance_group(
                self.params.get('ag_name'))['uuid'])
        url = 'https://%(host)s:%(port)s/api/v1/event-services/assured-networks/%(fabric_id)s/epochs?$sort=collectionTimestamp' % self.params
        resp, auth = fetch_url(self.module, url,
                               headers=self.http_headers,
                               data=None,
                               method='GET')

        if auth.get('status') != 200:
            if ('filename' in self.params):
                self.params['file'] = self.params['filename']
                del self.params['filename']
            self.module.exit_json(
                msg=json.loads(
                    auth.get('body'))['messages'][0]['message'],
                **self.result)

        r = gzip.decompress(resp.read())
        return json.loads(r.decode())['value']['data']

    def send_pre_change_payload(self):
        self.params['fabric_id'] = str(
            self.get_assurance_group(
                self.params.get('ag_name'))['uuid'])
        # self.params['base_epoch_id'] = str(self.get_epochs()[-1]["epoch_id"])
        epochs = self.get_epochs()
        count = 0
        for x in epochs:
            count = count + 1
        for j in range(count - 1, 0, -1):
            if not (epochs[j]["epoch_type"] == "PCV"):
                self.params['base_epoch_id'] = str(epochs[j]["epoch_id"])
                break
        fields = {
            ('data',
             (self.params.get('file'),
              # content to upload
              '''{
                        "name": "''' + self.params.get('name') + '''",
                        "fabric_uuid": "''' + self.params.get('fabric_id') + '''",
                        "base_epoch_id": "''' + self.params.get('base_epoch_id') + '''",
                        "changes": ''' + str(self.params.get('changes')) + ''',
                        "stop_analysis": false,
                        "change_type": "CHANGE_LIST"
                        }'''  # The content type of the file
              , 'application/json'))
        }
        url = 'https://%(host)s:%(port)s/api/v1/config-services/prechange-analysis' % self.params
        m = MultipartEncoder(fields=fields)
        self.http_headers['Content-Type'] = m.content_type

        resp, auth = fetch_url(self.module, url,
                               headers=self.http_headers,
                               data=m,
                               method='POST')

        if auth.get('status') != 200:
            if ('filename' in self.params):
                self.params['file'] = self.params['filename']
                del self.params['filename']
            self.module.exit_json(
                msg=json.loads(
                    auth.get('body'))['messages'][0]['message'],
                **self.result)

        if ('filename' in self.params):
            self.params['file'] = self.params['filename']
            del self.params['filename']

        self.result['Result'] = "Pre-change analysis %(name)s successfully created." % self.params