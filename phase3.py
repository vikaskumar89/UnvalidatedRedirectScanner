import json
import requests
import logging
from urllib import urlopen
from urllib import urlencode
import urllib, urllib2
import cookielib
from urllib2 import HTTPError, URLError
import sys


def writeoutput(maps):
    print "Writing output"
    phase3output["exploits"] = vulnerlist
    with open('output/phase3output.json', 'w') as w:
        json.dump(maps, w, indent=2)


def forminjectiondictionary(key, value, method):
    injectdic = dict()
    paramdict = dict()
    paramdict["key"] = key
    paramdict["value"] = value
    paramdict["type"] = method
    ls = list()
    ls.append(paramdict)
    injectdic["params"] = ls
    return injectdic


def isvulnerabilitypresent(inp):
    s = str(inp)
    if s.find("www.google.com") > 0 and app_name not in s:
        return True
    else:
        return False


def urlalreadyadded(pageurl):
    for ele in vulnerlist:
        if ele["url"] == pageurl:
            logging.info("URL is already present in the bug dictionary %s", pageurl)
            return False
    return True


def storevulnerabilitydetails(method, pageurl, paramsdict):
    if pageurl not in pathset:
        vdc = dict()
        vdc["url"] = pageurl
        vdc["type"] = method
        vdc["params"] = paramsdict
        vulnerlist.append(vdc)


def extractheadermethod(params, pagedic, pageurlt):
    logging.info("Inside HEADER method")


def removeasciitext(postdc):
    dc = dict()
    for k, v in postdc.item():
        dc[str(k)[2:-1]] = str(v)[2:-1]
    return dc


def encodeparams(postparamdictionary):
    #logging.info('Inside encoded params method for %s', postparamdictionary)
    #postparamdictionary = removeasciitext(postparamdictionary)
    try:
        if postparamdictionary is not None and postparamdictionary != "":
            for x,y in postparamdictionary.items():
                if y is None or y is '':
                    postparamdictionary[x] = ""
                else:
                    if not isinstance(y, basestring):
                        del postparamdictionary[x]

            return urlencode(postparamdictionary)
    except:
        return urlencode("")


def sendpostrequest(postparamdictionary, method, actionlink, pageurl):
    #logging.info('Inside send post request method ')
    edc = encodeparams(postparamdictionary)
    try:
        resp = opener.open(actionlink, edc)
        if isvulnerabilitypresent(resp.url):
            storevulnerabilitydetails(method, actionlink,postparamdictionary)
            return True
    except HTTPError as h:
        logging.error('Error at %s %s', actionlink, h.reason)
    except URLError as e:
        logging.error('Error at %s %s', actionlink, e.reason)
    except:
        logging.error('Error at %s', actionlink)

    return False


def makepostparamdictionary(paramlist):
    #logging.info('Inside makepostparamdictionary method')
    pdiction = dict()
    for ele in paramlist:
        if ele["name"] == "sesskey":
            pdiction[ele["name"]] = sesskey
        elif ele["name"] == "cancel":
            continue
        elif ele["name"] is not None:
            pdiction[ele["name"]] = ele["value"]

    return pdiction


def launchpostattack(paramlist, method, actionlink, pageurl):
    #logging.info("Inside launch post attack method for url %s", pageurl)
    postparamdictionary = makepostparamdictionary(paramlist)
    for key,val in postparamdictionary.items():
        #print(key,":",val)
        oldval = val
        for pl in payload:
            postparamdictionary[key] = pl
            if sendpostrequest(postparamdictionary,method, actionlink, pageurl):
                pathset.add(actionlink)
                logging.info("Vulnerability found at %s", pageurl)
                return

        postparamdictionary[key] = oldval


def extractpostmethod(type,pagedict,pageurl):
    #logging.info("Inside extractpostmethod method")
    typeList = pagedict[type]
    pageurl = typeList["pageurl"]
    for forms in typeList["formList"]:
        actionlink = forms["formactionLink"]
        method = forms["method"]
        paramList = forms["params"]
        launchpostattack(paramList, method, actionlink, pageurl)


def launchgetattack(path, paramsdict):
    for param in paramsdict:
        oldval = paramsdict[param]
        for pl in payload:
            paramsdict[param] = pl
            edc = urlencode(paramsdict)
            url = path + '?' +edc
            try:
                resp = opener.open(url)
                if isvulnerabilitypresent(resp.url):
                    pathset.add(url)
                    storevulnerabilitydetails("GET", path, paramsdict)
                    return
            except HTTPError as h:
                logging.error('Page cannot be found %s', path)
            except URLError as e:
                logging.error('URL is malformed %s', path)
            except:
                logging.error('Something went wrong at %s', path)
        paramsdict[param] = oldval


def extractgetmethod(pagedict,pageurl):
    #logging.info("Extracting URL list parameters")
    path = pagedict["path"]
    paramsdict = pagedict["params"]
    if "sesskey" in paramsdict.keys():
        paramsdict["sesskey"] = sesskey
    launchgetattack(path, paramsdict)


def getinjectionpoint(injections):
    #uri = injections["uri"]
    for pages in injections:
        #logging.info('Items in List are---- %s',pages)
        pagedict = injections[pages]
        for params in pagedict:
            if params == "body" and len(pagedict["body"]) > 0:
                extractpostmethod(params, pagedict, pages)
            elif params == "getlist" and len(pagedict["getlist"]) > 0:
                extractgetmethod(pagedict["getlist"], pages)


def formatoutput(phase3output):
    phase3output["exploits"] = []
    phase3output["appname"] = app_name
    phase3output["logindetails"] = logindetails
    #phase3output["loginurl"] = loginurl
    phase3output["baseurl"] = baseurl


def startredirectinjections(redirect):
    try:
        for eachitem in redirect:
            url = eachitem["from_url"]
            if url in pathset:
                continue
            num = len(eachitem["params"])
            if not num == 0:
                paramsdc = eachitem["params"]
                path = paramsdc["path"]
                datadc = paramsdc["params"]
                edc = urlencode(datadc)
                surl = path + "?" + edc
            resp = opener.open(url)
            if isvulnerabilitypresent(resp.url):
                pathset.add(url)
                logging.info('Referrer Bug found at %s', url)
                if num ==0:
                    storevulnerabilitydetails("redirect", url, {})
                else:
                    storevulnerabilitydetails("redirect",path, datadc)

    except HTTPError as h:
        logging.error('Page cannot be found %s', url)
    except URLError as e:
        logging.error('URL is malformed %s', url)
    except:
        logging.error('Something went wrong at %s', url)

baseurl = ""
sess_id = ""
app_name = ""
logindetails = dict()
cookies = dict()
phase3output = dict()
injectiondict = dict()
payload = []
vulnerlist = []
pathset = set()
redirect = dict()
logging.basicConfig(filename='logs/phase3.log',level=logging.DEBUG)
logging.info('Starting executing phase 3 of Unvalidated Redirect URL')


with open('output/phase1Output.json') as f:
    ele = json.load(f)
    app_name = "app10"
    baseurl = ele["baseurl"]
    #loginurl = ele["loginurl"]
    logindetails = []#ele["logindetails"]
    #cookie = ele["cookies"]
    injectiondict = ele["injections"]

with open('output/phase2output.json') as f:
    file = json.load(f)
    payload = file["payload"]

def readredirectfile():
    with open('output/phase1Redirect.json') as f:
        file = json.load(f)
        redirect = file["redirects"]
        return redirect

for ele in logindetails:
    username = ele["username"]
    password = ele["password"]

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('Referer','https://www.google.com')]
sesskey = "http://www.google.com"
# login_data = urllib.urlencode({'username' : username, 'password' : password})
# lp = opener.open('https://app2.com/login/index.php', login_data)
# print lp.url
# s = str(lp.read())
# index = s.index("sesskey")
# if index >0:
#     skey = s[index:index+20]
#     name, sesskey = skey.split(":")
#     sesskey = str(sesskey).replace("\"", "")
#     print sesskey
formatoutput(phase3output)
getinjectionpoint(injectiondict)
redirectdc = readredirectfile()
startredirectinjections(redirectdc)
writeoutput(phase3output)
logging.info('Phase 3 of Unvalidated Redirect URL has ended. Check the output file for injection points')