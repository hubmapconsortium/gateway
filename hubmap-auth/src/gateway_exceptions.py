# Exceptions used internally by the service, typically for anticipated exceptions.
# Knowledge of Flask, HTTP codes, and formatting of the Response should be
# closer to the endpoint @app.route() methods rather than throughout service.
class GWConfigurationException(Exception):
    """Exception raised when problems loading the service configuration are encountered."""
    def __init__(self, message='There were problems loading the configuration for the service.'):
        self.message = message
        super().__init__(self.message)

class GWNoAuthHeaderException(Exception):
    """Exception raised when authorization header is not present in the request."""
    def __init__(self, message='Missing Authorization header.'):
        self.message = message
        super().__init__(self.message)

class GWNoBearerSchemeException(Exception):
    """Exception raised when a bearer token is not present in the request."""
    def __init__(self, message='Missing Bearer token.'):
        self.message = message
        super().__init__(self.message)
