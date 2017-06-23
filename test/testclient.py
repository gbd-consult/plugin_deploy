import requests
import json

if __name__ == '__main__':
    headers = {
            'X-Github-Delivery': 'testtest',
            'User-Agent': 'GitHub-Hookshot/044aadd',
            'Content-Type': 'application/json',
            'Content-Length': '6615',
            'X-GitHub-Event': 'release'
            }
    with open('example.json', 'r') as f:
        data = json.loads(f.read())
    r = requests.post('http://localhost:5000/plugin-release', json = data, headers = headers)
