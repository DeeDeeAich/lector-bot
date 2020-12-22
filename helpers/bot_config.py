import json

def load():
    with open('config.json', 'r') as f:
        data = json.load(f)
        
    return {
        'prefix' : data['prefix'],
        'token'  : data['token']
    }