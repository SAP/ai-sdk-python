"""Unit tests for sap_openapi_generator.preprocess_spec."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from sap_openapi_generator.preprocess_spec import (
    apply_api_name_extension,
    apply_operation_name_extension,
    apply_options_per_service,
    strip_api_suffix,
    validate_unique_operation_ids,
    _snake_case,
)


# ---------------------------------------------------------------------------
# strip_api_suffix
# ---------------------------------------------------------------------------


def test_strip_api_suffix_removes_trailing_Api():
    assert strip_api_suffix("FooApi") == "Foo"


def test_strip_api_suffix_case_sensitive_uppercase_unchanged():
    # Only literal "Api" is stripped — "API" is not (matches Java behavior)
    assert strip_api_suffix("FooAPI") == "FooAPI"


def test_strip_api_suffix_not_at_end():
    assert strip_api_suffix("MyApiService") == "MyApiService"


def test_strip_api_suffix_only_api():
    # Edge case: name IS "Api" → empty string
    assert strip_api_suffix("Api") == ""


def test_strip_api_suffix_no_suffix():
    assert strip_api_suffix("Foo") == "Foo"


# ---------------------------------------------------------------------------
# apply_api_name_extension
# ---------------------------------------------------------------------------


def _op(**kwargs) -> dict:
    op: dict = {"operationId": "defaultOp", "responses": {"200": {"description": "ok"}}}
    op.update(kwargs)
    return op


def test_api_name_root_level_applied_to_all_operations():
    spec = {
        "x-sap-cloud-sdk-api-name": "SodasApi",
        "paths": {
            "/sodas": {"get": _op(operationId="listSodas")},
            "/sodas/{id}": {"get": _op(operationId="getSoda")},
        },
    }
    apply_api_name_extension(spec)
    assert spec["paths"]["/sodas"]["get"]["tags"] == ["Sodas"]
    assert spec["paths"]["/sodas/{id}"]["get"]["tags"] == ["Sodas"]


def test_api_name_path_level_overrides_root():
    spec = {
        "x-sap-cloud-sdk-api-name": "RootApi",
        "paths": {
            "/a": {
                "x-sap-cloud-sdk-api-name": "PathApi",
                "get": _op(operationId="opA"),
            },
            "/b": {"get": _op(operationId="opB")},
        },
    }
    apply_api_name_extension(spec)
    assert spec["paths"]["/a"]["get"]["tags"] == ["Path"]
    assert spec["paths"]["/b"]["get"]["tags"] == ["Root"]


def test_api_name_operation_level_overrides_path_and_root():
    spec = {
        "x-sap-cloud-sdk-api-name": "RootApi",
        "paths": {
            "/a": {
                "x-sap-cloud-sdk-api-name": "PathApi",
                "get": _op(operationId="opA", **{"x-sap-cloud-sdk-api-name": "OperationApi"}),
            },
        },
    }
    apply_api_name_extension(spec)
    assert spec["paths"]["/a"]["get"]["tags"] == ["Operation"]


def test_api_name_no_extension_preserves_existing_tags():
    spec = {
        "paths": {
            "/a": {"get": {"operationId": "opA", "tags": ["existing"], "responses": {}}},
        }
    }
    apply_api_name_extension(spec)
    assert spec["paths"]["/a"]["get"]["tags"] == ["existing"]


def test_api_name_multiple_methods_on_same_path():
    spec = {
        "paths": {
            "/items": {
                "x-sap-cloud-sdk-api-name": "ItemsApi",
                "get": _op(operationId="listItems"),
                "post": _op(operationId="createItem"),
            }
        }
    }
    apply_api_name_extension(spec)
    assert spec["paths"]["/items"]["get"]["tags"] == ["Items"]
    assert spec["paths"]["/items"]["post"]["tags"] == ["Items"]


def test_api_name_non_http_method_keys_ignored():
    spec = {
        "x-sap-cloud-sdk-api-name": "FooApi",
        "paths": {
            "/a": {
                "parameters": [{"name": "id", "in": "path"}],
                "get": _op(operationId="getA"),
            }
        },
    }
    apply_api_name_extension(spec)
    assert spec["paths"]["/a"]["get"]["tags"] == ["Foo"]
    assert isinstance(spec["paths"]["/a"]["parameters"], list)


def test_api_name_empty_paths_does_not_crash():
    apply_api_name_extension({"paths": {}})


def test_api_name_no_paths_key_does_not_crash():
    apply_api_name_extension({})


# ---------------------------------------------------------------------------
# apply_operation_name_extension
# ---------------------------------------------------------------------------


def test_operation_name_overwrites_operation_id():
    spec = {
        "paths": {
            "/pets/{id}": {
                "get": {
                    "operationId": "getPetById",
                    "tags": ["Pets"],
                    "x-sap-cloud-sdk-operation-name": "fetchPet",
                    "responses": {},
                }
            }
        }
    }
    mappings = apply_operation_name_extension(spec)
    assert spec["paths"]["/pets/{id}"]["get"]["operationId"] == "fetchPet"
    assert mappings == {}


def test_operation_name_absent_leaves_operation_id_unchanged():
    spec = {"paths": {"/pets": {"get": {"operationId": "listPets", "responses": {}}}}}
    apply_operation_name_extension(spec)
    assert spec["paths"]["/pets"]["get"]["operationId"] == "listPets"


def test_operation_name_no_paths_key_does_not_crash():
    apply_operation_name_extension({})


def test_operation_name_disambiguates_cross_tag_collision():
    """Two operations in different tags both want 'search' — must be scoped."""
    spec = {
        "paths": {
            "/vector/search": {
                "post": {
                    "operationId": "vector.search_chunk",
                    "tags": ["Vector"],
                    "x-sap-cloud-sdk-operation-name": "search",
                    "responses": {},
                }
            },
            "/retrieval/search": {
                "post": {
                    "operationId": "retrieval.search",
                    "tags": ["Retrieval"],
                    "x-sap-cloud-sdk-operation-name": "search",
                    "responses": {},
                }
            },
        }
    }
    mappings = apply_operation_name_extension(spec)
    assert spec["paths"]["/vector/search"]["post"]["operationId"] == "vector_search"
    assert spec["paths"]["/retrieval/search"]["post"]["operationId"] == "retrieval_search"
    assert mappings == {"vector_search": "search", "retrieval_search": "search"}


def test_operation_name_no_collision_no_mappings():
    spec = {
        "paths": {
            "/a": {"get": {"operationId": "opA", "tags": ["A"],
                           "x-sap-cloud-sdk-operation-name": "getA", "responses": {}}},
            "/b": {"get": {"operationId": "opB", "tags": ["B"],
                           "x-sap-cloud-sdk-operation-name": "getB", "responses": {}}},
        }
    }
    mappings = apply_operation_name_extension(spec)
    assert spec["paths"]["/a"]["get"]["operationId"] == "getA"
    assert spec["paths"]["/b"]["get"]["operationId"] == "getB"
    assert mappings == {}


# ---------------------------------------------------------------------------
# _snake_case
# ---------------------------------------------------------------------------


def test_snake_case_camel():
    assert _snake_case("camelCase") == "camel_case"


def test_snake_case_pascal():
    assert _snake_case("PascalCase") == "pascal_case"


def test_snake_case_already_snake():
    assert _snake_case("already_snake") == "already_snake"


# ---------------------------------------------------------------------------
# Both extensions applied together
# ---------------------------------------------------------------------------


def test_both_extensions_applied_independently():
    spec = {
        "paths": {
            "/drinks/{id}": {
                "get": {
                    "operationId": "getDrinkById",
                    "x-sap-cloud-sdk-api-name": "DrinksApi",
                    "x-sap-cloud-sdk-operation-name": "fetchDrink",
                    "responses": {},
                }
            }
        }
    }
    apply_api_name_extension(spec)
    apply_operation_name_extension(spec)
    op = spec["paths"]["/drinks/{id}"]["get"]
    assert op["tags"] == ["Drinks"]
    assert op["operationId"] == "fetchDrink"

def test_no_extension_is_a_passthrough():
    spec = {
        "paths": {
            "/items": {
                "get": {"operationId": "listItems", "tags": ["items"], "responses": {}}
            }
        }
    }
    import copy
    original = copy.deepcopy(spec)
    apply_api_name_extension(spec)
    apply_operation_name_extension(spec)
    assert spec == original


# ---------------------------------------------------------------------------
# validate_unique_operation_ids
# ---------------------------------------------------------------------------


def test_validate_passes_when_all_ids_unique():
    spec = {
        "paths": {
            "/a": {"get": {"operationId": "opA", "responses": {}}},
            "/b": {"get": {"operationId": "opB", "responses": {}}},
        }
    }
    validate_unique_operation_ids(spec)  # must not raise or exit


def test_validate_exits_on_duplicate(capsys):
    spec = {
        "paths": {
            "/a": {"get": {"operationId": "dupOp", "responses": {}}},
            "/b": {"post": {"operationId": "dupOp", "responses": {}}},
        }
    }
    with pytest.raises(SystemExit) as exc_info:
        validate_unique_operation_ids(spec)
    assert exc_info.value.code == 1
    assert "dupOp" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# apply_options_per_service
# ---------------------------------------------------------------------------


def test_options_per_service_sets_servers(tmp_path):
    options = {"src/spec/api.yaml": {"basePath": "/lm/document-grounding"}}
    options_file = tmp_path / "options-per-service.json"
    options_file.write_text(json.dumps(options))

    spec: dict = {}
    apply_options_per_service(spec, options_file, "src/spec/api.yaml")
    assert spec["servers"] == [{"url": "/lm/document-grounding"}]


def test_options_per_service_overwrites_existing_servers(tmp_path):
    options = {"src/spec/api.yaml": {"basePath": "/new/path"}}
    options_file = tmp_path / "options-per-service.json"
    options_file.write_text(json.dumps(options))

    spec: dict = {"servers": [{"url": "http://old-host"}]}
    apply_options_per_service(spec, options_file, "src/spec/api.yaml")
    assert spec["servers"] == [{"url": "/new/path"}]


def test_options_per_service_missing_key_warns_and_does_not_modify(tmp_path, capsys):
    options = {"other/key.yaml": {"basePath": "/other"}}
    options_file = tmp_path / "options-per-service.json"
    options_file.write_text(json.dumps(options))

    spec: dict = {}
    apply_options_per_service(spec, options_file, "src/spec/api.yaml")
    assert "servers" not in spec
    assert "src/spec/api.yaml" in capsys.readouterr().err


def test_options_per_service_no_base_path_does_not_set_servers(tmp_path):
    options = {"src/spec/api.yaml": {"packageName": "my_pkg"}}
    options_file = tmp_path / "options-per-service.json"
    options_file.write_text(json.dumps(options))

    spec: dict = {}
    apply_options_per_service(spec, options_file, "src/spec/api.yaml")
    assert "servers" not in spec

