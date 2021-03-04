import json
import requests 

import webbrowser
from cselector import yes_or_no


def read_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)


def dump_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def get_device_code(config):
    data = {
        'client_id': config["client_id"],
    }
    headers = {
        "accept": "application/json",
    }
    response = requests.post('https://github.com/login/device/code', data=data, headers=headers)
    response_json = response.json()
    print(f"User Code : {response_json['user_code']}")
    webbrowser.open(response_json["verification_uri"], new=2)
    ret = yes_or_no(question="Did you authorize the device?",default="y")
    if ret:
        config["device_code"] = response_json["device_code"]
    else:
        raise ValueError('Not authorized.')
    return config


def get_authorization_code(config):
    data = {
    'client_id': config["client_id"],
    'device_code': config["device_code"],
    'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
    }
    headers = {
        "accept": "application/json",
    }
    response = requests.post('https://github.com/login/oauth/access_token', data=data, headers=headers)
    response_json = response.json()
    config["authorization_code"] = response_json["access_token"]
    return config


def main():
    config = read_json("config.json")
    if "client_id" not in config:
        raise ValueError("No client id in config.json.")
    if "device_code" not in config:
        config = get_device_code(config)
    if "authorization_code" not in config:
        config = get_authorization_code(config)
    dump_json(config, "config.json")
    print("Authorization ready.")

if __name__ == '__main__':
    main()
