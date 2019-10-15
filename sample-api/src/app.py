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
@app.route('/public', methods = ['GET'])
def public():
    return "This is a public endpoint"

# Private endpoint, requires auth
@app.route('/private', methods = ['GET'])
def private():
    return "This is a private endpoint"

# Public endpoint, no auth, but has parameter in path
@app.route('/public/<param>', methods = ['GET'])
def get_public_param(param):
    return param

# Private endpoint, requires auth, and also has parameter in path
@app.route('/private/<param>', methods = ['GET'])
def get_private_param(param):
    return param

# Private endpoint, requires auth and group access
@app.route('/private/group', methods = ['GET'])
def get_private_group():
    return "Yay!"

# Private endpoint, requires auth and group access, and also has parameter in path
@app.route('/private/<param>/group', methods = ['GET'])
def get_private_group_with_param(param):
    return "Yay! " + param

# Private endpoint, requires auth and group access
# But the nexus token is invalid for the defiend group access 
@app.route('/invalid', methods = ['GET'])
def invalid():
    return "You won't be able to see this message due to invalid group access!"

# Private endpoint, requires auth and group access
@app.route('/post', methods = ['POST'])
def post():
    # Display form data
    return make_response(jsonify(request.form))

# Private endpoint, requires auth and group access
@app.route('/put', methods = ['PUT'])
def put():
    return make_response(jsonify({"message": "Created"}), 201)
