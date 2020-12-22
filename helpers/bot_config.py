import json
import sys


def load():
    filename = 'config.json'
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        return {
            'prefix' : data['prefix'],
            'token'  : data['token']
        }

    except FileNotFoundError:
        print(f'\'{filename}\' does not exist.')
        sys.exit()

    except json.decoder.JSONDecodeError:
        print(f'\'{filename}\' is malformed.')
        sys.exit()

    except KeyError:
        print(f'\'{filename}\' is missing information.')
        sys.exit()