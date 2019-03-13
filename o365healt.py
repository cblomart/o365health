import bottle
import binascii
import os
import os.path
import base64
import json
import adal
import jwt
import requests

from bottle import request, abort, template, get, post, run, hook, response, redirect, static_file
from bottle.ext import beaker
from cachetools import cached, TTLCache

configfile = 'o365health.json'
azuread_authority_uri = 'https://login.microsoftonline.com'
azuread_resource_uri = "https://manage.office.com"
required_role = "ServiceHealth.Read" 
ttl = 60

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}

healthapp = beaker.middleware.SessionMiddleware(bottle.app(), session_opts)

# check for applicaiton configuration
infos = { 'tenant_id': '', 'client_id': '', 'client_secret': '' }
# access tokne
token = ""
# local memory cache for different objects
cache = {}

if os.path.isfile(configfile):
    with open(configfile) as infile:
        infos = json.load(infile)
    if infos['tenant_id']=='' or infos['client_id']=='' or infos['client_secret']=='':
        infos = { 'tenant_id': '', 'client_id': '', 'client_secret': '' }
        print('invalid config file: deleting %s\n' % configfile)
        os.remove(configfile)

if 'O365HEALTH_TENANT_ID' in os.environ and 'O365HEALTH_CLIENT_ID' in os.environ and 'O365HEALTH_CLIENT_SECRET' in os.environ:
    infos['tenant_id'] = os.environ['O365HEALTH_TENANT_ID']
    infos['client_id'] = os.environ['O365HEALTH_CLIENT_ID']
    infos['client_secret'] = os.environ['O365HEALTH_CLIENT_SECRET']
    with open(configfile, 'w') as outfile:
        json.dump(infos, outfile)

def authenticate_client_key():
    global token
    if infos['tenant_id']=='' or infos['client_id']=='' or infos['client_secret']=='':
        print("application not registerd please register the application\n")
        return
    authority_uri = azuread_authority_uri  + '/' + infos['tenant_id']
    context = adal.AuthenticationContext(authority_uri, api_version=None)
    try:
        mgmt_token = context.acquire_token_with_client_credentials(azuread_resource_uri, infos['client_id'], infos['client_secret'])
    except Exception as e:
        print("error getting token:\n%s\n" % e)
        return
    if "accessToken" not in mgmt_token:
        print("no access token in response\n")
        return
    token = mgmt_token["accessToken"]

def tokenvalid():   
    valid = False
    try:
        tokeninfos = jwt.decode(
            token, 
            audience=azuread_resource_uri,
            options={
                'verify_signature':False,
                'require_exp': True,
                'require_iat': True,
                'require_nbf': True
            }
        )
        if required_role in tokeninfos['roles']:
            valid = True
    except Exception as e:
        print("could not decode token:\n%s\n" % e)
    return valid

@cached(cache=TTLCache(maxsize=1, ttl=ttl))
def getstatus():
  headers = {'Authorization': 'Bearer ' + token}
  url = azuread_resource_uri + "/api/v1.0/" + infos['tenant_id'] + "/ServiceComms/CurrentStatus"
  response = requests.get(url, headers=headers)
  json = response.json()
  if 'value' not in json:
      return None
  return json['value']

# Static Routes
@get("/static/<filepath:path>")
def static(filepath):
    response.set_header("Cache-Control", "public, max-age=604800")
    return static_file(filepath, root="static")

# csrf protection
@hook('before_request')
def csrf_protect():
    if request.path.startswith("/static/") or request.path=="/favicon.ico":
        if request.method in  ['GET','HEAD']:
            return
        else:
            abort(403,text="unauthorized method")
    # first attempt to renew
    if token is None or token=="" or not tokenvalid():
        authenticate_client_key()
    # then fail
    if token is None or token=="" or not tokenvalid():
        abort(500,text="invalid oauth token")
    if request.method != 'POST':
        return
    # check csrf only for POST
    sess = request.environ['beaker.session']
    req_token = request.forms.get('csrf_token')
    # if no token is in session or it doesn't match the request one, abort
    if 'csrf_token' not in sess or sess['csrf_token'] != req_token:
        abort(403,text="invalid csrf token")

@get('/api/status')
def getapistatus():
    statuses = getstatus()
    res = []
    for status in statuses:
        print(status)
        item ={}
        item['Workload']=status['Workload']
        item['WorkloadDisplayName']=status['WorkloadDisplayName']
        item['Indidents']=len(status['IncidentIds'])
        item['StatusTime']=status['StatusTime']
        res.append(item)
    response.headers['Content-Type'] = 'application/json'
    return json.dumps(res)

@get('/api/status/<workload>')
def getapiworkloadstatus(workload):
    statuses = getstatus()
    for status in statuses:
        if status['Workload']==workload:
            response.headers['Content-Type'] = 'application/json'
            return json.dumps(status)

@get('/')
def getindex():
    global cache
    if infos['tenant_id']=='' or infos['client_id']=='' or infos['client_secret']=='':
        redirect("/config")
    # get office 365 status
    statuses = getstatus()
    return template('index.tpl',statuses=statuses)

@get('/config')
def getconfig():
    if infos['tenant_id']!='' and infos['client_id']!='' and infos['client_secret']!='':
        redirect('/')
    sess = request.environ['beaker.session']
    sess['csrf_token'] = base64.b64encode(os.urandom(30)).decode()
    return template('config.tpl',csrf_token=sess['csrf_token'])

@post('/config')
def postconfig():
    if infos['tenant_id']!='' and infos['client_id']!='' and infos['client_secret']!='':
        abort(403,text="application informations already present")
    if request.forms.get('tenant_id')!='' and request.forms.get('client_id')!='' and request.forms.get('client_secret')!='':
        infos['tenant_id'] = request.forms.get('tenant_id')
        infos['client_id'] = request.forms.get('client_id')
        infos['client_secret'] = request.forms.get('client_secret')
        with open(configfile, 'w') as outfile:
            json.dump(infos, outfile)
        redirect('/')

run(app=healthapp, host='localhost', port=8080)