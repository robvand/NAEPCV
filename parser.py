import requests
import json

#WebEx details
roomId = "Y2lzY29zcGFyazovL3VzL1JPT00vYmMzNGIyZjAtNjFmYS0xMWVhLWI4NTgtMTM5NTgxNTJhYmNl"
bearer = 'ODc5ZDVmZGUtM2Q0Yy00MzM3LTk2YmItYjlhYzZkNTZjN2VmYTk3ZjdlY2ItOTEx_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f'

def post_message(message):
    u = "https://api.ciscospark.com/v1/messages"
    headers = {"Content-type": "application/json",
               "Authorization": "Bearer {}".format(bearer)}
    body = {"roomId": roomId,
            "markdown": message}
    return requests.post(u, headers=headers, data=json.dumps(body))

with open('/tmp/results.json') as json_file:
    data = json.load(json_file)
    results = json.dumps(data, indent=4, sort_keys=True)
    print(json.dumps(data["Later_Epoch_Smart_Events"][0]["epoch2_details"]["description"]))

    message = []
    message.append("****************")
    message.append("    Description         : " + json.dumps(data["Later_Epoch_Smart_Events"][0]["epoch2_details"]["description"]))
    message.append("    Mnemonic            : " + json.dumps(data["Later_Epoch_Smart_Events"][0]["epoch2_details"]["mnemonic"]))
    message.append("    Event Severity      : " + json.dumps(data["Later_Epoch_Smart_Events"][0]["epoch2_details"]["severity"]))
    message.append("    Category            : " + json.dumps(data["Later_Epoch_Smart_Events"][0]["category"]))
    message.append("    Sub Category        : " + json.dumps(data["Later_Epoch_Smart_Events"][0]["epoch2_details"]["sub_category"]))
    print(message)
    post_resp = post_message("\n".join(message))