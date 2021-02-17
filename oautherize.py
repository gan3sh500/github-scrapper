import json
import requests

data = {
    'client_id': 'here'
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
print(make_json(response.text))
