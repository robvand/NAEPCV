#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

#     def createPreChange(self, ag_name,name,description,interactive_flag,changes):

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'],
                    'supported_by': 'certified'}

DOCUMENTATION = \
    r'''
---
module: nae_prechange
short_description: Manage pre-change analyses.
description:
- Manage Pre-Change Analyses on Cisco NAE fabrics.
version_added: '2.4'
options:
  ag_name:
    description:
    - The name of the assurance group.
    type: str
    required: yes
    aliases: [ fab_name ]
  name:
    description:
    - The name of the pre-change analysis
    type: str
    required: yes
    aliases: [ name ]
  description:
    description:
    - Description for the pre-change analysis.
    type: str
    required: no
    aliases: [ descr ]
  state:
    description:
    - Use C(present) or C(absent) for adding or removing.
    - Use C(query) for listing an object or multiple objects.
    - Use C(verify) for pipeline mode
type: str
    choices: [ absent, present, query, verify ]
    default: present
  file:
    description:
    - Optional parameter if creating new pre-change analysis from file.
  changes:
    description:
    - Optional parameter if creating new pre-change analysis from change-list (manual)

author:
- Shantanu Kulkarni (@shan_kulk)
'''

EXAMPLES = \
    r'''
- name: Add a pre-change analysis from manual changes
  nae_prechange:
    host: nae
    port: 8080
    username: Admin
    password: C@ndidadmin1234
    ag_name: FAB2
    name: NewTenantAnalysis
    changes: {"tenant_change": {"action": "ADD","dn": "uni/tn-newTenant","description": "Adding a new Tenant"}}
    name: NewAnalysis
    state: present
delegate_to: localhost
- name: Delete a pre-change analysis
  nae_prechange:
    host: nae
    port: 8080
    username: Admin
    password: C@ndidadmin1234
    ag_name: FAB2
    name: NewAnalysis
    state: absent
delegate_to: localhost
- name: Add a new pre-change analysis from file
  nae_prechange:
    host: nae
    port: 8080
    username: Admin
    password: C@ndidadmin1234
    ag_name: FAB2
    file: ../Camillo.json
    name: NewAnalysis
    description: New Analysis
    state: present
delegate_to: localhost
- name: Query a pre-change analysis
  nae_prechange:
    host: nae
    port: 8080
    username: Admin
    password: C@ndidadmin1234
    ag_name: FAB2
    name: Analysis1
    state: verify
  delegate_to: localhost
- name: Query a pre-change analysis
  nae_prechange:
    host: nae
    port: 8080
    username: Admin
    password: C@ndidadmin1234
    ag_name: FAB2
    name: Analysis1
    state: query
  delegate_to: localhost
- name: Query all pre-change analyses
  nae_prechange:
    host: nae
    port: 8080
    username: Admin
    password: C@ndidadmin1234
    ag_name: FAB2
    state: query
  delegate_to: localhost
  register: query_result
'''

RETURN = \
    '''
resp:
    description: Return payload
    type: str
    returned: always
'''

import requests
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.aci.nae import NAEModule, \
    nae_argument_spec
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def main():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    result = dict(changed=False, resp='')
    argument_spec = nae_argument_spec()
    argument_spec.update(  # Not required for querying all objects
        ag_name=dict(type='str', aliases=['fab_name']),
        name=dict(type='str', aliases=['name']),
        description=dict(type='str'),
        changes=dict(type='str'),
        file=dict(type='str', default=None),
        validate_certs=dict(type='bool', default=False),
        state=dict(type='str', default='present', choices=['absent',
                                                           'present', 'query', 'verify']),
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_if=[['state', 'absent', ['name']],
                                        ['state', 'present', ['name']]])

    changes = module.params.get('changes')
    change_file = module.params.get('file')
    description = module.params.get('description')
    state = module.params.get('state')
    ag_name = module.params.get('ag_name')
    name = module.params.get('name')

    nae = NAEModule(module)

    if state == 'query' and not name:
        nae.show_pre_change_analyses()
        module.exit_json(**nae.result)
    if state == 'absent':
        nae.delete_pre_change_analysis()
        module.exit_json(**nae.result)
    if (state == 'query' or state == 'verify') and name:
        nae.result['Result'] = nae.get_pre_change_result()
        if not nae.result['Result']:
            module.exit_json(
                msg="Pre-change analysis failed. The above smart events have been detected for later epoch only.",
                **nae.result)
        module.exit_json(**nae.result)
    if state == 'present' and change_file:
        nae.create_pre_change_from_file()
        nae.result['changed'] = True
        module.exit_json(**nae.result)
    if state == 'present' and changes:
        nae.create_pre_change_from_manual_changes()
        nae.result['changed'] = True
        module.exit_json(**nae.result)

    module.fail_json(msg='Incorrect params passed', **self.result)


if __name__ == '__main__':
    main()
