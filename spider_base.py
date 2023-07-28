import requests

def get_headersDict(text):
    text = text.strip().split('\n')
    headers = {x.split(':', 1)[0].strip(): x.split(':', 1)[1].strip() for x in text}
    return headers


def get_headersDict_2(text):
    '''
    针对新的浏览器复制的headers类型
    '''
    lis = text.strip().split('\n')
    headers = {}
    for i in range(len(lis)):
        if i % 2 == 0:
            key = lis[i][:-1].strip()
        else:
            value = lis[i].strip()
            headers[key] = value
    return headers

def getDict(text, patten = '&', patten2 = '=', stri_patten = ''):
    lis = text.split(patten + stri_patten)
    cookieDict = {}
    for str in lis:
        cookie = str.strip().split(stri_patten + patten2)
        cookieDict[cookie[0].strip(stri_patten)] = cookie[1].strip(stri_patten)
    return cookieDict

def getHTMLText(url, headers = {}, params = {}, cookies = {}, encoding = ''):
    try_time = 0
    while try_time >= 0:
        try:
            r=requests.get(url, headers = headers, params = params, cookies = cookies)
            r.raise_for_status()
            if encoding:
                r.encoding = encoding
            else:
                r.encoding = r.apparent_encoding
            return r.text
        except:
            try_time += 1

def get_content(url, headers = {}, params = {}, cookies = {}):
    try_time = 0
    while try_time >= 0:
        try:
            r = requests.get(url, headers = headers, params = params, cookies = cookies)
            r.raise_for_status()
            return r.content
        except:
            try_time += 1

def post_content(url, headers = {}, data = {}):
    try_time = 0
    while True:
        try:
            r = requests.post(url, data = data, headers = headers)
            r.raise_for_status()
            return r.content
        except:
            try_time += 1

def post_HTMLText(url, headers = {}, cookies = {}, data = {}, encoding = ''):
    while True:
        try:
            r = requests.post(url, data = data, headers = headers, cookies = cookies)
            r.raise_for_status()
            if encoding:
                r.encoding = encoding
            else:
                r.encoding = r.apparent_encoding
            return r.text
        except:
            pass

def res2cookie(response):
    cookies = requests.utils.dict_from_cookiejar(response.cookies)
    return cookies