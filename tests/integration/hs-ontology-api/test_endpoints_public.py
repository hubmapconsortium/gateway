"""
Tests for public hs-ontology-api endpoints accessible without authentication.

Auth classification source:
  gateway/api_endpoints.localhost.json, branch karlburke/CaptureAPIUsage

All hs-ontology-api endpoints are public — no authorizer is configured in
the AWS API Gateway definition.

Endpoints that take a parameter use a bogus identifier (test-id or similar).
The expected response is 404 (not found) rather than 401 (unauthorized),
confirming the auth gate passed and business logic handled the request.

Endpoints that take no parameter assert 200.

Run all hs-ontology-api public endpoint tests:
    TEST_API="hs-ontology-api" pytest test_hs_ontology_api_endpoints_public.py -v

Run a subset by name pattern:
    TEST_API="hs-ontology-api" pytest test_hs_ontology_api_endpoints_public.py -k "field" -v
"""

import requests

TIMEOUT = 10
_ID = "test-id"
_IDS = "test-id1,test-id2"
_SAB = "test-sab"
_NAME = "test-name"
_SYMBOL = "test-symbol"
_CONCEPT = "test-concept"
_TERM = "test-term"
_CODE = "test-code"
_SEMANTIC = "test-semantic"


# ---------------------------------------------------------------------------
# GET - no parameter, assert 200
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: GET / auth: false
def test_root_endpoint(base_url):
    """Test GET / is publicly accessible."""
    r = requests.get(f"{base_url}/", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /status auth: false
def test_status_endpoint(base_url):
    """Test GET /status is publicly accessible."""
    r = requests.get(f"{base_url}/status", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401
    assert isinstance(r.json(), dict)

# gateway api_endpoints.*.json authorization: GET /property-types auth: false
def test_property_types(base_url):
    """Test GET /property-types is publicly accessible."""
    r = requests.get(f"{base_url}/property-types", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /sabs auth: false
def test_sabs(base_url):
    """Test GET /sabs is publicly accessible."""
    r = requests.get(f"{base_url}/sabs", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /sabs/codes/counts auth: false
def test_sabs_codes_counts(base_url):
    """Test GET /sabs/codes/counts is publicly accessible."""
    r = requests.get(f"{base_url}/sabs/codes/counts", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /pathways/with-genes auth: false
def test_pathways_with_genes(base_url):
    """Test GET /pathways/with-genes is publicly accessible."""
    r = requests.get(f"{base_url}/pathways/with-genes", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /genes-info auth: false
def test_genes_info(base_url):
    """Test GET /genes-info is publicly accessible."""
    r = requests.get(f"{base_url}/genes-info", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /proteins-info auth: false
def test_proteins_info(base_url):
    """Test GET /proteins-info is publicly accessible."""
    r = requests.get(f"{base_url}/proteins-info", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /celltypes-info auth: false
def test_celltypes_info(base_url):
    """Test GET /celltypes-info is publicly accessible."""
    r = requests.get(f"{base_url}/celltypes-info", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /field-assays auth: false
def test_field_assays(base_url):
    """Test GET /field-assays is publicly accessible."""
    r = requests.get(f"{base_url}/field-assays", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /field-descriptions auth: false
def test_field_descriptions(base_url):
    """Test GET /field-descriptions is publicly accessible."""
    r = requests.get(f"{base_url}/field-descriptions", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /field-entities auth: false
def test_field_entities(base_url):
    """Test GET /field-entities is publicly accessible."""
    r = requests.get(f"{base_url}/field-entities", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /field-schemas auth: false
def test_field_schemas(base_url):
    """Test GET /field-schemas is publicly accessible."""
    r = requests.get(f"{base_url}/field-schemas", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /field-types auth: false
def test_field_types(base_url):
    """Test GET /field-types is publicly accessible."""
    r = requests.get(f"{base_url}/field-types", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /field-types-info auth: false
def test_field_types_info(base_url):
    """Test GET /field-types-info is publicly accessible."""
    r = requests.get(f"{base_url}/field-types-info", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /node-types auth: false
def test_node_types(base_url):
    """Test GET /node-types is publicly accessible."""
    r = requests.get(f"{base_url}/node-types", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /relationship-types auth: false
def test_relationship_types(base_url):
    """Test GET /relationship-types is publicly accessible."""
    r = requests.get(f"{base_url}/relationship-types", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /semantics/semantic-types auth: false
def test_semantics_semantic_types(base_url):
    """Test GET /semantics/semantic-types is publicly accessible."""
    r = requests.get(f"{base_url}/semantics/semantic-types", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /organs auth: false
def test_organs(base_url):
    """Test GET /organs is publicly accessible (requires application_context param, expect 400 without it)."""
    r = requests.get(f"{base_url}/organs", timeout=TIMEOUT)
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /organs/by-code auth: false
def test_organs_by_code(base_url):
    """Test GET /organs/by-code is publicly accessible (requires application_context param, expect 400 without it)."""
    r = requests.get(f"{base_url}/organs/by-code", timeout=TIMEOUT)
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /sources auth: false
def test_sources(base_url):
    """Test GET /sources is publicly accessible."""
    r = requests.get(f"{base_url}/sources", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /annotations auth: false
def test_annotations(base_url):
    """Test GET /annotations is publicly accessible (requires params, expect 400 without them)."""
    r = requests.get(f"{base_url}/annotations", timeout=TIMEOUT)
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /annotations/organs auth: false
def test_annotations_organs(base_url):
    """Test GET /annotations/organs is publicly accessible."""
    r = requests.get(f"{base_url}/annotations/organs", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /annotations/organ-levels auth: false
def test_annotations_organ_levels(base_url):
    """Test GET /annotations/organ-levels is publicly accessible."""
    r = requests.get(f"{base_url}/annotations/organ-levels", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /assayclasses auth: false
def test_assayclasses(base_url):
    """Test GET /assayclasses is publicly accessible (requires params, expect 400 without them)."""
    r = requests.get(f"{base_url}/assayclasses", timeout=TIMEOUT)
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /dataset-types auth: false
def test_dataset_types(base_url):
    """Test GET /dataset-types is publicly accessible (requires params, expect 400 without them)."""
    r = requests.get(f"{base_url}/dataset-types", timeout=TIMEOUT)
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /dataset-types/hierarchy auth: false
def test_dataset_types_hierarchy(base_url):
    """Test GET /dataset-types/hierarchy is publicly accessible (requires params, expect 400 without them)."""
    r = requests.get(f"{base_url}/dataset-types/hierarchy", timeout=TIMEOUT)
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /dataset-types/hierarchy/valueset auth: false
def test_dataset_types_hierarchy_valueset(base_url):
    """Test GET /dataset-types/hierarchy/valueset is publicly accessible (expect 404 or 400, not 401)."""
    r = requests.get(f"{base_url}/dataset-types/hierarchy/valueset", timeout=TIMEOUT)
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /concepts/paths/subgraph auth: false
def test_concepts_paths_subgraph(base_url):
    """Test GET /concepts/paths/subgraph is publicly accessible (requires params, expect 400 without them)."""
    r = requests.get(f"{base_url}/concepts/paths/subgraph", timeout=TIMEOUT)
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /concepts/paths/subgraph/sequential auth: false
def test_concepts_paths_subgraph_sequential(base_url):
    """Test GET /concepts/paths/subgraph/sequential is publicly accessible (requires params, expect 400 without them)."""
    r = requests.get(f"{base_url}/concepts/paths/subgraph/sequential", timeout=TIMEOUT)
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /database/server auth: false
def test_database_server(base_url):
    """Test GET /database/server is publicly accessible."""
    r = requests.get(f"{base_url}/database/server", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /valueset auth: false
def test_valueset(base_url):
    """Test GET /valueset passes auth gate (expect 400 for missing params, not 401)."""
    r = requests.get(f"{base_url}/valueset", timeout=TIMEOUT)
    assert r.status_code != 401


# ---------------------------------------------------------------------------
# GET - parameter present, assert 404 (not 401)
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: GET /sabs/<*>/codes/counts auth: false
def test_sabs_sab_codes_counts(base_url):
    """Test GET /sabs/<sab>/codes/counts passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/sabs/{_SAB}/codes/counts", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /sabs/<*>/codes/details auth: false
def test_sabs_sab_codes_details(base_url):
    """Test GET /sabs/<sab>/codes/details passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/sabs/{_SAB}/codes/details", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /sabs/<*>/term-types auth: false
def test_sabs_sab_term_types(base_url):
    """Test GET /sabs/<sab>/term-types passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/sabs/{_SAB}/term-types", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /pathways/<*>/participants auth: false
def test_pathways_participants(base_url):
    """Test GET /pathways/<id>/participants passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/pathways/{_ID}/participants", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /genes/<*> auth: false
def test_genes_by_id(base_url):
    """Test GET /genes/<ids> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/genes/{_IDS}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /genes/<*>/detail auth: false
def test_genes_detail(base_url):
    """Test GET /genes/<ids>/detail passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/genes/{_IDS}/detail", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /proteins/<*> auth: false
def test_proteins_by_id(base_url):
    """Test GET /proteins/<id> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/proteins/{_ID}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /celltypes/<*> auth: false
def test_celltypes_by_id(base_url):
    """Test GET /celltypes/<ids> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/celltypes/{_IDS}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /celltypes/<*>/detail auth: false
def test_celltypes_detail(base_url):
    """Test GET /celltypes/<ids>/detail passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/celltypes/{_IDS}/detail", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /field-assays/<*> auth: false
def test_field_assays_by_name(base_url):
    """Test GET /field-assays/<name> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/field-assays/{_NAME}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /field-descriptions/<*> auth: false
def test_field_descriptions_by_name(base_url):
    """Test GET /field-descriptions/<name> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/field-descriptions/{_NAME}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /field-entities/<*> auth: false
def test_field_entities_by_name(base_url):
    """Test GET /field-entities/<name> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/field-entities/{_NAME}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /field-schemas/<*> auth: false
def test_field_schemas_by_name(base_url):
    """Test GET /field-schemas/<name> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/field-schemas/{_NAME}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /field-types/<*> auth: false
def test_field_types_by_name(base_url):
    """Test GET /field-types/<name> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/field-types/{_NAME}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /terms/<*>/codes auth: false
def test_terms_codes(base_url):
    """Test GET /terms/<term_id>/codes passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/terms/{_TERM}/codes", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /terms/<*>/concepts auth: false
def test_terms_concepts(base_url):
    """Test GET /terms/<term_id>/concepts passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/terms/{_TERM}/concepts", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /codes/<*>/terms auth: false
def test_codes_terms(base_url):
    """Test GET /codes/<code_id>/terms passes auth gate (expect 400 or 404, not 401)."""
    r = requests.get(f"{base_url}/codes/{_CODE}/terms", timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /codes/<*>/codes auth: false
def test_codes_codes(base_url):
    """Test GET /codes/<code_id>/codes passes auth gate (expect 400 or 404, not 401)."""
    r = requests.get(f"{base_url}/codes/{_CODE}/codes", timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /codes/<*>/concepts auth: false
def test_codes_concepts(base_url):
    """Test GET /codes/<code_id>/concepts passes auth gate (expect 400 or 404, not 401)."""
    r = requests.get(f"{base_url}/codes/{_CODE}/concepts", timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /concepts/<*>/codes auth: false
def test_concepts_codes(base_url):
    """Test GET /concepts/<concept_id>/codes passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/concepts/{_CONCEPT}/codes", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /concepts/<*>/concepts auth: false
def test_concepts_concepts(base_url):
    """Test GET /concepts/<concept_id>/concepts passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/concepts/{_CONCEPT}/concepts", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /concepts/<*>/definitions auth: false
def test_concepts_definitions(base_url):
    """Test GET /concepts/<concept_id>/definitions passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/concepts/{_CONCEPT}/definitions", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /concepts/<*>/nodeobjects auth: false
def test_concepts_nodeobjects(base_url):
    """Test GET /concepts/<concept_id>/nodeobjects passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/concepts/{_CONCEPT}/nodeobjects", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /concepts/<*>/paths/expand auth: false
def test_concepts_paths_expand(base_url):
    """Test GET /concepts/<concept_id>/paths/expand passes auth gate (expect 400 or 404, not 401)."""
    r = requests.get(f"{base_url}/concepts/{_CONCEPT}/paths/expand",
                     params={"rel": "test-rel", "sab": _SAB}, timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /concepts/<*>/paths/shortestpath/<*> auth: false
def test_concepts_paths_shortestpath(base_url):
    """Test GET /concepts/<concept_id>/paths/shortestpath/<terminus> passes auth gate (expect 400 or 404, not 401)."""
    r = requests.get(f"{base_url}/concepts/{_CONCEPT}/paths/shortestpath/test-terminus",
                     params={"rel": "test-rel", "sab": _SAB}, timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /concepts/<*>/paths/subgraph/sequential auth: false
def test_concepts_paths_subgraph_sequential_with_id(base_url):
    """Test GET /concepts/<concept_id>/paths/subgraph/sequential passes auth gate (expect 400 or 404, not 401)."""
    r = requests.get(f"{base_url}/concepts/{_CONCEPT}/paths/subgraph/sequential", timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /concepts/<*>/paths/subgraph/sequential/sequential auth: false
def test_concepts_paths_subgraph_sequential_sequential(base_url):
    """Test GET /concepts/<concept_id>/paths/subgraph/sequential/sequential passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/concepts/{_CONCEPT}/paths/subgraph/sequential/sequential", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /concepts/<*>/paths/trees auth: false
def test_concepts_paths_trees(base_url):
    """Test GET /concepts/<concept_id>/paths/trees passes auth gate (expect 400 or 404, not 401)."""
    r = requests.get(f"{base_url}/concepts/{_CONCEPT}/paths/trees",
                     params={"rel": "test-rel", "sab": _SAB}, timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /node-types/<*>/counts auth: false
def test_node_types_counts(base_url):
    """Test GET /node-types/<node_type>/counts passes auth gate (expect 400 or 404, not 401)."""
    r = requests.get(f"{base_url}/node-types/{_ID}/counts", timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /node-types/<*>/counts-by-sab auth: false
def test_node_types_counts_by_sab(base_url):
    """Test GET /node-types/<node_type>/counts-by-sab passes auth gate (expect 400 or 404, not 401)."""
    r = requests.get(f"{base_url}/node-types/{_ID}/counts-by-sab",
                     params={"sab": _SAB}, timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /relationships/gene/<*> auth: false
def test_relationships_gene(base_url):
    """Test GET /relationships/gene/<target_symbol> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/relationships/gene/{_SYMBOL}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /semantics/semantic-types/<*> auth: false
def test_semantics_semantic_types_by_id(base_url):
    """Test GET /semantics/semantic-types/<identifier> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/semantics/semantic-types/{_SEMANTIC}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /semantics/semantic-types/<*>/subtypes auth: false
def test_semantics_semantic_types_subtypes(base_url):
    """Test GET /semantics/semantic-types/<identifier>/subtypes passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/semantics/semantic-types/{_SEMANTIC}/subtypes", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /annotations/<*> auth: false
def test_annotations_by_id(base_url):
    """Test GET /annotations/<ids> passes auth gate (expect 400 or 404, not 401)."""
    r = requests.get(f"{base_url}/annotations/{_IDS}", timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /annotations/<*>/organs auth: false
def test_annotations_by_id_organs(base_url):
    """Test GET /annotations/<ids>/organs passes auth gate (expect 400 or 404, not 401)."""
    r = requests.get(f"{base_url}/annotations/{_IDS}/organs", timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /annotations/<*>/organ-levels auth: false
def test_annotations_by_id_organ_levels(base_url):
    """Test GET /annotations/<ids>/organ-levels passes auth gate (expect 400 or 404, not 401)."""
    r = requests.get(f"{base_url}/annotations/{_IDS}/organ-levels", timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /assayclasses/<*> auth: false
def test_assayclasses_by_name(base_url):
    """Test GET /assayclasses/<name> passes auth gate (expect 400 or 404, not 401)."""
    r = requests.get(f"{base_url}/assayclasses/{_NAME}", timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /dataset-types/hierarchy/<*> auth: false
def test_dataset_types_hierarchy_by_code(base_url):
    """Test GET /dataset-types/hierarchy/<dataset_type_code> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/dataset-types/hierarchy/{_ID}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /dataset-types/hierarchy/<*>/<*> auth: false
def test_dataset_types_hierarchy_two_codes(base_url):
    """Test GET /dataset-types/hierarchy/<dataset_type_code>/<modality_code> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/dataset-types/hierarchy/{_ID}/test-modality", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /dataset-types/hierarchy/<*>/<*>/<*> auth: false
def test_dataset_types_hierarchy_three_codes(base_url):
    """Test GET /dataset-types/hierarchy/<dataset_type_code>/<modality_code>/<analyte_code> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/dataset-types/hierarchy/{_ID}/test-modality/test-analyte", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401
