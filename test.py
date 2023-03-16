import json
import requests

segments: list = json.load(open('segments.json'))

proxies = [
    '167.172.238.6:9990',
    '46.101.85.55:443',
    '167.172.238.15:9997',
    '167.172.96.117:45345',
    '167.172.173.210:42895',
    '217.180.218.36:8080',
    '82.165.29.197:3128',
    '185.226.118.159:1080'
]

proxy_index = 0

for i, url in enumerate(segments[:5]):
    
    prox = {
        'https': proxies[proxy_index]
    }
    
    print(f'{prox = }')
    
    proxy_index = (proxy_index + 1) % len(proxies)
    
    res = requests.get(url, proxies = prox)
    
    print(res.status_code)