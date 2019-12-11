import json
import httplib, base64, Password
import webapp2, os, jinja2
import urllib2,logging, urllib
#urllib.request, urllib.error

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def safeMeme(numberofmemes):
    memeURL = 'https://meme-api.herokuapp.com'
    try:
        return urllib2.urlopen(memeURL + '/gimme/' + str(numberofmemes))
    except urllib2.URLError as e:
        logging.error(e)
        return 'None'
def getMemes(numberofmemes = 3):
    listofmemes = []
    requeststr = safeMeme(numberofmemes)
    data = json.load(requeststr)
    results = data['memes']
    for meme in results:
        listofmemes.append(meme['url'])
        if listofmemes is []:
            listofmemes[0] = 'This meme does not exist'
            logging.error('No memes in list')
    return listofmemes

def get_image_features(img_url):
    # Code from https://www.mssqltips.com/sqlservertip/5955/azure-vision-service-and-face-api-example-with-python/
    headers = {
        # Request headers.
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': Password.microsoftKey,
    }
    params = urllib.urlencode({
        # Request parameters. All of them are optional.
        'visualFeatures': 'Categories,Description,Color,Adult,Brands,Faces,ImageType,Objects',
        'language': 'en',
    })
    body = "{'url':'" + img_url + "'}"
    try:
        # Execute the REST API call and get the response.
        conn = httplib.HTTPSConnection(Password.uri)
        conn.request("POST", "/vision/v2.0/analyze?%s" % params, body, headers)
        response = conn.getresponse()
        data = response.read()
        parsed = json.loads(data.decode("UTF-8"))
        if response is not None:
            return parsed
        conn.close()
    except Exception as e:
        logging.error('Error:', e)

def get_text_features(img_url):
    #Code from https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts/python-print-text
    url = Password.microsoftBase + "vision/v2.1/ocr"
    headers = {'Ocp-Apim-Subscription-Key': Password.microsoftKey,'Content-type':'application/json'}
    params = {'mode': 'Printed'}
    body = {'url': img_url}
    logging.info(img_url)
    fullurl = url + "?" + urllib.urlencode(params)
    req = urllib2.Request(fullurl,headers=headers,data=json.dumps(body))
    resp = urllib2.urlopen(req)
    analysis = json.load(resp)
    #response = requests.post(url, headers = headers, params = params, json = body)
    #response.raise_for_status()
    #analysis = response.json()
    return analysis


def overview(dict):
    phrase = ''
    if dict['adult']['isAdultContent']:
        phrase += 'NSFW: Adult Content Detected (%.0f/100 confidence).<br>' %dict['adult']['adultScore']*100
    if dict['color']['isBWImg']:
        phrase += 'A black and white image'
    else:
        phrase += 'An image'
    if dict['imageType']['clipArtType'] != 0:
        phrase += ' containing clip art'
        if dict['imageType']['lineDrawingType'] != 0:
            phrase += ' and line drawings'
    elif dict['imageType']['lineDrawingType'] != 0:
        phrase += ' containing line drawings'
    if dict['color']['dominantColorBackground'] != 'None':
        phrase += ' with a %s background' %dict['color']['dominantColorBackground'].lower()
    phrase += '.<br>'
    return phrase

def imagedetails(dict):
    phrase = 'The image is of '
    phrase = phrase + dict['description']['captions'][0]['text']
    logging.info(pretty(dict))
    phrase += ' (confidence: %.0f/100).<br>'%(float(dict['description']['captions'][0]['confidence'])*100)
    objects = dict['objects']
    if dict['objects'] is not None and len(dict['objects']) != 0:
        phrase += '%d objects found:' %len(dict['objects'])
        for object in dict['objects']:
            phrase += "<br>A %s (%.0f/100 confident)" %(object['object'], (float(object['confidence'])*100))
    return phrase



def get_words(dict):
    regionCounter = 0
    if len(dict['regions']) == 0:
        return ""
    phrase = "Image Text:<br>"
    for region in dict['regions']:
        if regionCounter != 0:
            phrase += '<br>'
        regionCounter +=1
        lineCounter = 0
        for line in region['lines']:
            if lineCounter != 0:
                phrase += '<br>'
            lineCounter += 1
            for word in line['words']:
                phrase += word['text'] + ' '
    return phrase

def urlToDescription(image):
    imagedict = get_image_features(image)
    worddict = get_text_features(image)
    description = '[Image Description: <br>'
    description += overview(imagedict) +'<br>'
    description += imagedetails(imagedict)
    description += get_words(worddict)
    description += '<br>End Description]'
    return description

class MainHandler(webapp2.RequestHandler):
    def get(self):
        data = {}
        req = self.request
        numMemes = req.get('num', 3)
        data['numMemes'] = numMemes
        memeURLList = getMemes(numMemes)
        memes = []
        for memeurl in memeURLList:
            dict = {}
            dict['image'] = memeurl
            dict['text'] = urlToDescription(memeurl)
            memes.append(dict)
        data['memes'] = memes

        JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                               extensions=['jinja2.ext.autoescape'],
                                               autoescape=True)
        template = JINJA_ENVIRONMENT.get_template('finalwebpagetemplate.html')
        self.response.write(template.render(data))

application = webapp2.WSGIApplication([('/',MainHandler)], debug =True)

