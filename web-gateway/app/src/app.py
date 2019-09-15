from flask import Flask, request, jsonify, make_response, render_template, session, redirect, url_for
from globus_sdk import AuthClient, AccessTokenAuthorizer, ConfidentialAppAuthClient
import requests
import json
from cachetools import cached, TTLCache
import functools

# For debugging
from pprint import pprint


# Init app and use the config from instance folder
app = Flask(__name__, instance_relative_config=True)
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

@app.route('/')
def home():
    return "This is HuBMAP Web Gateway :)"


####################################################################################################
## API Auth, no UI
####################################################################################################

@app.route('/cache_clear')
def cache_clear():
    cache.clear()
    return "All function cache cleared."


# Auth for private API services
# All endpoints access need to be authenticated
# Direct access will see the JSON message
# Nginx auth_request module won't be able to display the JSON message for 401 response
@app.route('/api_auth')
def api_auth():
    # Debugging
    pprint(request.headers)

    # Nginx auth_request only cares about the response status code
    # it ignores the response body
    # We use body here only for direct visit to this endpoint
    response_200 = make_response(jsonify({"message": "OK: Authorized"}), 200)
    response_401 = make_response(jsonify({"message": "ERROR: Unauthorized"}), 401)
    response_403 = make_response(jsonify({"message": "ERROR: Forbidden"}), 403)

    # Load endpoints from json
    data = load_endpoints()

    public_endpoints = data['public']
    private_endpoints = data['private']

    # Next, validate the nexus_token for group access
    original_uri = None
    if ("X-Original-Request-Method" in request.headers) and ("X-Forwarded-Proto" in request.headers) and ("Host" in request.headers) and ("X-Original-URI" in request.headers):
        method = request.headers.get("X-Original-Request-Method")
        scheme = request.headers.get("X-Forwarded-Proto")
        host = request.headers.get("Host")
        request_uri = request.headers.get("X-Original-URI")

        # This is the full uri
        original_uri = scheme + '://' + host + request_uri

    if original_uri is not None:
        # Check if this URI is one of the public endpoints
        endpoint = method.upper() + ' ' + original_uri
        # Return 200 for all public endpoints
        # Check the Mauthorization header for private endpoints
        # Return 200 for endpoints that are not listed in neither public or private lookup
        if endpoint in public_endpoints:
            return response_200
        else:
            # First we create a list of private endpoints
            private_endpoints_list = list()
            for entry in private_endpoints:
                private_endpoints_list.append(entry['endpoint'])

            # Require Mauthorization header for private endpoints
            if endpoint in private_endpoints_list:
                # Parsing the Mauthorization token
                if ("MAuthorization" in request.headers) and request.headers.get("MAuthorization").upper().startswith("MBEARER"):
                    mauth = request.headers.get("MAuthorization")[7:].strip()
                    mauth_json = json.loads(mauth)
                    # Only need auth token at this point
                    # Will need nexus token later for group access check
                    auth_token = mauth_json['auth_token']

                    # Validate the Globus auth token provided from request
                    # Do this before validating the nexus group token
                    if is_active_auth_token(auth_token):
                        # Now further check the group access with nexus token
                        if 'nexus_token' in mauth_json:
                            # Get group info
                            group_response = get_group_info(mauth_json['nexus_token'])
  
                            # If returns group info, this nexus token is valid
                            if group_response.status_code == 200:
                                # Further check the access based on globus group ID
                                group_info = group_response.json()
                                # Create a list of group IDs
                                assigned_groups = list()
                                for group in group_info:
                                    assigned_groups.append(group['id'])

                                # Now we check if the group ID of target endpoint can be found in this assigned_groups IDs list
                                target_group = get_private_endpoint_group(endpoint)   
                                if target_group in assigned_groups:
                                    return response_200
                                else:
                                    # Authenticated but not authorized
                                    return response_403
                            else:
                                # Authenticated but not authorized
                                return response_403
                        else:
                            # In case missing nexus token
                            return response_401
                    else:
                        # Not authenticated at all
                        return response_401
                else:
                	# No MAuthorization header or couldn't parse
                	return response_401
            # It's possible the comming URI doesn't belong to either public or private
            # Idealy, we should return 404. But auth_request will send back a 500 for any codes
            # other than 200, 401/403
            return response_401
    else:
        # In case the original_uri is missing
        return response_401


####################################################################################################
## User Auth, with UI rendering and redirection
####################################################################################################

# User auth with UI rendering
# All endpoints access need to be authenticated
# Direct access will see the login form
# Nginx auth_request module won't be able to display the login form for 401 response
@app.route('/user_auth')
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


@app.route('/login_form')
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
@app.route('/login')
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
@app.route('/logout')
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
## Internal Functions
####################################################################################################

# Get user info from globus with the auth access token
def get_globus_user_info(token):
    auth_client = AuthClient(authorizer=AccessTokenAuthorizer(token))
    return auth_client.oauth2_userinfo()

# Fetch the globus group infor for a given nexus token via Globus REST API
def get_group_info(nexus_token):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + nexus_token
    }
    globus_geoup_api_url = 'https://nexus.api.globusonline.org/groups?fields=id,name,description,group_type,has_subgroups,identity_set_properties&for_all_identities=false&include_identaaaaay_set_properties=false&my_statuses=active'
    response = requests.get(globus_geoup_api_url, headers = headers)
    return response


# Validate the Globus auth token provided from request
# Do this before validating the nexus group token
# The resulting response has the form {"active": True} when the token is valid, and {"active": False} when it is not.
def is_active_auth_token(auth_token): 
    confidential_app_auth_client = ConfidentialAppAuthClient(app.config['GLOBUS_APP_ID'], app.config['GLOBUS_APP_SECRET'])
    result = confidential_app_auth_client.oauth2_validate_token(auth_token)
    return result['active']

# Load all endpoints from json file and cache the data
@cached(cache)
def load_endpoints():
    with open("endpoints.json", "r") as file:
        data = json.load(file)
        return data

@cached(cache)
def get_private_endpoint_group(target_endpoint):
    data = load_endpoints()
    private_endpoints = data['private']

    entry = next(item for item in private_endpoints if item['endpoint'] == target_endpoint)
    return entry['group']