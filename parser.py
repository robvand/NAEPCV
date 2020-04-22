import requests
import json

#WebEx details
roomId = ""
bearer = ''

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

    message = []
    message.append("****************")
    message.append("    Description         : " + json.dumps(data["Later Epoch Smart Events"][0]["epoch2_details"]["description"]))
    message.append("    Mnemonic            : " + json.dumps(data["Later Epoch Smart Events"][0]["epoch2_details"]["mnemonic"]))
    message.append("    Event Severity      : " + json.dumps(data["Later Epoch Smart Events"][0]["epoch2_details"]["severity"]))
    message.append("    Category            : " + json.dumps(data["Later Epoch Smart Events"][0]["category"]))
    message.append("    Sub Category        : " + json.dumps(data["Later Epoch Smart Events"][0]["epoch2_details"]["sub_category"]))
    print(message)
    post_resp = post_message("\n".join(message))