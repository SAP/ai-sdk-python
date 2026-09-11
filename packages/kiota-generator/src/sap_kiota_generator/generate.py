"""End-to-end Kiota generation pipeline for SAP Cloud SDK Python packages.

Mirrors the sap-generate interface so both generators are interchangeable:

    sap-kiota-generate -i <inputDir> -o <outputDir> [-s <optionsPerService>]

For each spec file found under <inputDir>:
  1. Reads per-service options from options-per-service.json (directoryName, basePath,
     and a nested "kiota" object with className / namespaceName)
  2. Pre-processes the spec (vendor extension resolution, base-path injection) via
     the shared sap_openapi_generator.preprocess_spec module
  3. Invokes the Kiota CLI (must be on PATH: `kiota generate -l python ...`)
  4. Moves generated output into place under <outputDir>/<directoryName>/
  5. Touches py.typed

options-per-service.json keys are paths relative to <inputDir>. Supported fields:
  directoryName  - output subdirectory under <outputDir> (required)
  basePath       - overrides the servers[0].url baked into Configuration (optional)
  kiota          - nested object with Kiota-specific options:
    className      - root client class name (default: ApiClient)
    namespaceName  - Python namespace / module prefix (default: generated)
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

from sap_openapi_generator.preprocess_spec import preprocess, load_spec, dump_spec

_SPEC_EXTENSIONS = {".yaml", ".yml", ".json"}
_EXCLUDED_FILENAMES = {"options-per-service.json"}


def _find_specs(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    return sorted(
        p for p in input_path.rglob("*")
        if p.suffix in _SPEC_EXTENSIONS and p.is_file() and p.name not in _EXCLUDED_FILENAMES
    )


def _load_options_per_service(options_path: Path) -> dict:
    if options_path.is_dir():
        options_path = options_path / "options-per-service.json"
    if not options_path.exists():
        return {}
    return json.loads(options_path.read_text())


def _service_key(spec_path: Path, input_dir: Path) -> str:
    return PurePosixPath(spec_path.relative_to(input_dir)).as_posix()


def _strip_security(spec_path: Path) -> None:
    """Remove securitySchemes and security fields from a preprocessed spec.

    Kiota's OpenAPI parser enforces RFC-3986 URI validity on OAuth flow URLs.
    SAP specs often contain placeholder values (e.g. tokenUrl with parenthesised
    template variables) that are invalid URIs. Since auth is handled by the SAP
    wrapper client — not by Kiota — stripping these fields is safe.
    """
    spec = load_spec(spec_path)
    spec.pop("security", None)
    components = spec.get("components", {})
    components.pop("securitySchemes", None)
    if not components:
        spec.pop("components", None)
    # Also remove per-operation security overrides
    for path_item in spec.get("paths", {}).values():
        if not isinstance(path_item, dict):
            continue
        for method in ("get", "post", "put", "delete", "patch", "options", "head", "trace"):
            op = path_item.get(method)
            if isinstance(op, dict):
                op.pop("security", None)
    dump_spec(spec, spec_path)


def generate_one(
    spec_path: Path,
    output_dir: Path,
    kiota_class_name: str,
    kiota_namespace: str,
    options_path: Path | None = None,
    spec_key: str | None = None,
) -> None:
    with tempfile.TemporaryDirectory(prefix="sap-kiota-") as tmp:
        tmp_path = Path(tmp)
        processed = tmp_path / "processed.yaml"
        gen_tmp = tmp_path / "gen-tmp"

        preprocess(
            input_path=spec_path,
            output_path=processed,
            options_path=options_path,
            spec_key=spec_key,
        )

        # Kiota's OpenAPI parser rejects invalid URIs in securitySchemes (e.g. placeholder
        # tokenUrl values like "https://(subdomain).auth.(host)/token"). Strip security
        # definitions entirely — auth is handled by the SAP wrapper client, not by Kiota.
        _strip_security(processed)

        cmd = [
            "kiota", "generate",
            "-l", "python",
            "-d", str(processed),
            "-o", str(gen_tmp),
            "-c", kiota_class_name,
            "-n", kiota_namespace,
            "--clean-output",
            "--exclude-backward-compatible",
        ]

        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            sys.exit(result.returncode)

        if not gen_tmp.exists():
            print(f"ERROR: expected generated output at {gen_tmp}", file=sys.stderr)
            sys.exit(1)

        if output_dir.exists():
            shutil.rmtree(output_dir)
        shutil.copytree(str(gen_tmp), str(output_dir))

    (output_dir / "py.typed").touch()


def generate(
    input_path: Path,
    output_dir: Path,
    options_per_service_path: Path | None = None,
) -> None:
    specs = _find_specs(input_path)
    if not specs:
        print(f"ERROR: no spec files found under {input_path}", file=sys.stderr)
        sys.exit(1)

    input_dir = input_path if input_path.is_dir() else input_path.parent
    service_options = _load_options_per_service(options_per_service_path) if options_per_service_path else {}

    for spec in specs:
        key = _service_key(spec, input_dir)
        opts = service_options.get(key, {})

        directory_name = opts.get("directoryName")
        if not directory_name:
            print(
                f"ERROR: no 'directoryName' for spec '{key}' in options-per-service.json.",
                file=sys.stderr,
            )
            sys.exit(1)

        kiota_opts = opts.get("kiota", {})
        kiota_class_name = kiota_opts.get("className", "ApiClient")
        # kiota.directoryName overrides the top-level directoryName for the Kiota output
        kiota_directory = kiota_opts.get("directoryName", directory_name)
        # Derive a default namespace from the kiota directory if not specified
        default_namespace = kiota_directory.replace("/", ".")
        kiota_namespace = kiota_opts.get("namespaceName", default_namespace)

        service_output = output_dir / kiota_directory

        generate_one(
            spec_path=spec,
            output_dir=service_output,
            kiota_class_name=kiota_class_name,
            kiota_namespace=kiota_namespace,
            options_path=options_per_service_path,
            spec_key=key,
        )
        print(f"Generated (kiota): {key} → {service_output}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Python API clients from OpenAPI specs using Kiota (SAP Cloud SDK style)."
    )
    parser.add_argument(
        "-i", "--input", required=True, type=Path,
        help="Input directory or spec file (.yaml/.yml/.json)",
    )
    parser.add_argument(
        "-o", "--outputDir", required=True, type=Path,
        help="Output base directory; each service is placed in a subdirectory per directoryName",
    )
    parser.add_argument(
        "-s", "--optionsPerService", type=Path, default=None,
        help="Path to options-per-service.json (or directory containing it)",
    )
    args = parser.parse_args()
    generate(
        input_path=args.input,
        output_dir=args.outputDir,
        options_per_service_path=args.optionsPerService,
    )


if __name__ == "__main__":
    main()
