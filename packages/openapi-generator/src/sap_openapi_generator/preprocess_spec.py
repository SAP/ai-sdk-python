"""Pre-process an OpenAPI spec to apply SAP Cloud SDK vendor extensions.

Replicates the Java ApiClassNameFieldPreprocessor and MethodNameFieldPreprocessor
logic so the standard openapi-generator-cli sees a clean, normalized spec.

Two vendor extensions are handled:

  x-sap-cloud-sdk-api-name:
    Sets operation tags[0] to the given value (trailing "Api" suffix stripped).
    Cascade resolution: operation level > path level > root level.

  x-sap-cloud-sdk-operation-name:
    Overwrites the operation's operationId with the given value.
    The generator then derives the Python method name from that operationId.

Additionally, an options-per-service.json file (same format as the JS SDK) can be
supplied to embed service-level config such as basePath into the spec servers list:

  options-per-service.json format:
    { "<spec-key>": { "basePath": "/lm/document-grounding", "packageName": "..." } }

  Effect: spec["servers"] is replaced with [{"url": basePath}] so the generator
  bakes it into Configuration._base_path.

Usage:
    sap-preprocess-spec --input path/to/spec.yaml --output path/to/processed.yaml
    sap-preprocess-spec --input api.yaml --output out.yaml \\
        --options options-per-service.json --spec-key src/spec/api.yaml
    python -m sap_openapi_generator.preprocess_spec --input ... --output ...
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

import yaml

HTTP_METHODS = ("get", "post", "put", "delete", "patch", "options", "head", "trace")


def strip_api_suffix(name: str) -> str:
    """Remove a trailing literal 'Api' suffix (case-sensitive, matching Java behavior)."""
    return name[:-3] if name.endswith("Api") else name


def apply_api_name_extension(spec: dict) -> None:
    """Set operation tags[0] based on x-sap-cloud-sdk-api-name.

    Cascade resolution: operation level > path level > root level.
    Strips a trailing literal 'Api' suffix from the resolved name before setting.
    """
    root_name = spec.get("x-sap-cloud-sdk-api-name")
    for path_item in spec.get("paths", {}).values():
        if not isinstance(path_item, dict):
            continue
        path_name = path_item.get("x-sap-cloud-sdk-api-name")
        for method in HTTP_METHODS:
            op = path_item.get(method)
            if not isinstance(op, dict):
                continue
            effective = op.get("x-sap-cloud-sdk-api-name") or path_name or root_name
            if effective:
                op["tags"] = [strip_api_suffix(effective)]


def _snake_case(name: str) -> str:
    """Convert camelCase or PascalCase to snake_case."""
    import re
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def apply_operation_name_extension(spec: dict) -> dict:
    """Overwrite operationId with x-sap-cloud-sdk-operation-name when present.

    When two operations in different tags share the same desired name (e.g. both
    VectorApi and RetrievalApi want a method called "search"), the OAS spec requires
    globally unique operationIds. The operationId is scoped to tag+name to satisfy
    this, and operationIdNameMappings are returned so the generator renames the
    Python method back to the desired short name within its class.

    Returns an operationIdNameMappings dict (may be empty).
    """
    # First pass: collect all desired (tag, name) pairs to detect cross-tag collisions
    desired: list[tuple[dict, str, str]] = []  # (op_dict, desired_name, tag)
    for path_item in spec.get("paths", {}).values():
        if not isinstance(path_item, dict):
            continue
        for method in HTTP_METHODS:
            op = path_item.get(method)
            if not isinstance(op, dict):
                continue
            override = op.get("x-sap-cloud-sdk-operation-name")
            if override:
                tag = (op.get("tags") or ["default"])[0]
                desired.append((op, override, tag))

    # Detect which names appear more than once (across different tags)
    from collections import Counter
    name_counts = Counter(name for _, name, _ in desired)
    duplicates = {name for name, count in name_counts.items() if count > 1}

    mappings: dict[str, str] = {}
    for op, name, tag in desired:
        if name in duplicates:
            # Scope the operationId: snake_case(tag) + "_" + snake_case(name)
            scoped = f"{_snake_case(tag)}_{_snake_case(name)}"
            op["operationId"] = scoped
            # Map scoped → desired so the generator uses the desired method name
            mappings[scoped] = _snake_case(name)
        else:
            op["operationId"] = name

    return mappings

def apply_options_per_service(spec: dict, options_path: Path, spec_key: str) -> None:
    """Inject service options from an options-per-service.json file into the spec.

    Replaces spec["servers"] with a single entry whose URL is the basePath from
    the options file. This causes the generator to bake basePath into
    Configuration._base_path rather than leaving it as "http://localhost".
    """
    with options_path.open() as f:
        options: dict = json.load(f)

    service_opts = options.get(spec_key)
    if not service_opts:
        print(
            f"WARNING: spec key '{spec_key}' not found in {options_path}. "
            "No service options applied.",
            file=sys.stderr,
        )
        return

    base_path = service_opts.get("basePath")
    if base_path:
        spec["servers"] = [{"url": base_path}]


def validate_unique_operation_ids(spec: dict) -> None:
    """Exit with an error if duplicate operationIds exist after applying overrides."""
    seen: dict[str, str] = {}
    for path, path_item in spec.get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue
        for method in HTTP_METHODS:
            op = path_item.get(method)
            if not isinstance(op, dict):
                continue
            op_id = op.get("operationId")
            if not op_id:
                continue
            if op_id in seen:
                print(
                    f"ERROR: Duplicate operationId '{op_id}' at "
                    f"'{method.upper()} {path}' conflicts with '{seen[op_id]}'.",
                    file=sys.stderr,
                )
                sys.exit(1)
            seen[op_id] = f"{method.upper()} {path}"


def load_spec(path: Path) -> dict:
    with path.open() as f:
        if path.suffix == ".json":
            return json.load(f)
        return yaml.safe_load(f)


def dump_spec(spec: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        if path.suffix == ".json":
            json.dump(spec, f, indent=2)
        else:
            yaml.dump(spec, f, allow_unicode=True, sort_keys=False)


def preprocess(
    input_path: Path,
    output_path: Path,
    options_path: Path | None = None,
    spec_key: str | None = None,
    mappings_output_path: Path | None = None,
) -> None:
    spec = copy.deepcopy(load_spec(input_path))
    if options_path:
        apply_options_per_service(spec, options_path, spec_key or "")
    apply_api_name_extension(spec)
    mappings = apply_operation_name_extension(spec)
    validate_unique_operation_ids(spec)
    dump_spec(spec, output_path)
    if mappings_output_path:
        mappings_output_path.parent.mkdir(parents=True, exist_ok=True)
        # Write as newline-separated key=value pairs for --operation-id-name-mappings.
        lines = "\n".join(
            f"{scoped}={desired}"
            for scoped, desired in sorted(mappings.items())
        )
        mappings_output_path.write_text(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pre-process an OpenAPI spec to apply SAP Cloud SDK vendor extensions."
    )
    parser.add_argument("--input", required=True, type=Path, help="Source spec file (.yaml or .json)")
    parser.add_argument("--output", required=True, type=Path, help="Output path for processed spec")
    parser.add_argument(
        "--options",
        type=Path,
        default=None,
        help="Path to options-per-service.json (JS SDK format)",
    )
    parser.add_argument(
        "--spec-key",
        default=None,
        help="Key in options-per-service.json selecting this spec's options (e.g. 'src/spec/api.yaml')",
    )
    parser.add_argument(
        "--mappings-output",
        type=Path,
        default=None,
        help="Optional path to write operationIdNameMappings YAML fragment (for --config merging)",
    )
    args = parser.parse_args()
    preprocess(args.input, args.output, args.options, args.spec_key, args.mappings_output)


if __name__ == "__main__":
    main()
