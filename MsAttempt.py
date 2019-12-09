import http.client, urllib.request, urllib.parse, urllib.error, base64, json, Password, requests


image = 'https://www.rd.com/wp-content/uploads/2018/06/02_In-full-flight.jpg'
TestImage = ['https://www.rd.com/wp-content/uploads/2018/06/02_In-full-flight.jpg', 'https://cdn.ebaumsworld.com/2019/07/05/031706/86009023/womanyellingatcatmeme9.jpg', 'https://i.imgflip.com/24bjna.jpg']


def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

#Code from https://www.mssqltips.com/sqlservertip/5955/azure-vision-service-and-face-api-example-with-python/
def get_image_features(img_url):
    headers = {
        # Request headers.
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': Password.microsoftKey,
    }
    params = urllib.parse.urlencode({
        # Request parameters. All of them are optional.
        'visualFeatures': 'Categories,Description,Color,Adult,Brands,Faces,ImageType,Objects',
        'language': 'en',
    })
    body = "{'url':'" + img_url + "'}"
    try:
        # Execute the REST API call and get the response.
        conn = http.client.HTTPSConnection(Password.uri)
        #print('Conn:', conn)
        conn.request("POST", "/vision/v2.0/analyze?%s" % params, body, headers)
        response = conn.getresponse()
        #print('response type:', type(response))
        data = response.read()
        # 'data' contains the JSON response.
        parsed = json.loads(data.decode("UTF-8"))
        #print(pretty(parsed))
        if response is not None:
            return parsed
        conn.close()
    except Exception as e:
        print('Error:')
        print(e)

def get_text_features(img_url):
    #Code from https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts/python-print-text
    url = Password.microsoftBase + "vision/v2.1/ocr"
    headers = {'Ocp-Apim-Subscription-Key': Password.microsoftKey,}
    params = {'mode': 'Printed'}
    body = {'url': img_url}
    response = requests.post(url, headers = headers, params = params, json = body)
    #print(type(response))
    response.raise_for_status()
    analysis = response.json()
    #print(type(analysis))
    #print(pretty(analysis))
    return analysis

def urlToDescription(image):
    jsonData = get_image_features(image)
    #print(pretty(jsonData))
    desc = jsonData['description']['captions'][0]['text']
    jsonText = get_text_features(image)
    print(Description(jsonData, jsonText))
    # phrase = get_words(jsonText)
    # #print(pretty(jsonText))
    # print("start description:")
    # print(desc)
    # print('Text:')
    # print(phrase)
    # print('End Description')

def Description(imagedict, worddict):
    description = '[Image Description:\n'
    description += overview(imagedict) +'\n'
    description += imagedetails(imagedict)
    description += get_words(worddict)
    description += '\nEnd Description]'
    return description

def overview(dict):
    phrase = ''
    if dict['adult']['isAdultContent']:
        phrase += 'NSFW: Adult Content Detected (%.0f/100 confidence).\n' %dict['adult']['adultScore']*100
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
    phrase += '.'
    return phrase

def imagedetails(dict):
    phrase = 'The image is of '
    phrase += dict['description']['captions'][0]['text']
    phrase += ' (confidence: %.0f/100).\n'%dict['description']['captions'][0]['confidence']*100
    objects = dict['objects']
    if dict['objects'] is not None and len(dict['objects']) != 0:
        phrase += '%d objects found:' %len(dict['objects'])
        for object in dict['objects']:
            phrase += "\nA %s (%.0f/100 confident)(Location TBD)" %(object['object'], float(object['confidence'])*100)
    return phrase

def get_words(dict):
    #print(pretty(dict))
    regionCounter = 0
    if len(dict['regions']) == 0:
        return ""
    phrase = "Image Text:\n"
    for region in dict['regions']:
        if regionCounter != 0:
            phrase += '\n'
        regionCounter +=1
        lineCounter = 0
        for line in region['lines']:
            if lineCounter != 0:
                phrase += '\n'
            lineCounter += 1
            for word in line['words']:
                phrase += word['text'] + ' '
    return phrase





urlToDescription(image)
print('\n')
urlToDescription('https://img.buzzfeed.com/buzzfeed-static/static/2018-08/14/13/asset/buzzfeed-prod-web-06/sub-buzz-26630-1534268868-2.png?downsize=700:*&output-format=auto&output-quality=auto')

# for photo in TestImage:
#     urlToDescription(photo)

