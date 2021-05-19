import requests

url = 'https://databases.lovd.nl/shared/download/all/gene/GAA'
r = requests.get(url)

data = r.content.decode('utf-8').splitlines()
for line in data:
    if line.startswith('#'):
        print(line)