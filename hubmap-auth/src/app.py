from flask import Flask, request, jsonify, make_response, Response
import requests
import json
import logging
from cachetools import cached, TTLCache
import functools
import re
import os
from urllib.parse import urlparse, parse_qs

# HuBMAP commons
from hubmap_commons.hm_auth import AuthHelper
from hubmap_commons.hubmap_const import HubmapConst
from hubmap_commons.exceptions import HTTPException

# Specify the absolute path of the instance folder and use the config file relative to the instance path
app = Flask(__name__, instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance'), instance_relative_config=True)
app.config.from_pyfile('app.cfg')

# Remove trailing slash / from URL base to avoid "//" caused by config with trailing slash
app.config['ENTITY_ACCESS_LEVEL_URL'] = app.config['ENTITY_ACCESS_LEVEL_URL'].strip('/')

# Also remove trailing slash / for those status endpoints in case Flask takes / as a different endpoint
app.config['UUID_API_STATUS_URL'] = app.config['UUID_API_STATUS_URL'].strip('/')
app.config['ENTITY_API_STATUS_URL'] = app.config['ENTITY_API_STATUS_URL'].strip('/')
app.config['INGEST_API_STATUS_URL'] = app.config['INGEST_API_STATUS_URL'].strip('/')
app.config['SEARCH_API_STATUS_URL'] = app.config['SEARCH_API_STATUS_URL'].strip('/')

# Set logging level (default is warning)
logging.basicConfig(level=logging.DEBUG)

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
## Status of API services and File service
####################################################################################################

@app.route('/status', methods = ['GET'])
def status():
    # All API services have api_auth status (meaning the gateway's API auth is working)
    # Add additional API-specific status to the dict when API auth check passes
    status_data = {
        'uuid_api': {
            'api_auth': False
        },
        'entity_api': {
            'api_auth': False
        },
        'ingest_api': {
            'api_auth': False
        },
        'search_api': {
            'api_auth': False
        }
    }

    # Use modified version of globus app secrect from configuration as the internal token
    # All API endpoints specified in gateway regardless of auth is required or not, 
    # will consider this internal token as valid and has the access to HuBMAP-Read group
    auth_helper = init_auth_helper()
    request_headers = create_request_headers_for_auth(auth_helper.getProcessSecret())

    # uuid-api
    uuid_api_response = status_request(app.config['UUID_API_STATUS_URL'], request_headers)
    if uuid_api_response.status_code == 200:
        # Overwrite the default value
        status_data['uuid_api']['api_auth'] = True

        # Then parse the response json to determine if neo4j connection is working
        response_json = uuid_api_response.json()
        if 'mysql_connection' in response_json:
            # Add the mysql connection status
            status_data['uuid_api']['mysql_connection'] = response_json['mysql_connection']

    # entity-api
    entity_api_response = status_request(app.config['ENTITY_API_STATUS_URL'], request_headers)
    if entity_api_response.status_code == 200:
        # Overwrite the default value
        status_data['entity_api']['api_auth'] = True

        # Then parse the response json to determine if neo4j connection is working
        response_json = entity_api_response.json()
        if 'neo4j_connection' in response_json:
            # Add the neo4j connection status
            status_data['entity_api']['neo4j_connection'] = response_json['neo4j_connection']

    # ingest-api
    ingest_api_response = status_request(app.config['INGEST_API_STATUS_URL'], request_headers)
    if ingest_api_response.status_code == 200:
        # Overwrite the default value
        status_data['ingest_api']['api_auth'] = True

        # Then parse the response json to determine if neo4j connection is working
        response_json = ingest_api_response.json()
        if 'neo4j_connection' in response_json:
            # Add the neo4j connection status
            status_data['ingest_api']['neo4j_connection'] = response_json['neo4j_connection']

    # search-api
    search_api_response = status_request(app.config['SEARCH_API_STATUS_URL'], request_headers)
    if search_api_response.status_code == 200:
        # Overwrite the default value
        status_data['search_api']['api_auth'] = True

        # Then parse the response json to determine if elasticsearch cluster is connected
        response_json = search_api_response.json()
        if 'elasticsearch_connection' in response_json:
            # Add the elasticsearch connection status
            status_data['search_api']['elasticsearch_connection'] = response_json['elasticsearch_connection']
        
        # Also check if the health status of elasticsearch cluster is available
        if 'elasticsearch_status' in response_json:
            # Add the elasticsearch cluster health status
            status_data['search_api']['elasticsearch_status'] = response_json['elasticsearch_status']

    # Final result
    return jsonify(status_data)


####################################################################################################
## API Auth
####################################################################################################

@app.route('/cache_clear', methods = ['GET'])
def cache_clear():
    cache.clear()
    app.logger.info("All gatewat API Auth function cache cleared.")
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

    app.logger.info("======api_auth request.headers======")
    app.logger.info(request.headers)

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


####################################################################################################
## File Auth
####################################################################################################

# Auth for file service
# URL pattern: https://assets.dev.hubmapconsortium.org/<dataset-uuid>/<relative-file-path>[?token=<globus-token>]
# The query string with token is optional, but will be used by the portal-ui
@app.route('/file_auth', methods = ['GET'])
def file_auth():
    app.logger.info("======file_auth Orginal request.headers======")
    app.logger.info(request.headers)

    # Nginx auth_request only cares about the response status code
    # it ignores the response body
    # We use body here only for direct visit to this endpoint
    response_200 = make_response(jsonify({"message": "OK: Authorized"}), 200)
    response_401 = make_response(jsonify({"message": "ERROR: Unauthorized"}), 401)
    response_403 = make_response(jsonify({"message": "ERROR: Forbidden"}), 403)
    response_500 = make_response(jsonify({"message": "ERROR: Internal Server Error"}), 500)
  
    method = None
    orig_uri = None

    # URI = scheme:[//authority]path[?query][#fragment] where authority = [userinfo@]host[:port]
    # This "Host" header is nginx `$http_host` which contains port number, unlike `$host` which doesn't include port number
    # Here we don't parse the "X-Forwarded-Proto" header because the scheme is either HTTP or HTTPS
    if ("X-Original-Request-Method" in request.headers) and ("X-Original-URI" in request.headers):
        method = request.headers.get("X-Original-Request-Method")
        orig_uri = request.headers.get("X-Original-URI")

    # File access only via http GET
    if method is not None:
        if method.upper() == 'GET':
            if orig_uri is not None:
                parsed_uri = urlparse(orig_uri)
                
                app.logger.debug("======parsed_uri======")
                app.logger.debug(parsed_uri)

                # Parse the path to get the dataset UUID
                # Remove the leading slash before split
                path_list = parsed_uri.path.strip("/").split("/")
                dataset_uuid = path_list[0]

                # Also get the "token" parameter from query string
                # query is a dict, keys are the unique query variable names and the values are lists of values for each name
                token_from_query = None
                query = parse_qs(parsed_uri.query)

                if "token" in query:
                    token_from_query = query["token"][0]
                
                app.logger.debug("======token_from_query======")
                app.logger.debug(token_from_query)

                # Check if the globus token is valid for accessing this secured dataset
                code = get_file_access(dataset_uuid, token_from_query, request)

                app.logger.debug("======get_file_access() result code======")
                app.logger.debug(code)

                if code == 200:
                    return response_200
                elif code == 401:
                    return response_401
                elif code == 403:
                    return response_403
                elif code == 500:
                    return response_500
            else: 
                # Missing dataset UUID in path
                return response_401
        else:
            # Wrong http method
            return response_401
    # Not a valid http request
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

# Make a call to the given target URL with the given headers
def status_request(target_url, request_headers):
    response = requests.get(url = target_url, headers = request_headers) 
    return response

# Get user infomation dict based on the http request(headers)
# `group_required` is a boolean, when True, 'hmgroupids' is in the output
def get_user_info_for_access_check(request, group_required):
    auth_helper = init_auth_helper()
    return auth_helper.getUserInfoUsingRequest(request, group_required)

# Due to Flask's EnvironHeaders is immutable
# We create a new class with the headers property 
# so AuthHelper can access it using the dot notation req.headers
class CustomRequest:
    # Constructor
    def __init__(self, headers):
        self.headers = headers

# Create a dict with HTTP Authorization header with Bearer token
def create_request_headers_for_auth(token):
    auth_header_name = 'Authorization'
    auth_scheme = 'Bearer'

    headers_dict = {
        # Don't forget the space between scheme and the token value
        auth_header_name: auth_scheme + ' ' + token
    }

    return headers_dict

# Check if a given dataset is accessible based on token and access level assigned to the dataset
def get_file_access(dataset_uuid, token_from_query, request):
    # Returns one of the following codes
    allowed = 200
    authentication_required = 401
    authorization_required = 403
    internal_error = 500

    # Will need this to call getProcessSecret() and getUserDataAccessLevel()
    auth_helper = init_auth_helper()

    # request.headers may or may not contain the 'Authorization' header
    final_request = request

    # First check the dataset access level based on the uuid without taking the token into consideration
    entity_api_full_url = app.config['ENTITY_ACCESS_LEVEL_URL'] + '/' + dataset_uuid
    # Use modified version of globus app secrect from configuration as the internal token
    # All API endpoints specified in gateway regardless of auth is required or not, 
    # will consider this internal token as valid and has the access to HuBMAP-Read group
    request_headers = create_request_headers_for_auth(auth_helper.getProcessSecret())

    # Possible response status codes: 200, 401, and 500 to be handled below
    response = requests.get(url = entity_api_full_url, headers = request_headers) 

    # Using the globus app secret as internal token should always return 200 supposely
    # If not, either technical issue 500 or something wrong with this internal token 401 (even if the user doesn't provide a token, since we use the internal secret as token)
    if response.status_code == 200:
        # The call to entity-api returns string directly
        data_access_level = response.text

        app.logger.debug("======data_access_level returned by entity-api for given dataset uuid======")
        app.logger.debug(data_access_level)

        # Throw error 500 if invalid access level value assigned to the dataset metadata node
        if data_access_level != HubmapConst.ACCESS_LEVEL_PUBLIC and data_access_level != HubmapConst.ACCESS_LEVEL_CONSORTIUM and data_access_level != HubmapConst.ACCESS_LEVEL_PROTECTED:
            app.logger.error("The 'data_access_level' value assigned for this dataset " + dataset_uuid + " is invalid")
            return internal_error

        # Get the user access level based on token (optional) from HTTP header or query string
        # The globus token can be specified in the 'Authorization' header OR through a "token" query string in the URL
        # Use the globus token from URL query string if present and set as the value of 'Authorization' header
        # If not found, default to the 'Authorization' header
        # Because auth_helper.getUserDataAccessLevel() checks against the 'Authorization' or 'Mauthorization' header
        if token_from_query is not None:
            # NOTE: request.headers is type 'EnvironHeaders', 
            # and it's immutable(read only version of the headers from a WSGI environment)
            # So we can't modify the request.headers
            # Instead, we use a custom request object and set as the 'Authorization' header 
            app.logger.debug("======set Authorization header with query string token value======")

            custom_headers_dict = create_request_headers_for_auth(token_from_query)

            # Overwrite the default final_request
            # CustomRequest and Flask's request are different types, but the Commons's AuthHelper only access the request.headers
            # So as long as headers from CustomRequest instance can be accessed with the dot notation
            final_request = CustomRequest(custom_headers_dict)

        # By now, request.headers may or may not contain the 'Authorization' header
        app.logger.debug("======file_auth final_request.headers======")
        app.logger.debug(final_request.headers)

        # When Authorization is not present, return value is based on the data_access_level of the given dataset
        # In this case we can't call auth_helper.getUserDataAccessLevel() because it returns HTTPException when Authorization header is missing
        if 'Authorization' not in final_request.headers:
            # Return 401 if the data access level is consortium or protected since they's require token but Authorization header missing
            if data_access_level != HubmapConst.ACCESS_LEVEL_PUBLIC:
                return authentication_required
            # Only return 200 since public dataset doesn't require token
            return allowed

        # By now the Authorization is present and it's either provided directly from the request headers or query string (overwriting)
        # Then we can call auth_helper.getUserDataAccessLevel() to find out the user's assigned access level
        try:
            # The user_info contains HIGHEST access level of the user based on the token
            # Default to HubmapConst.ACCESS_LEVEL_PUBLIC if none of the Authorization/Mauthorization header presents
            # This call raises an HTTPException with a 401 if any auth issues are found
            user_info = auth_helper.getUserDataAccessLevel(final_request)

            app.logger.info("======user_info======")
            app.logger.info(user_info)
        # If returns HTTPException with a 401, invalid header format or expired/invalid token
        except HTTPException as e:
            msg = "HTTPException from calling auth_helper.getUserDataAccessLevel() HTTP code: " + str(e.get_status_code()) + " " + e.get_description() 

            app.logger.warning(msg)

            # In the case of requested dataset is public but provided globus token is invalid/expired,
            # we'll return 401 so the end user knows something wrong with the token rather than allowing file access
            return authentication_required

        # By now the user_info is returned and based on the logic of auth_helper.getUserDataAccessLevel(), 
        # 'data_access_level' should always be found user_info and its value is always one of the 
        # HubmapConst.ACCESS_LEVEL_PUBLIC, HubmapConst.ACCESS_LEVEL_CONSORTIUM, or HubmapConst.ACCESS_LEVEL_PROTECTED
        # So no need to check unknown value
        user_access_level = user_info['data_access_level']

        # By now we have both data_access_level and the user_access_level obtained with one of the valid values
        # Allow file access as long as data_access_level is public, no need to care about the user_access_level (since Authorization header presents with valid token)
        if data_access_level == HubmapConst.ACCESS_LEVEL_PUBLIC:
            return allowed
        
        # When data_access_level is comsortium, allow access only when the user_access_level (remember this is the highest level) is consortium or protected
        if (data_access_level == HubmapConst.ACCESS_LEVEL_CONSORTIUM and
            (user_access_level == HubmapConst.ACCESS_LEVEL_PROTECTED or user_access_level == HubmapConst.ACCESS_LEVEL_CONSORTIUM)):
            return allowed
        
        # When data_access_level is protected, allow access only when user_access_level is also protected
        if data_access_level == HubmapConst.ACCESS_LEVEL_PROTECTED and user_access_level == HubmapConst.ACCESS_LEVEL_PROTECTED:
            return allowed
            
        # All other cases
        return authorization_required
    # Something wrong with fullfilling the request with secret as token
    # E.g., for some reason the gateway returns 401
    elif response.status_code == 401:    
        app.logger.error("Couldn't authenticate the request made to " + entity_api_full_url + " with internal token (modified globus app secrect)")
        return authorization_required
    # All other cases with 500 response
    # E.g., entity-api server down?
    else:  
        app.logger.error("The server encountered an unexpected condition that prevented it from getting the access level of this dataset " + dataset_uuid)
        return internal_error

# Always pass through the requests with using modified version of the globus app secret as internal token
def is_secrect_token(request):
    auth_helper = init_auth_helper()
    internal_token = auth_helper.getProcessSecret()
    parsed_token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        parsed_token = auth_header[6:].strip()

    if internal_token == parsed_token:
        return True

    return False

# Chceck if access to the given endpoint item is allowed
# Also check if the globus token associated user is a member of the specified group assocaited with the endpoint item
def api_access_allowed(item, request):
    app.logger.info("======Matched endpoint======")
    app.logger.info(item)

    # Check if auth is required for this endpoint
    if item['auth'] == False:
        return True

    # Check if using modified version of the globus app secret as internal token
    if is_secrect_token(request):
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

