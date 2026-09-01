"""
EndpointAuthorizer - evaluates whether a request is authorized to access
a matched API endpoint item.

Usage in app.py:
    from endpoint_authorizer import endpoint_authorizer

    if endpoint_authorizer.api_access_allowed(item, request):
        ...
"""

import logging
import warnings
import time
from datetime import datetime, timezone

# HuBMAP commons
from hubmap_commons.hm_auth import AuthHelper

# local imports
import gateway_exceptions as gwEx

# For the hooks used to log endpoint usage, set the level to use while
# logging these events by using an unnamed level as close to the configured
# level, but high enough to log.
_ENDPOINT_LOG_LEVEL_NAME = "API_USAGE"
_MAX_SEARCH = 5

def _find_available_level(start_level: int, max_level: int) -> int | None:
    """Return the first unnamed level at or above logger's effective level.

    A level is considered unnamed if logging.getLevelName() returns the
    default 'Level <N>' string that Python assigns to unregistered levels.
    """
    for candidate in range(start_level, max_level):
        if logging.getLevelName(candidate) == f"Level {candidate}":
            return candidate
    return None

def _register_endpoint_log_level(logger: logging.Logger) -> int:
    """Register API_USAGE at the first available level at or above the
    logger's effective level. Returns the registered level."""
    level = _find_available_level(start_level = logger.getEffectiveLevel()
                                  , max_level = logger.getEffectiveLevel()+_MAX_SEARCH)
    if level is None:
        effective = logger.getEffectiveLevel()
        warnings.warn(message = f"Could not find an unnamed log level in range "
                                f"[{effective}, {effective + _MAX_SEARCH - 1}]. "
                                f"Falling back to the logger's effective level "
                                f" ({effective}) named '{logging.getLevelName(effective)}' ")
        logger.critical(f"Endpoint usage log message will not be emitted with a level named "
                        f" '{_ENDPOINT_LOG_LEVEL_NAME}', but will be emitted as '{logging.getLevelName(effective)}'")
        return effective
    else:
        logging.addLevelName(level, _ENDPOINT_LOG_LEVEL_NAME)
        logger.info(f"Set the endpoint usage log level to "
                    f"{level}, emitting with the name {logging.getLevelName(level)}.")
        return level

class EndpointAuthorizer:

    def __init__(self, ahi:AuthHelper):
        self.logger = logging.getLogger('gateway')
        self.effective_endpoint_log_level = _register_endpoint_log_level(self.logger)
        self._auth_functions = {
            'read':             self._handle_read_auth,
            'create':           self._handle_write_auth,
            'data-admin':       self._handle_data_admin_auth,
            'pipeline-test':    self._handle_pipeline_testing_auth
        }
        self._auth_helper_instance: AuthHelper = ahi

    # ------------------------------------------------------------------
    # Authorization handlers
    # Each accepts a request and returns bool.
    # Stubs - replace with real logic as handlers are expanded.
    # ------------------------------------------------------------------

    def _handle_read_auth(self, request_token) -> bool:
        return self._auth_helper_instance.has_read_privs(request_token)

    def _handle_write_auth(self, request_token) -> bool:
        return self._auth_helper_instance.has_write_privs(request_token)

    def _handle_data_admin_auth(self, request_token) -> bool:
        return self._auth_helper_instance.has_data_admin_privs(request_token)

    def _handle_pipeline_testing_auth(self, request_token) -> bool:
        return self._auth_helper_instance.has_pipeline_testing_privs(request_token)

    def _handle_unknown_auth(self, auth_type: str) -> bool:
        raise ValueError(f"Authorization method '{auth_type}' not supported")

    # Indicate if the token parsed from the request is the secret, internal Globus token
    def _is_secret_token(self, request_token) -> bool:
        internal_token = self._auth_helper_instance.getProcessSecret()

        return internal_token == request_token

    # Pull the token from the Request
    def _get_request_bearer_token(self, request) -> bool:
        if 'Authorization' not in request.headers:
            raise gwEx.GWNoAuthHeaderException('Missing Authorization header')
        if not request.headers['Authorization'].upper().startswith('BEARER '):
            raise gwEx.GWNoBearerSchemeException('Missing Bearer token')
        return request.headers['Authorization'][6:].strip()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def api_access_allowed(self, item, request) -> bool:
        """Return True if the request is authorized to access the endpoint item.

        Access is granted unconditionally when:
          - the item has no 'authorizer' key, or
          - the request carries the Globus internal secret token.

        Otherwise, the appropriate handler for item['authorizer'] is invoked.
        Raises ValueError if the authorizer type is unrecognized.
        """
        self.logger.info("======Matched endpoint======")
        self.logger.info(item)

        determination_log_msg = f"Authorization from api_access_allowed is'" \
                                  f" '_DETERMINATION_' for" \
                                  f" {request.headers.get("Host")}," \
                                  f" {request.headers.get("X-Original-Request-Method")}," \
                                  f" {request.headers.get("X-Original-URI")}."

        # If no authorizer is identified for the endpoint, access is allowed
        if 'authorizer' not in item:
            self.logger.debug(determination_log_msg.replace('_DETERMINATION_', f"{True}"))
            return True

        try:
            token = self._get_request_bearer_token(request=request)
        except (gwEx.GWNoAuthHeaderException, gwEx.GWNoBearerSchemeException) as gwe:
            self.logger.debug(f"Setting access_allowed_determination to False due to token problem:"
                              f" '{gwe.message}'")
            access_allowed_determination = False
            self.logger.debug(determination_log_msg.replace('_DETERMINATION_', f"{access_allowed_determination}"))
            return access_allowed_determination

        # Allow access for any request presenting the secret, internal Globus token
        if self._is_secret_token(token):
            self.logger.debug(determination_log_msg.replace('_DETERMINATION_', f"{True}"))
            return True

        auth_handler = self._auth_functions.get(item['authorizer'])
        if auth_handler is None:
            self.logger.error(f"Authorization method '{item['authorizer']}' configured for"
                                f" {request.headers.get("Host")},"
                                f" {request.headers.get("X-Original-Request-Method")},"
                                f" {request.headers.get("X-Original-URI")} "
                                f" is not supported.")
            self._handle_unknown_auth(item['authorizer'])
        access_allowed_determination = auth_handler(request_token=token)
        if not isinstance(access_allowed_determination, bool):
            self.logger.debug(  f"Based on auth_handler returning "
                                f" '{access_allowed_determination}'"
                                f" setting access_allowed_determination to False.")
            access_allowed_determination = False
        self.logger.debug(determination_log_msg.replace('_DETERMINATION_', f"{access_allowed_determination}"))
        return access_allowed_determination

    def log_auth_decision(self, response_code, response_length, auth_req_api, method, endpoint, client_ip, matched_pattern=None):
        """
        Log authorization decision in Common Log Format.

        Logs each authorization check with details about the request and decision.
        Format matches entity-api's after_request logging style.

        Args:
            response_code: HTTP status code (200 for authorized, 401 for denied)
            auth_req_api: The service/host making the request (e.g., "entity-api")
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: The original endpoint being accessed (e.g., "/entities/abc123")
            matched_pattern: The pattern that matched from api_endpoints.json (e.g., "/entities/<*>")
                            or special values: "NO_MATCH", "UNKNOWN_SERVICE", "MISSING_HEADERS"
        """
        # Bail out immediately if the log statement about to be build would not be emitted.
        if not self.logger.isEnabledFor(self.effective_endpoint_log_level):
            return

        # Assume caller has extracted a single IP address using the X-Forwarded-For header, but
        # switch to log a conventional '-' if it is not set.
        client_ip = client_ip or '-'

        # Caller - not available without AWS IAM, use '-'
        caller = '-'

        # User - not available at authorization time (token not yet validated)
        # Could extract from Authorization header if needed, but use '-' for now
        user = '-'

        # Request time in AWS/Apache format: [DD/MMM/YYYY:HH:MM:SS +0000]
        request_time = datetime.now(timezone.utc).strftime('%d/%b/%Y:%H:%M:%S +0000')

        # HTTP method and resource path from parameters
        # method and endpoint are passed as parameters (not from Flask request object)
        # because they come from X-Original-* headers, not the /api_auth request itself

        # Protocol - assume HTTP/1.1 for auth requests
        protocol = 'HTTP/1.1'
        #
        # # Response length - auth responses are small JSON messages (~34 bytes for 401, ~26 for 200)
        # # Use approximate sizes or '-'
        # response_length = 34 if response_code == 401 else 26

        # Add matched pattern as additional info if available
        # This helps understand which rule was applied
        pattern_info = f"pattern={matched_pattern}" if matched_pattern else ""

        # Add the API originating the authorization as additional info need by API Usage reporting
        authority_info = f"authority={auth_req_api}" if auth_req_api else ""

        # Format log message matching Common Log Format, aligned with these AWS API Gateway fields for
        # custom access logs:
        # $sourceIp $caller $user [$requestTime] "$method $resourcePath $protocol" $status $responseLength
        log_message = (
            f'{client_ip}' # aligned with AWS API Gateway $sourceIp
            f' {caller}' # aligned with AWS API Gateway $caller
            f' {user}' # aligned with AWS API Gateway $user
            f' [{request_time}]' # aligned with AWS API Gateway $requestTime
            f' "{method} {endpoint} {protocol}"' # aligned with AWS API Gateway $method $resourcePath $protocol
            f' {response_code}' # aligned with AWS API Gateway $status
            f' {response_length}'
            f' {pattern_info}'    # Supplemental data for reporting, beyond Common Log Format
            f' {authority_info}'  # Supplemental data for reporting, beyond Common Log Format
        )

        self.logger.log(level=self.effective_endpoint_log_level
                        , msg=log_message)
