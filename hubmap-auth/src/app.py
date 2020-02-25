from flask import Flask, request, jsonify, make_response, Response, render_template, session, redirect, url_for
from globus_sdk import AuthClient, AccessTokenAuthorizer, ConfidentialAppAuthClient
import requests
import json
from cachetools import cached, TTLCache
import functools
import re
import os

# HuBMAP commons
from hubmap_commons.hm_auth import AuthHelper

# For debugging
from pprint import pprint


# Specify the absolute path of the instance folder and use the config file relative to the instance path
app = Flask(__name__, instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance'), instance_relative_config=True)
app.config.from_pyfile('app.cfg')

# Remove trailing slash / from URL base to avoid "//" caused by config with trailing slash
app.config['FLASK_APP_BASE_URI'] = app.config['FLASK_APP_BASE_URI'].strip('/')

# LRU Cache implementation with per-item time-to-live (TTL) value
# with a memoizing callable that saves up to maxsize results based on a Least Frequently Used (LFU) algorithm
# with a per-item time-to-live (TTL) value
# Here we use two hours, 7200 seconds for ttl
cache = TTLCache(maxsize=app.config['CACHE_MAXSIZE'], ttl=app.config['CACHE_TTL'])

####################################################################################################
## Default route
####################################################################################################

@app.route('/', methods = ['GET'])
def home():
    return "This is HuBMAP Web Gateway :)"


####################################################################################################
## API Auth, no UI
####################################################################################################

@app.route('/cache_clear', methods = ['GET'])
def cache_clear():
    cache.clear()
    return "All function cache cleared."


# Auth for private API services
# All endpoints access need to be authenticated
# Direct access will see the JSON message
# Nginx auth_request module won't be able to display the JSON message for 401 response
@app.route('/api_auth', methods = ['GET'])
def api_auth():
    wildcard_delimiter = "<*>"
    # The regular expression pattern takes any alphabetical and numerical characters, also other characters permitted in the URI
    regex_pattern = "[a-zA-Z0-9_.:#@!&=+*-]+"

    # Debugging
    pprint("===========request.headers=============")
    pprint(request.headers)

    # Nginx auth_request only cares about the response status code
    # it ignores the response body
    # We use body here only for direct visit to this endpoint
    response_200 = make_response(jsonify({"message": "OK: Authorized"}), 200)
    response_401 = make_response(jsonify({"message": "ERROR: Unauthorized"}), 401)
    
    # In the json, we use authority as the key to differ each service section
    authority = None
    method = None
    endpoint = None

    # URI = scheme:[//authority]path[?query][#fragment] where authority = [userinfo@]host[:port]
    # This "Host" header is nginx `$http_host` which contains port number, unlike `$host` which doesn't include port number
    # Here we don't parse the "X-Forwarded-Proto" header because the scheme is either HTTP or HTTPS
    if ("X-Original-Request-Method" in request.headers) and ("Host" in request.headers) and ("X-Original-URI" in request.headers):
        authority = request.headers.get("Host")
        method = request.headers.get("X-Original-Request-Method")
        endpoint = request.headers.get("X-Original-URI")

    # method and endpoint are always not None as long as authority is not None
    if authority is not None:
        # Load endpoints from json
        data = load_file(app.config['API_ENDPOINTS_FILE'])

        if authority in data.keys():
            # First pass, loop through the list to find exact static match
            for item in data[authority]:
                if (item['method'].upper() == method.upper()) and (wildcard_delimiter not in item['endpoint']):
                    # Ignore the query string
                    target_endpoint = endpoint.split("?")[0]
                    # Remove trailing slash for comparison
                    if item['endpoint'].strip('/') == target_endpoint.strip('/'):
                        if api_access_allowed(item, request):
                            return response_200
                        else:
                            return response_401
                    
            # Second pass, loop through the list to do the wildcard match
            for item in data[authority]:
                if (item['method'].upper() == method.upper()) and (wildcard_delimiter in item['endpoint']):
                    # First replace all occurrences of the wildcard delimiters with regular expression
                    endpoint_pattern = item['endpoint'].replace(wildcard_delimiter, regex_pattern)
                    # Ignore the query string
                    target_endpoint = endpoint.split("?")[0]
                    # If the full url path matches the regular expression pattern, 
                    # return a corresponding match object, otherwise return None
                    target_endpoint = endpoint.split("?")[0]
                    # Remove trailing slash for comparison
                    if re.fullmatch(endpoint_pattern.strip('/'), target_endpoint.strip('/')) is not None:
                        if api_access_allowed(item, request):
                            return response_200
                        else:
                            return response_401

            # After two passes and still no match found
            # It could be either unknown request method or unknown path
            return response_401

        # Handle the cases when authority not in data.keys() 
        return response_401
    else:
        # Missing lookup_key
        return response_401


# Auth for file service
# Nginx auth_request module won't be able to display the JSON message for 401 response
@app.route('/file_auth', methods = ['GET'])
def file_auth():
    # Debugging
    pprint("===========request.headers=============")
    pprint(request.headers)

    # Nginx auth_request only cares about the response status code
    # it ignores the response body
    # We use body here only for direct visit to this endpoint
    response_200 = make_response(jsonify({"message": "OK: Authorized"}), 200)
    response_401 = make_response(jsonify({"message": "ERROR: Unauthorized"}), 401)
    response_403 = make_response(jsonify({"message": "ERROR: Forbidden"}), 403)
  
    # The file path in URL is the same as file system path
    endpoint = None

    # URI = scheme:[//authority]path[?query][#fragment] where authority = [userinfo@]host[:port]
    # This "Host" header is nginx `$http_host` which contains port number, unlike `$host` which doesn't include port number
    # Here we don't parse the "X-Forwarded-Proto" header because the scheme is either HTTP or HTTPS
    if ("X-Original-Request-Method" in request.headers) and ("X-Original-URI" in request.headers):
        method = request.headers.get("X-Original-Request-Method")
        endpoint = request.headers.get("X-Original-URI")

    # File access only via http GET
    if method.upper() == 'GET':
        if endpoint is not None:
            # Parse the path to get the dataset UUID
            # Remove the leading slash before split
            path_list = endpoint.strip("/").split("/")
            dataset_uuid = path_list[0]
            # Check if the globus token is valid for accessing this secured dataset
            code = get_file_access(dataset_uuid, request)

            if code == 200:
                return response_200
            elif code == 401:
                return response_401
            elif code == 403:
                return response_403
        else: 
            # Missing dataset UUID in path
            return response_401
    else:
        # Wrong http method
        return response_401


####################################################################################################
## Internal Functions Used By API Auth and File Auth
####################################################################################################

@cached(cache)
def load_file(file):
    with open(file, "r") as f:
        data = json.load(f)
        return data

# Initialize AuthHelper (AuthHelper from HuBMAP commons package)
# HuBMAP commons AuthHelper handles "MAuthorization" or "Authorization"
def init_auth_helper():
    if AuthHelper.isInitialized() == False:
        auth_helper = AuthHelper.create(app.config['GLOBUS_APP_ID'], app.config['GLOBUS_APP_SECRET'])
    else:
        auth_helper = AuthHelper.instance()
    
    return auth_helper

# Get user infomation dict based on the http request(headers)
# `group_required` is a boolean, when True, 'hmgroupids' is in the output
def get_user_info_for_access_check(request, group_required):
    auth_helper = init_auth_helper()
    return auth_helper.getUserInfoUsingRequest(request, group_required)

# Check if a given dataset requries globus group access
# For dataset UUIDs that are listed in the secured_datasets.json, also check
# if the globus token associated user is a member of the specified group assocaited with the UUID
def get_file_access(dataset_uuid, request):
    allowed = 200
    authentication_required = 401
    authorization_required = 403

    user_info = get_user_info_for_access_check(request, True)

    # If returns error response, invalid header or token
    if isinstance(user_info, Response):
        return authentication_required

    # Otherwise, user_info is a dict and we check if the group ID of target endpoint can be found in user_info['hmgroupids'] list
    # Key 'hmgroupids' presents only when group_required is True
    hubmap_read_group = '5777527e-ec11-11e8-ab41-0af86edb4424'
    for group in user_info['hmgroupids']:
        if group == hubmap_read_group:
            # Further check if the dataset contains gene sequence information
            # sending get request and saving the response as response object 
            response = requests.get(url = "http://hubmap-auth:3333/entities/" + dataset_uuid, headers={"AUTHORIZATION": request.headers.get("AUTHORIZATION")}) 
            if response.status_code == 200:
                metadata = response.json()
                pprint(metadata)
                # No access to datasets that contain gene sequence
                if 'phi' in metadata and metadata['phi'] == "yes":
                    return authorization_required
                else:
                    return allowed        

            return authentication_required

    # None of the assigned groups match the group ID
    return authentication_required


# Chceck if access to the given endpoint item is allowed
# Also check if the globus token associated user is a member of the specified group assocaited with the endpoint item
def api_access_allowed(item, request):
    pprint("===========Matched endpoint=============")
    pprint(item)

    # Check if auth is required for this endpoint
    if item['auth'] == False:
        return True
    
    # When auth is required, we need to check if group access is also required
    group_required = True if 'groups' in item else False

    # Get user info and do further parsing
    user_info = get_user_info_for_access_check(request, group_required)

    # If returns error response, invalid header or token
    if isinstance(user_info, Response):
        return False

    # Otherwise, user_info is a dict and we check if the group ID of target endpoint can be found in user_info['hmgroupids'] list
    # Key 'hmgroupids' presents only when group_required is True
    if group_required:
        for group in user_info['hmgroupids']:
            if group in item['groups']:
                return True

        # None of the assigned groups match the group ID specified in item['groups']
        return False

    # When no group access requried and user_info dict gets returned
    return True


####################################################################################################
## User UI Auth, with UI rendering and redirection
####################################################################################################

# User auth with UI rendering
# All endpoints access need to be authenticated
# Direct access will see the login form
# Nginx auth_request module won't be able to display the login form for 401 response
@app.route('/user_auth', methods = ['GET'])
def user_auth():
    # Nginx auth_request only cares about the response status code
    # it ignores the response body
    # We use body here only for direct visit to this endpoint
    response_200 = make_response('OK', 200)
    response_401 = make_response('Unauthorized', 401)

    # use cookies.get(key) instead of cookies[key] to not get a
    # KeyError if the cookie is missing.
    # Cookie value is string not boolean
    is_authenticated = request.cookies.get('is_authenticated')

    if is_authenticated is not None:
        if is_authenticated == 'True':
            return response_200
        else:
            return response_401
    else:
        return response_401


@app.route('/login_form', methods = ['GET'])
def login_form():
    resp = make_response(render_template('login.html'))

    # Parsing query string
    args = request.args
    if "original_uri" in args:
            original_uri = request.args.get("original_uri")
            resp = make_response(render_template('login.html'))
            # Store in cookie for later redirect
            resp.set_cookie('original_uri', original_uri, domain = app.config['COOKIE_DOMAIN'])
            
            return resp
    else:
        # Just show the login page, won't be able to redirec to the orginal uri
        return resp

# Redirect users from react app login page to Globus auth login widget then redirect back
@app.route('/login', methods = ['GET'])
def login():
    redirect_uri = url_for('login', _external=True)
    confidential_app_auth_client = ConfidentialAppAuthClient(app.config['GLOBUS_APP_ID'], app.config['GLOBUS_APP_SECRET'])
    confidential_app_auth_client.oauth2_start_flow(redirect_uri)

    # If there's no "code" query string parameter, we're in this route
    # starting a Globus Auth login flow.
    # Redirect out to Globus Auth
    if 'code' not in request.args:                                        
        auth_uri = confidential_app_auth_client.oauth2_get_authorize_url(additional_params={"scope": "openid profile email urn:globus:auth:scope:transfer.api.globus.org:all urn:globus:auth:scope:auth.globus.org:view_identities urn:globus:auth:scope:nexus.api.globus.org:groups" })
        return redirect(auth_uri)
    # If we do have a "code" param, we're coming back from Globus Auth
    # and can start the process of exchanging an auth code for a token.
    else:
        auth_code = request.args.get('code')

        token_response = confidential_app_auth_client.oauth2_exchange_code_for_tokens(auth_code)
        
        # Get all Bearer tokens
        auth_token = token_response.by_resource_server['auth.globus.org']['access_token']
        nexus_token = token_response.by_resource_server['nexus.api.globus.org']['access_token']
        transfer_token = token_response.by_resource_server['transfer.api.globus.org']['access_token']

        # Also get the user info (sub, email, name, preferred_username) using the AuthClient with the auth token
        user_info = get_globus_user_info(auth_token)

        # Response
        original_uri = request.cookies.get('original_uri')

        if original_uri is not None:
            resp = make_response(redirect(original_uri))
        else:
            # If no original_uri found in cookie, won't be able to redirect
            resp = make_response('You are authenticated :)', 200)

        # Convert boolean to string ans store in cookie
        resp.set_cookie('is_authenticated', str(True), domain = app.config['COOKIE_DOMAIN'])
        resp.set_cookie('globus_user_id', user_info['sub'], domain = app.config['COOKIE_DOMAIN'])
        resp.set_cookie('name', user_info['name'], domain = app.config['COOKIE_DOMAIN'])
        resp.set_cookie('email', user_info['email'].lower(), domain = app.config['COOKIE_DOMAIN'])
        resp.set_cookie('auth_token', auth_token, domain = app.config['COOKIE_DOMAIN'])
        resp.set_cookie('nexus_token', nexus_token, domain = app.config['COOKIE_DOMAIN'])
        resp.set_cookie('transfer_token', transfer_token, domain = app.config['COOKIE_DOMAIN'])

        # No logner need the orginal uri at this point
        resp.set_cookie('original_uri', expires=0, domain = app.config['COOKIE_DOMAIN'])
        
        return resp 


# Revoke the tokens with Globus Auth
# Expire all cookie data
# Redirect the user to the Globus Auth logout page
@app.route('/logout', methods = ['GET'])
def logout():
    confidential_app_auth_client = ConfidentialAppAuthClient(app.config['GLOBUS_APP_ID'], app.config['GLOBUS_APP_SECRET'])

    auth_token = request.cookies.get('auth_token')
    nexus_token = request.cookies.get('nexus_token')
    transfer_token = request.cookies.get('transfer_token')

    # Revoke the tokens with Globus Auth
    confidential_app_auth_client.oauth2_revoke_token(auth_token)
    confidential_app_auth_client.oauth2_revoke_token(nexus_token)
    confidential_app_auth_client.oauth2_revoke_token(transfer_token)

    # Expire those values in cookie
    resp = make_response("Bye~", 200)
    resp.set_cookie('is_authenticated', expires=0, domain = app.config['COOKIE_DOMAIN'])
    resp.set_cookie('globus_user_id', expires=0, domain = app.config['COOKIE_DOMAIN'])
    resp.set_cookie('name', expires=0, domain = app.config['COOKIE_DOMAIN'])
    resp.set_cookie('email', expires=0, domain = app.config['COOKIE_DOMAIN'])
    resp.set_cookie('auth_token', expires=0, domain = app.config['COOKIE_DOMAIN'])
    resp.set_cookie('nexus_token', expires=0, domain = app.config['COOKIE_DOMAIN'])
    resp.set_cookie('transfer_token', expires=0, domain = app.config['COOKIE_DOMAIN'])

    return resp


####################################################################################################
## Internal Functions Used By user UI Auth
####################################################################################################

# Get user info from globus with the auth access token
def get_globus_user_info(token):
    auth_client = AuthClient(authorizer=AccessTokenAuthorizer(token))
    return auth_client.oauth2_userinfo()


