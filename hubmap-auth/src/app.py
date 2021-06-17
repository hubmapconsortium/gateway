from flask import Flask, request, jsonify, make_response, Response, render_template
import requests
import requests_cache
# Don't confuse urllib (Python native library) with urllib3 (3rd-party library, requests also uses urllib3)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import logging
from cachetools import cached, TTLCache
import functools
import re
import os
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# HuBMAP commons
from hubmap_commons.hm_auth import AuthHelper
from hubmap_commons.exceptions import HTTPException


# Set logging fromat and level (default is warning)
# All the API logging is forwarded to the uWSGI server and gets written into the log file `uwsgo-entity-api.log`
# Log rotation is handled via logrotate on the host system with a configuration file
# Do NOT handle log file and rotation via the Python logging to avoid issues with multi-worker processes
logging.basicConfig(format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Specify the absolute path of the instance folder and use the config file relative to the instance path
app = Flask(__name__, instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance'), instance_relative_config=True)
app.config.from_pyfile('app.cfg')

# Remove trailing slash / from URL base to avoid "//" caused by config with trailing slash
app.config['ENTITY_API_URL'] = app.config['ENTITY_API_URL'].strip('/')

# Also remove trailing slash / for those status endpoints in case Flask takes / as a different endpoint
app.config['UUID_API_STATUS_URL'] = app.config['UUID_API_STATUS_URL'].strip('/')
app.config['ENTITY_API_STATUS_URL'] = app.config['ENTITY_API_STATUS_URL'].strip('/')
app.config['INGEST_API_STATUS_URL'] = app.config['INGEST_API_STATUS_URL'].strip('/')
app.config['SEARCH_API_STATUS_URL'] = app.config['SEARCH_API_STATUS_URL'].strip('/')
app.config['FILE_ASSETS_STATUS_URL'] = app.config['FILE_ASSETS_STATUS_URL'].strip('/')

# LRU Cache implementation with per-item time-to-live (TTL) value
# with a memoizing callable that saves up to maxsize results based on a Least Frequently Used (LFU) algorithm
# with a per-item time-to-live (TTL) value
# Here we use two hours, 7200 seconds for ttl
cache = TTLCache(maxsize=app.config['CACHE_MAXSIZE'], ttl=app.config['CACHE_TTL'])

# Requests cache generates the sqlite file
# File path defined in app.config['REQUESTS_CACHE_SQLITE_NAME'] without the .sqlite extension
# Use the same CACHE_TTL from configuration
requests_cache.install_cache(app.config['REQUESTS_CACHE_SQLITE_NAME'], backend='sqlite', expire_after=app.config['CACHE_TTL'])

# Suppress InsecureRequestWarning warning when requesting status on https with ssl cert verify disabled
requests.packages.urllib3.disable_warnings(category = InsecureRequestWarning)

####################################################################################################
## AuthHelper initialization
####################################################################################################

# Initialize AuthHelper class and ensure singleton
try:
    if AuthHelper.isInitialized() == False:
        auth_helper_instance = AuthHelper.create(app.config['GLOBUS_APP_ID'], 
                                                 app.config['GLOBUS_APP_SECRET'])

        logger.info("Initialized AuthHelper class successfully :)")
    else:
        auth_helper_instance = AuthHelper.instance()
except Exception:
    msg = "Failed to initialize the AuthHelper class"
    # Log the full stack trace, prepend a line with our message
    logger.exception(msg)


####################################################################################################
## Default route
####################################################################################################

@app.route('/', methods = ['GET'])
def home():
    return "This is HuBMAP Web Gateway :)"

####################################################################################################
## Status of API services and File service
####################################################################################################

# JSON version of status
@app.route('/status.json', methods = ['GET'])
def status_json():
    return jsonify(get_status_data())

# HTML rendering of the status
@app.route('/status.html', methods = ['GET'])
def status_html():
    resp = make_response(render_template('status.html', data = get_status_data()))
    return resp

####################################################################################################
## API Auth
####################################################################################################

@app.route('/cache_clear', methods = ['GET'])
def cache_clear():
    cache.clear()
    logger.info("All gatewat API Auth function cache cleared.")
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

    logger.info("======api_auth request.headers======")
    logger.info(request.headers)

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

# Auth for assets file service
# URL pattern: https://assets.dev.hubmapconsortium.org/<uuid>/<relative-file-path>[?token=<globus-token>]
# The <uuid> could either be a real dataset uuid or 
# a thumbnail.jpg image file uuid associated with the target dataset
# The query string with token is optional, but will be used by the portal-ui
@app.route('/file_auth', methods = ['GET'])
def file_auth():
    logger.info("======file_auth Orginal request.headers======")
    logger.info(request.headers)

    # Nginx auth_request only cares about the response status code
    # it ignores the response body
    # We use body here only for description purposes and direct visit to this endpoint
    response_200 = make_response(jsonify({"message": "OK: Authorized"}), 200)
    response_401 = make_response(jsonify({"message": "ERROR: Unauthorized"}), 401)
    response_403 = make_response(jsonify({"message": "ERROR: Forbidden"}), 403)
    response_500 = make_response(jsonify({"message": "ERROR: Internal Server Error"}), 500)

    # Note: 404 is not supported http://nginx.org/en/docs/http/ngx_http_auth_request_module.html
    # Any response code other than 200/401/403 returned by the subrequest is considered an error 500
    # The end user or client will never see 404 but 500
    response_404 = make_response(jsonify({"message": "ERROR: Not Found"}), 404)
  
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
        # Supports both GET and HEAD request methods
        if method.upper() in ['GET', 'HEAD']:
            if orig_uri is not None:
                parsed_uri = urlparse(orig_uri)
                
                logger.debug("======parsed_uri======")
                logger.debug(parsed_uri)

                # Remove the leading slash before split
                path_list = parsed_uri.path.strip("/").split("/")

                # This parsed uuid couldbe either be the dataset uuid 
                # or thumbnail.jpg image file uuid associated with the target dataset
                uuid = path_list[0]

                # Also get the "token" parameter from query string
                # query is a dict, keys are the unique query variable names and the values are lists of values for each name
                token_from_query = None
                query = parse_qs(parsed_uri.query)

                if "token" in query:
                    token_from_query = query["token"][0]
                
                logger.debug("======token_from_query======")
                logger.debug(token_from_query)

                # Check if the globus token is valid for accessing this secured dataset
                code = get_file_access(uuid, token_from_query, request)

                logger.debug("======get_file_access() resulting code======")
                logger.debug(code)

                if code == 200:
                    return response_200
                elif code == 401:
                    return response_401
                elif code == 403:
                    return response_403
                # Returned 404 will be considered as 500 by nginx auth_request module
                elif code == 404:
                    logger.warning("The end user or client will never see 404 but 500")
                    return response_404
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

# Make a call to the given target status URL
def status_request(target_url):
    # Verify if requests used the cached response from the SQLite database
    now = time.ctime(int(time.time()))

    # Disable ssl certificate verification
    response = requests.get(url = target_url, verify = False) 

    logger.debug(f"Time: {now} / GET request URL: {target_url} / Used requests cache: {response.from_cache}")

    return response

# Dict of API status data
def get_status_data():
    # Some constants
    GATEWAY = 'gateway'
    VERSION = 'version'
    BUILD = 'build'
    UUID_API = 'uuid_api'
    ENTITY_API = 'entity_api'
    INGEST_API = 'ingest_api'
    SEARCH_API = 'search_api'
    FILE_ASSETS = 'file_assets'
    API_AUTH = 'api_auth'
    MYSQL_CONNECTION = 'mysql_connection'
    NEO4J_CONNECTION = 'neo4j_connection'
    ELASTICSEARCH_CONNECTION = 'elasticsearch_connection'
    ELASTICSEARCH_STATUS = 'elasticsearch_status'
    FILE_ASSETS_STATUS = 'file_assets_status'

    # All API services have api_auth status (meaning the gateway's API auth is working)
    # We won't get other status if api_auth fails
    # Add additional API-specific status to the dict when API auth check passes
    # Gateway version and build are parsed from VERSION and BUILD files directly
    # instead of making API calls. So they alwasy present
    status_data = {
        GATEWAY: {
            # Use strip() to remove leading and trailing spaces, newlines, and tabs
            VERSION: (Path(__file__).absolute().parent.parent / 'VERSION').read_text().strip(),
            BUILD: (Path(__file__).absolute().parent.parent / 'BUILD').read_text().strip()
        },
        UUID_API: {
            API_AUTH: False
        },
        ENTITY_API: {
            API_AUTH: False
        },
        INGEST_API: {
            API_AUTH: False
        },
        SEARCH_API: {
            API_AUTH: False
        },
        FILE_ASSETS: {
            API_AUTH: False
        }
    }

    # uuid-api
    uuid_api_response = status_request(app.config['UUID_API_STATUS_URL'])
    if uuid_api_response.status_code == 200:
        # Overwrite the default value
        status_data[UUID_API][API_AUTH] = True

        # Then parse the response json to determine if neo4j connection is working
        response_json = uuid_api_response.json()
        if VERSION in response_json:
            # Set version
            status_data[UUID_API][VERSION] = response_json[VERSION]

        if BUILD in response_json:
            # Set build
            status_data[UUID_API][BUILD] = response_json[BUILD]

        if MYSQL_CONNECTION in response_json:
            # Add the mysql connection status
            status_data[UUID_API][MYSQL_CONNECTION] = response_json[MYSQL_CONNECTION]

    # entity-api
    entity_api_response = status_request(app.config['ENTITY_API_STATUS_URL'])
    if entity_api_response.status_code == 200:
        # Overwrite the default value
        status_data[ENTITY_API][API_AUTH] = True

        # Then parse the response json to determine if neo4j connection is working
        response_json = entity_api_response.json()
        if VERSION in response_json:
            # Set version
            status_data[ENTITY_API][VERSION] = response_json[VERSION]

        if BUILD in response_json:
            # Set build
            status_data[ENTITY_API][BUILD] = response_json[BUILD]

        if NEO4J_CONNECTION in response_json:
            # Add the neo4j connection status
            status_data[ENTITY_API][NEO4J_CONNECTION] = response_json[NEO4J_CONNECTION]

    # ingest-api
    ingest_api_response = status_request(app.config['INGEST_API_STATUS_URL'])
    if ingest_api_response.status_code == 200:
        # Overwrite the default value
        status_data[INGEST_API][API_AUTH] = True

        # Then parse the response json to determine if neo4j connection is working
        response_json = ingest_api_response.json()
        if VERSION in response_json:
            # Set version
            status_data[INGEST_API][VERSION] = response_json[VERSION]

        if BUILD in response_json:
            # Set build
            status_data[INGEST_API][BUILD] = response_json[BUILD]

        if NEO4J_CONNECTION in response_json:
            # Add the neo4j connection status
            status_data[INGEST_API][NEO4J_CONNECTION] = response_json[NEO4J_CONNECTION]

    # search-api
    search_api_response = status_request(app.config['SEARCH_API_STATUS_URL'])
    if search_api_response.status_code == 200:
        # Overwrite the default value
        status_data[SEARCH_API][API_AUTH] = True

        # Then parse the response json to determine if elasticsearch cluster is connected
        response_json = search_api_response.json()
        if VERSION in response_json:
            # Set version
            status_data[SEARCH_API][VERSION] = response_json[VERSION]

        if BUILD in response_json:
            # Set build
            status_data[SEARCH_API][BUILD] = response_json[BUILD]

        if ELASTICSEARCH_CONNECTION in response_json:
            # Add the elasticsearch connection status
            status_data[SEARCH_API][ELASTICSEARCH_CONNECTION] = response_json[ELASTICSEARCH_CONNECTION]
        
        # Also check if the health status of elasticsearch cluster is available
        if ELASTICSEARCH_STATUS in response_json:
            # Add the elasticsearch cluster health status
            status_data[SEARCH_API][ELASTICSEARCH_STATUS] = response_json[ELASTICSEARCH_STATUS]

    # file assets, no need to send headers
    file_assets_response = status_request(app.config['FILE_ASSETS_STATUS_URL'])
    if file_assets_response.status_code == 200:
        # Overwrite the default value
        status_data[FILE_ASSETS][API_AUTH] = True

        # Then parse the response json to determine if neo4j connection is working
        response_json = file_assets_response.json()
        if FILE_ASSETS_STATUS in response_json:
            # Add the file assets status since file is accessible via nginx
            status_data[FILE_ASSETS][FILE_ASSETS_STATUS] = response_json[FILE_ASSETS_STATUS]

    # Final result
    return status_data


# Get user infomation dict based on the http request(headers)
# `group_required` is a boolean, when True, 'hmgroupids' is in the output
def get_user_info_for_access_check(request, group_required):
    return auth_helper_instance.getUserInfoUsingRequest(request, group_required)

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

# Check if the target dataset is accessible based on token 
# and access level assigned to the dataset
# The uuid passed in could either be a real dataset uuid or
# a dataset thumbnail image file uuid associated with the target dataset
def get_file_access(uuid, token_from_query, request):
    # Returns one of the following codes
    allowed = 200
    authentication_required = 401
    authorization_required = 403
    not_found = 404
    internal_error = 500

    # All lowercase for easy comparision
    ACCESS_LEVEL_PUBLIC = 'public'
    ACCESS_LEVEL_CONSORTIUM = 'consortium'
    ACCESS_LEVEL_PROTECTED = 'protected'

    # Special case used by file assets status only
    if uuid == 'status':
        return allowed

    # request.headers may or may not contain the 'Authorization' header
    final_request = request

    # First get the real dataset uuid based on the given uuid
    # If the given uuid is a thumbnail.jpg image file uuid, it'll return
    # the associated dataset uuid. 
    # Otherwise treat the given uuid as a dataset uuid
    try:
        dataset_uuid = get_dataset_uuid_via_file_uuid_retrival(uuid)
    except requests.exceptions.RequestException as e:
        # We'll just hanle 400 and all other cases all together here as 500
        # because nginx auth_request only handles 200/401/403/500
        return internal_error

    # By now, the given uuid is either a real dataset uuid
    # or we have found the dataset uuid of the given file uuid
    # Check the data access level of the target dataset
    entity_api_full_url = app.config['ENTITY_API_URL'] + '/entities/' + dataset_uuid + "?property=data_access_level"
    
    # Use modified version of globus app secrect from configuration as the internal token
    # All API endpoints specified in gateway regardless of auth is required or not, 
    # will consider this internal token as valid and has the access to HuBMAP-Read group
    request_headers = create_request_headers_for_auth(auth_helper_instance.getProcessSecret())

    # Disable ssl certificate verification
    # Possible response status codes: 200, 401, and 500 to be handled below
    response = requests.get(url = entity_api_full_url, headers = request_headers, verify = False) 

    # Verify if requests used the cached response from the SQLite database
    verify_request_cache(entity_api_full_url, response.from_cache)

    # Using the globus app secret as internal token should always return 200 supposely
    # If not, either technical issue 500 or something wrong with this internal token 401 (even if the user doesn't provide a token, since we use the internal secret as token)
    if response.status_code == 200:
        # The call to entity-api returns string directly
        data_access_level = (response.text).lower()

        logger.debug("======data_access_level returned by entity-api for given dataset uuid======")
        logger.debug(data_access_level)

        # Throw error 500 if invalid access level value assigned to the dataset
        if data_access_level not in [ACCESS_LEVEL_PUBLIC, ACCESS_LEVEL_CONSORTIUM, ACCESS_LEVEL_PROTECTED]:
            logger.error("The 'data_access_level' value of this dataset " + dataset_uuid + " is invalid")
            return internal_error

        # Get the user access level based on token (optional) from HTTP header or query string
        # The globus token can be specified in the 'Authorization' header OR through a "token" query string in the URL
        # Use the globus token from URL query string if present and set as the value of 'Authorization' header
        # If not found, default to the 'Authorization' header
        # Because auth_helper_instance.getUserDataAccessLevel() checks against the 'Authorization' or 'Mauthorization' header
        if token_from_query is not None:
            # NOTE: request.headers is type 'EnvironHeaders', 
            # and it's immutable(read only version of the headers from a WSGI environment)
            # So we can't modify the request.headers
            # Instead, we use a custom request object and set as the 'Authorization' header 
            logger.debug("======set Authorization header with query string token value======")

            custom_headers_dict = create_request_headers_for_auth(token_from_query)

            # Overwrite the default final_request
            # CustomRequest and Flask's request are different types, but the Commons's AuthHelper only access the request.headers
            # So as long as headers from CustomRequest instance can be accessed with the dot notation
            final_request = CustomRequest(custom_headers_dict)

        # By now, request.headers may or may not contain the 'Authorization' header
        logger.debug("======file_auth final_request.headers======")
        logger.debug(final_request.headers)

        # When Authorization is not present, return value is based on the data_access_level of the given dataset
        # In this case we can't call auth_helper_instance.getUserDataAccessLevel() because it returns HTTPException when Authorization header is missing
        if 'Authorization' not in final_request.headers:
            # Return 401 if the data access level is consortium or protected since they's require token but Authorization header missing
            if data_access_level != ACCESS_LEVEL_PUBLIC:
                return authentication_required
            # Only return 200 since public dataset doesn't require token
            return allowed

        # By now the Authorization is present and it's either provided directly from the request headers or query string (overwriting)
        # Then we can call auth_helper_instance.getUserDataAccessLevel() to find out the user's assigned access level
        try:
            # The user_info contains HIGHEST access level of the user based on the token
            # Default to ACCESS_LEVEL_PUBLIC if none of the Authorization/Mauthorization header presents
            # This call raises an HTTPException with a 401 if any auth issues are found
            user_info = auth_helper_instance.getUserDataAccessLevel(final_request)

            logger.info("======user_info======")
            logger.info(user_info)
        # If returns HTTPException with a 401, invalid header format or expired/invalid token
        except HTTPException as e:
            msg = "HTTPException from calling auth_helper_instance.getUserDataAccessLevel() HTTP code: " + str(e.get_status_code()) + " " + e.get_description() 

            logger.warning(msg)

            # In the case of requested dataset is public but provided globus token is invalid/expired,
            # we'll return 401 so the end user knows something wrong with the token rather than allowing file access
            return authentication_required

        # By now the user_info is returned and based on the logic of auth_helper_instance.getUserDataAccessLevel(), 
        # 'data_access_level' should always be found user_info and its value is always one of the 
        # ACCESS_LEVEL_PUBLIC, ACCESS_LEVEL_CONSORTIUM, or ACCESS_LEVEL_PROTECTED
        # So no need to check unknown value
        user_access_level = user_info['data_access_level'].lower()

        # By now we have both data_access_level and the user_access_level obtained with one of the valid values
        # Allow file access as long as data_access_level is public, no need to care about the user_access_level (since Authorization header presents with valid token)
        if data_access_level == ACCESS_LEVEL_PUBLIC:
            return allowed
        
        # When data_access_level is comsortium, allow access only when the user_access_level (remember this is the highest level) is consortium or protected
        if (data_access_level == ACCESS_LEVEL_CONSORTIUM and
            (user_access_level == ACCESS_LEVEL_PROTECTED or user_access_level == ACCESS_LEVEL_CONSORTIUM)):
            return allowed
        
        # When data_access_level is protected, allow access only when user_access_level is also protected
        if data_access_level == ACCESS_LEVEL_PROTECTED and user_access_level == ACCESS_LEVEL_PROTECTED:
            return allowed
            
        # All other cases
        return authorization_required
    # Something wrong with fullfilling the request with secret as token
    # E.g., for some reason the gateway returns 401
    elif response.status_code == 401:    
        logger.error("Couldn't authenticate the request made to " + entity_api_full_url + " with internal token (modified globus app secrect)")
        return authorization_required
    elif response.status_code == 404:
        logger.error(f"Dataset with uuid {dataset_uuid} not found")
        return not_found
    # All other cases with 500 response
    else:  
        logger.error("The server encountered an unexpected condition that prevented it from getting the access level of this dataset " + dataset_uuid)
        return internal_error

# Always pass through the requests with using modified version of the globus app secret as internal token
def is_secrect_token(request):
    internal_token = auth_helper_instance.getProcessSecret()
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
    logger.info("======Matched endpoint======")
    logger.info(item)

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

# If the given uuid is a thumbnail.jpg image file uuid
# we'll retrive the associated dataset uuid
# Otherwise if the given uuid itself is a dataset uuid, just return it
def get_dataset_uuid_via_file_uuid_retrival(uuid):
    dataset_uuid = None

    # First determine if the given uuid is the real dataset uuid or thumbnail.jpg file uuid
    uuid_api_full_url = app.config['UUID_API_URL'] + '/file-id/' + uuid

    # Use modified version of globus app secrect from configuration as the internal token
    # All API endpoints specified in gateway regardless of auth is required or not, 
    # will consider this internal token as valid and has the access to HuBMAP-Read group
    request_headers = create_request_headers_for_auth(auth_helper_instance.getProcessSecret())

    # Disable ssl certificate verification
    response = requests.get(url = uuid_api_full_url, headers = request_headers, verify = False) 

    # Verify if requests used the cached response from the SQLite database
    verify_request_cache(uuid_api_full_url, response.from_cache)

    if response.status_code == 200:
        file_uuid_dict = response.json()

        # This given uuid is a file uuid
        if 'ancestor_uuid' in file_uuid_dict:
            logger.debug(f"======The given uuid {uuid} is not a dataset uuid but a file uuid======")

            # For thumbnail image file uuid, its ancestor_uuid (the parent_id when generating this file uuid)
            # is the actual dataset uuid that can be used to get back the data_access_level
            # Overwrite the default value
            dataset_uuid = file_uuid_dict['ancestor_uuid']
            dataset_uuid = '58ebb89caf1512e9452d1f9e0e1efa8e'
    elif response.status_code == 404:
        # Either the given uuid does not exist or it's not a file uuid
        # It could be a regular entity uuid but will return 404 by /file-id/<uuid>
        # We just log this and move forward
        # The call to entity-api will tell us if this dataset uuid exists and valid
        logger.debug(f"======Unable to find the file uuid: {uuid}, treat it as dataset uuid======")

        # Treat the given uuid as a dataset uuid
        dataset_uuid = uuid
    else:
        # uuid-api returns 400 if the given id is invalid
        msg = f"Unable to make a request to query the uuid via uuid-api: {uuid}"
        # Log the full stack trace, prepend a line with our message
        logger.exception(msg)

        logger.debug("======status code from uuid-api======")
        logger.debug(response.status_code)

        logger.debug("======response text from uuid-api======")
        logger.debug(response.text)

        # Also bubble up the error message from uuid-api
        raise requests.exceptions.RequestException(response.text)

    # Final return
    return dataset_uuid

# Verify if requests used the cached response from the SQLite database
def verify_request_cache(url, response_from_cache):
    now = time.ctime(int(time.time()))
    logger.debug(f"Time: {now} / GET request URL: {url} / Used requests cache: {response_from_cache}")
