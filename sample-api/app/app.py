from flask import Flask, request, jsonify, make_response
import json

# Init app
app = Flask(__name__)

####################################################################################################
## API Endpoints
####################################################################################################

# Public endpoint, no auth
@app.route('/', methods = ['GET'])
def index():
    return "Hello! This is HuBMAP sample API service :)"

# Public endpoint, no auth
@app.route('/status', methods = ['GET'])
def status():
    return "Status of this sample API: running..."

# Private endpoint, requires auth and group access
# But the nexus token is invalid for the defiend group access 
@app.route('/invalid', methods = ['GET'])
def invalid():
    return "You won't be able to see this message due to invalid group access!"

# Private endpoint, requires auth and group access
@app.route('/get', methods = ['GET'])
def get():
    mauth_json = parse_mauth()
    return make_response(mauth_json)

# Private endpoint, requires auth and group access
@app.route('/post', methods = ['POST'])
def post():
    # Display form data
    return make_response(jsonify(request.form))

# Private endpoint, requires auth and group access
@app.route('/put', methods = ['PUT'])
def put():
    return make_response(jsonify({"message": "Created"}), 201)

####################################################################################################
## Internal Functions
####################################################################################################

def parse_mauth():
    mauth_json = None
    if ("MAuthorization" in request.headers) and request.headers.get("MAuthorization").upper().startswith("MBEARER"):
        mauth = request.headers.get("MAuthorization")[7:].strip()
        mauth_json = json.loads(mauth)

    return mauth_json