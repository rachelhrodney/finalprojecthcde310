import urllib.parse, urllib.request, urllib.error, json
import requests

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

url = 'https://api.imgflip.com/get_memes'

userinput = 'woman'
listofmemes = []

def findmemes(userinput):
    try:
        return requests.get(url = url)

    except urllib.error.URLError as e:
        print(e)
        return 'None'


requeststr = findmemes(userinput)
data = requeststr.json()
results = data['data']['memes']
for meme in results:
    namestr = meme['name'].split()
    for word in namestr:
        if word.lower() == userinput.lower():
            listofmemes.append(meme['url'])
    if listofmemes is []:
        listofmemes[0] = 'This meme does not exist'

print(listofmemes)