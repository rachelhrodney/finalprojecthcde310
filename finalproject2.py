import urllib.parse, urllib.request, urllib.error, json
import requests

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

url = 'https://meme-api.herokuapp.com'

numberofmemes = 5
listofmemes = []

def findmemes(numberofmemes):
    try:
        return urllib.request.urlopen(url + '/gimme/' + str(numberofmemes))
        # requests.post(url = ('https://meme-api.herokuapp.com' + '/gimme/' + str(numberofmemes)))

    except urllib.error.URLError as e:
        print(e)
        return 'None'

requeststr = findmemes(numberofmemes)
data = json.load(requeststr)
results = data['memes']
for meme in results:
    listofmemes.append(meme['url'])
    if listofmemes is []:
        listofmemes[0] = 'This meme does not exist'

print(listofmemes)