import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

ag_name = "apic-amslab"

# receive OTP with whoami
url = 'https://candid-amslab.cisco.com/api/v1/whoami'
headers = {"Content-Type": "application/json"}
with requests.Session() as s:
 response = s.get(url, headers=headers, verify=False)

# Log in to NAE and grab bearer token
url = 'https://candid-amslab.cisco.com/api/v1/login'
headers = {"Content-Type": "application/json",
           "X-NAE-LOGIN-OTP": response.headers['x-nae-login-otp'],
           "Cookie" : response.headers['set-cookie']
}
data = {
  "username": "admin",
  "password": "C!sco1234567890"
}
with requests.Session() as s:
 response = s.post(url, headers=headers, data=json.dumps(data), verify=False)

headers = {"Content-Type": "application/json",
           "X-NAE-CSRF-TOKEN": response.headers['X-NAE-CSRF-TOKEN'],
}
# Receive Assurance Group uuid from matching fabric (ag_name)
url = 'https://candid-amslab.cisco.com/api/v1/config-services/assured-networks/aci-fabric'
response = s.get(url, headers=headers, verify=False)
json_dict = json.loads(response.text)
for data in json_dict['value']['data']:
    if data['unique_name'] == ag_name:
        uuid = data['uuid']
    else:
        print("Wrong fabric name: {}".format(data['unique_name']))
print(uuid)

# Start assurance group
url = "https://candid-amslab.cisco.com/nae/api/v1/config-services/analysis/737ea995-98a30e27-78a3-4b57-8059-da1b77506135/stop"
data = '''
{
  "interval": 900,
  running_status: "STOP_REQUESTED",
  "type": "AUTO",
  "assurance_group_list": [
    {
      "uuid": 

    }
  ],
  "offline_analysis_list": [],
  "iterations": 1
}'''
response = s.post(url, headers=headers, data=data, verify=False)
print(response.status_code)
print(url)
