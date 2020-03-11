import re
import requests
import os
import json
from json import JSONDecodeError

#WebEx details
roomId = "Y2lzY29zcGFyazovL3VzL1JPT00vYmMzNGIyZjAtNjFmYS0xMWVhLWI4NTgtMTM5NTgxNTJhYmNl"
bearer = 'Bearer ODc5ZDVmZGUtM2Q0Yy00MzM3LTk2YmItYjlhYzZkNTZjN2VmYTk3ZjdlY2ItOTEx_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f'

CI_PIPELINE_ID = os.getenv('CI_PIPELINE_ID')

pcv_output = open('output_'+CI_PIPELINE_ID+".txt", 'r').read()
new_string = re.sub("\[\{", "", pcv_output)

parsed_input_string = pcv_output[(pcv_output.find("FAILED! => ") + len("FAILED! => ")): pcv_output.find("PLAY RECAP") - 2]
try:
    output_dict = json.loads(parsed_input_string)
    epoch_details = output_dict['Later Epoch Smart Events'][0]['epoch2_details']
    epoch_details_desc = epoch_details['description']
    epoch_details_mnemonic = epoch_details['mnemonic']
except JSONDecodeError as e:
    print(e)
    output_dict = {"key":"value"}
text = "Description: {0},\nMessage: {1}".format(output_dict['Later Epoch Smart Events'][0]['epoch2_details']['description'],
                                                  output_dict['msg'])

print(output_dict)

url = 'https://api.ciscospark.com/v1/messages'
payload = {'roomId' : roomId, 'text': text}
headers = {'Authorization': bearer}
res = requests.post(url, data=payload, headers=headers)