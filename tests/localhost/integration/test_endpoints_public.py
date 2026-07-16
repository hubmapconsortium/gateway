"""
Tests for public entity-api endpoints accessible without authentication.

Auth classification source:
  gateway/api_endpoints.localhost.json, branch karlburke/CaptureAPIUsage

These tests call entity-api endpoints directly and verify responses.
No knowledge of hubmap-auth internal mechanisms.

Endpoints that take an <id> parameter use a well-formed UUID that does not
exist in the database (from test_config.yaml: fake_uuid). The expected
response is 404 (not found) rather than 401 (unauthorized) — confirming the
auth gate passed and business logic handled the request.

Endpoints that take no ID parameter assert 200.

Run all public endpoint tests:
    pytest test_endpoints_public.py -v

Run a subset by name pattern:
    pytest test_endpoints_public.py -k "datasets" -v
"""

import requests

TIMEOUT = 10


# ---------------------------------------------------------------------------
# GET - no ID parameter, assert 200
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: GET / auth: false
# @app.route('/', methods = ['GET'])
def test_root_endpoint(base_url):
    """Test GET / is publicly accessible."""
    r = requests.get(f"{base_url}/", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /status auth: false
# @app.route('/status', methods = ['GET'])
def test_status_endpoint(base_url):
    """Test GET /status is publicly accessible."""
    r = requests.get(f"{base_url}/status", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401
    assert isinstance(r.json(), dict)

# gateway api_endpoints.*.json authorization: GET /entity-types auth: false
# @app.route('/entity-types', methods = ['GET'])
def test_entity_types_endpoint(base_url):
    """Test GET /entity-types is publicly accessible."""
    r = requests.get(f"{base_url}/entity-types", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /datasets/sankey_data auth: false
# @app.route('/datasets/sankey_data', methods=['GET'])
def test_datasets_sankey_data(base_url):
    """Test GET /datasets/sankey_data is publicly accessible."""
    r = requests.get(f"{base_url}/datasets/sankey_data", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401


# ---------------------------------------------------------------------------
# GET - ID parameter present, assert 404 (not 401)
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: GET /entities/<*> auth: false
# @app.route('/entities/<id>', methods = ['GET'])
def test_entities_lookup(base_url, fake_uuid):
    """Test GET /entities/<id> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/entities/{fake_uuid}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /entities/<*>/provenance auth: false
# @app.route('/entities/<id>/provenance', methods = ['GET'])
def test_entities_provenance(base_url, fake_uuid):
    """Test GET /entities/<id>/provenance passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/entities/{fake_uuid}/provenance", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /entities/<*>/revisions auth: false
# @app.route('/entities/<id>/revisions', methods=['GET'])
def test_entities_revisions(base_url, fake_uuid):
    """Test GET /entities/<id>/revisions passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/entities/{fake_uuid}/revisions", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /entities/<*>/tuplets auth: false
# @app.route('/entities/<id>/tuplets', methods = ['GET'])
def test_entities_tuplets(base_url, fake_uuid):
    """Test GET /entities/<id>/tuplets passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/entities/{fake_uuid}/tuplets", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /entities/<*>/collections auth: false
# @app.route('/entities/<id>/collections', methods = ['GET'])
def test_entities_collections(base_url, fake_uuid):
    """Test GET /entities/<id>/collections passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/entities/{fake_uuid}/collections", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /entities/<*>/uploads auth: false
# @app.route('/entities/<id>/uploads', methods = ['GET'])
def test_entities_uploads(base_url, fake_uuid):
    """Test GET /entities/<id>/uploads passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/entities/{fake_uuid}/uploads", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /entities/<*>/globus-url auth: false
# @app.route('/entities/<id>/globus-url', methods = ['GET'])
def test_entities_globus_url(base_url, fake_uuid):
    """Test GET /entities/<id>/globus-url passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/entities/{fake_uuid}/globus-url", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /entities/<*>/ancestor-organs auth: false
# @app.route('/entities/<id>/ancestor-organs', methods = ['GET'])
def test_entities_ancestor_organs(base_url, fake_uuid):
    """Test GET /entities/<id>/ancestor-organs passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/entities/{fake_uuid}/ancestor-organs", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /entities/<*>/siblings auth: false
# @app.route('/entities/<id>/siblings', methods = ['GET'])
def test_entities_siblings(base_url, fake_uuid):
    """Test GET /entities/<id>/siblings passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/entities/{fake_uuid}/siblings", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /entities/<*>/instanceof/<*> auth: false
# @app.route('/entities/<id>/instanceof/<type>', methods=['GET'])
def test_entities_instanceof_type(base_url, fake_uuid):
    """Test GET /entities/<id>/instanceof/<type> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/entities/{fake_uuid}/instanceof/Sample", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /entities/type/<*>/instanceof/<*> auth: false
# @app.route('/entities/type/<type_a>/instanceof/<type_b>', methods=['GET'])
def test_entities_type_instanceof(base_url):
    """Test GET /entities/type/<type_a>/instanceof/<type_b> passes auth gate (expect 200, not 401)."""
    r = requests.get(f"{base_url}/entities/type/Sample/instanceof/Entity", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /ancestors/<*> auth: false
# @app.route('/ancestors/<id>', methods = ['GET'])
def test_ancestors_endpoint(base_url, fake_uuid):
    """Test GET /ancestors/<id> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/ancestors/{fake_uuid}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /parents/<*> auth: false
# @app.route('/parents/<id>', methods = ['GET'])
def test_parents_endpoint(base_url, fake_uuid):
    """Test GET /parents/<id> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/parents/{fake_uuid}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /datasets/<*>/prov-info auth: false
# @app.route('/datasets/<id>/prov-info', methods=['GET'])
def test_datasets_prov_info(base_url, fake_uuid):
    """Test GET /datasets/<id>/prov-info passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/datasets/{fake_uuid}/prov-info", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /datasets/<*>/prov-metadata auth: false
# @app.route('/datasets/<id>/prov-metadata', methods=['GET'])
def test_datasets_prov_metadata(base_url, fake_uuid):
    """Test GET /datasets/<id>/prov-metadata passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/datasets/{fake_uuid}/prov-metadata", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /datasets/<*>/revisions auth: false
# @app.route('/datasets/<id>/revisions', methods=['GET'])
def test_datasets_revisions(base_url, fake_uuid):
    """Test GET /datasets/<id>/revisions passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/datasets/{fake_uuid}/revisions", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /datasets/<*>/revision auth: false
# @app.route('/datasets/<id>/revision', methods=['GET'])
def test_datasets_revision(base_url, fake_uuid):
    """Test GET /datasets/<id>/revision passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/datasets/{fake_uuid}/revision", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /datasets/<*>/latest-revision auth: false
# @app.route('/datasets/<id>/latest-revision', methods=['GET'])
def test_datasets_latest_revision(base_url, fake_uuid):
    """Test GET /datasets/<id>/latest-revision passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/datasets/{fake_uuid}/latest-revision", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /datasets/<*>/donors auth: false
# @app.route('/datasets/<id>/donors', methods=['GET'])
def test_datasets_donors(base_url, fake_uuid):
    """Test GET /datasets/<id>/donors passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/datasets/{fake_uuid}/donors", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /datasets/<*>/samples auth: false
# @app.route('/datasets/<id>/samples', methods=['GET'])
def test_datasets_samples(base_url, fake_uuid):
    """Test GET /datasets/<id>/samples passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/datasets/{fake_uuid}/samples", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /datasets/<*>/organs auth: false
# @app.route('/datasets/<id>/organs', methods=['GET'])
def test_datasets_organs(base_url, fake_uuid):
    """Test GET /datasets/<id>/organs passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/datasets/{fake_uuid}/organs", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /datasets/<*>/paired-dataset auth: false
# @app.route('/datasets/<id>/paired-dataset', methods=['GET'])
def test_datasets_paired_dataset(base_url, fake_uuid):
    """Test GET /datasets/<id>/paired-dataset passes auth gate (expect 404, not 401)."""
    r = requests.get(
        f"{base_url}/datasets/{fake_uuid}/paired-dataset",
        params={"data_type": "whatever"},
        timeout=TIMEOUT
    )
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /dataset/globus-url/<*> auth: false
# @app.route('/dataset/globus-url/<id>', methods = ['GET'])
def test_dataset_globus_url(base_url, fake_uuid):
    """Test GET /dataset/globus-url/<id> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/dataset/globus-url/{fake_uuid}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /entities/dataset/globus-url/<*> auth: false
# @app.route('/entities/dataset/globus-url/<id>', methods = ['GET'])
def test_entities_dataset_globus_url(base_url, fake_uuid):
    """Test GET /entities/dataset/globus-url/<id> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/entities/dataset/globus-url/{fake_uuid}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /redirect/<*> auth: false
# @app.route('/redirect/<hmid>', methods = ['GET'])
def test_redirect_by_hmid(base_url):
    """Test GET /redirect/<hmid> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/redirect/HBM123.ABCD.456", timeout=TIMEOUT, allow_redirects=False)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /doi/redirect/<*> auth: false
# @app.route('/doi/redirect/<id>', methods = ['GET'])
def test_doi_redirect(base_url, fake_uuid):
    """Test GET /doi/redirect/<id> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/doi/redirect/{fake_uuid}", timeout=TIMEOUT, allow_redirects=False)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /collection/redirect/<*> auth: false
# @app.route('/collection/redirect/<id>', methods = ['GET'])
def test_collection_redirect(base_url, fake_uuid):
    """Test GET /collection/redirect/<id> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/collection/redirect/{fake_uuid}", timeout=TIMEOUT, allow_redirects=False)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /documents/<*> auth: false
# @app.route('/documents/<id>', methods = ['GET'])
def test_documents_endpoint(base_url, fake_uuid):
    """Test GET /documents/<id> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/documents/{fake_uuid}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: covered by catch-all GET /<*> auth: false
# @app.route('/visibility/<id>', methods = ['GET'])
# N.B. Not an endpoint exposed by the gateway
def test_visibility_endpoint(base_url, fake_uuid):
    """Test GET /visibility/<id> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/visibility/{fake_uuid}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: covered by catch-all GET /<*> auth: false
# @app.route('/<entity_type>/entities', methods = ['GET'])
# N.B. Not an endpoint exposed by the gateway
def test_entity_type_entities_list(base_url):
    """Test GET /<entity_type>/entities passes auth gate (expect 200, not 401)."""
    r = requests.get(f"{base_url}/Sample/entities", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401


# ---------------------------------------------------------------------------
# POST
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: POST /entities/batch-ids auth: false
# @app.route('/entities/batch-ids', methods = ['POST'])
def test_entities_batch_ids(base_url, fake_uuid):
    """Test POST /entities/batch-ids passes auth gate (expect 404, not 401)."""
    r = requests.post(
        f"{base_url}/entities/batch-ids",
        json=[fake_uuid],
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: POST /constraints auth: false
# @app.route('/constraints', methods=['POST'])
def test_constraints_endpoint(base_url):
    """Test POST /constraints passes auth gate (expect 200, not 401)."""
    r = requests.post(
        f"{base_url}/constraints",
        json=[{
            "ancestors": {
                    "entity_type": "sample",
                    "sub_type": ["organ"],
                    "sub_type_val": ["BD"]
            },
            "descendants": {
                "entity_type": "sample",
                "sub_type": ["suspension"]
            }
        }],
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401


# ---------------------------------------------------------------------------
# PUT
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: PUT /datasets auth: false
# @app.route('/datasets', methods=['PUT'])
def test_datasets_bulk_update(base_url, fake_uuid):
    """Test PUT /datasets passes auth gate (expect 404, not 401)."""
    r = requests.put(
        f"{base_url}/datasets",
        json={"uuids": [fake_uuid]},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: PUT /uploads auth: false
# @app.route('/uploads', methods=['PUT'])
def test_uploads_update(base_url, fake_uuid):
    """Test PUT /uploads passes auth gate (expect 404, not 401)."""
    r = requests.put(
        f"{base_url}/uploads",
        json={"uuids": [fake_uuid]},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code == 404
    assert r.status_code != 401
