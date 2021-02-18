import json
import requests
import config 

data = {
    'client_id': config.client_id,
}

def make_json(text):
    text_list = text.split('&')
    json_dict = {}
    for item in text_list:
        k, v = item.split('=')
        if '%3A' in v:
            v = v.replace('%3A', ':')
        if '%2F' in  v:
            v = v.replace('%2F', '/')
        json_dict[k] = v
    return json_dict

response = requests.post('https://github.com/login/device/code', data=data)
json = make_json(response.text)
print(json)
x = input()
data = {
    'client_id': config.client_id,
    'client_secret': config.client_secret,
    'device_code': config.device_code,
    'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
}
response = requests.post('https://github.com/login/oauth/access_token', data=data)
json = make_json(response.text)
print(json)
for i in range(100):
    auth = ('username', config.authorization_code)
    response = requests.get('https://api.github.com/users/octocat', auth=auth)
    # print(json.loads(response.text))
    print(i)

