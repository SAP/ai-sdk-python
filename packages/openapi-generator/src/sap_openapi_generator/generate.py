"""End-to-end OpenAPI generation pipeline for SAP Cloud SDK Python packages.

Mirrors the SAP Cloud SDK JS generator interface:

    sap-generate -i <inputDir> -o <outputDir> [-s <optionsPerService>]

For each spec file found under <inputDir>:
  1. Reads per-service options from options-per-service.json (directoryName, basePath)
  2. Pre-processes the spec (vendor extension resolution, base-path injection)
  3. Invokes openapi-generator-cli via npx
  4. Rewrites bare 'generated.*' imports to the fully-qualified package path
  5. Touches py.typed (httpx template omits it)

options-per-service.json keys are paths relative to <inputDir>. Supported fields:
  directoryName  - output subdirectory under <outputDir> (required)
  basePath       - overrides the servers[0].url baked into Configuration (optional)
  packageName    - ignored (JS npm name, not used in Python)
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

from sap_openapi_generator.preprocess_spec import preprocess

_DEFAULT_CONFIG = Path(__file__).parent.parent.parent / "config" / "python-config.yaml"
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
    """Return the options-per-service.json key for a spec (POSIX relative path from input_dir)."""
    return PurePosixPath(spec_path.relative_to(input_dir)).as_posix()


def _build_opid_flags(mappings_path: Path) -> list[str]:
    if not mappings_path.exists() or not mappings_path.stat().st_size:
        return []
    flags = []
    for line in mappings_path.read_text().splitlines():
        line = line.strip()
        if line:
            flags += ["--operation-id-name-mappings", line]
    return flags


def _fix_numbered_duplicates(output_dir: Path) -> None:
    """Rename fileN.py → file.py when the generator appends a digit to avoid collisions.

    The openapi-generator appends '0', '1', … to a filename when its snake_case
    version collides with another file (e.g. filterconditions0.py vs filter_conditions.py).
    The generated imports reference the un-suffixed name, so we rename the file to match.
    Only renames when the un-suffixed target does not already exist.
    """
    import re
    for numbered in sorted(output_dir.rglob("*.py")):
        m = re.fullmatch(r"(.+?)(0)\.py", numbered.name)
        if not m:
            continue
        canonical = numbered.with_name(m.group(1) + ".py")
        if not canonical.exists():
            numbered.rename(canonical)


def _fix_field_aliases(output_dir: Path) -> None:
    """Replace Field(alias="camelCase") with serialization_alias="camelCase".

    The openapi-generator emits alias= which makes Pydantic use the camelCase name
    as the __init__ parameter, hiding the snake_case field name from type checkers.
    Replacing with serialization_alias= keeps camelCase JSON output while letting
    the __init__ use the natural snake_case field name.
    """
    import re

    ALIAS_RE = re.compile(
        r'(Field\((?:[^"\')\n]|"[^"]*"|\'[^\']*\')*?)(?<![a-z_])alias=(["\'])([^"\']+)\2'
    )

    for py_file in output_dir.rglob("*.py"):
        src = py_file.read_text()
        if 'alias=' not in src:
            continue
        updated = ALIAS_RE.sub(
            lambda m: f"{m.group(1)}serialization_alias={m.group(2)}{m.group(3)}{m.group(2)}",
            src,
        )
        if updated != src:
            py_file.write_text(updated)


def _rewrite_imports(output_dir: Path, package_name: str) -> None:
    for py_file in output_dir.rglob("*.py"):
        src = py_file.read_text()
        updated = (
            src
            .replace("from generated.", f"from {package_name}.")
            .replace("import generated.", f"import {package_name}.")
            .replace("from generated import ", f"from {package_name} import ")
        )
        if updated != src:
            py_file.write_text(updated)


def generate_one(
    spec_path: Path,
    output_dir: Path,
    package_name: str,
    options_path: Path | None = None,
    spec_key: str | None = None,
    config_path: Path | None = None,
) -> None:
    config_path = config_path or _DEFAULT_CONFIG
    leaf = "generated"

    with tempfile.TemporaryDirectory(prefix="sap-openapi-") as tmp:
        tmp_path = Path(tmp)
        processed = tmp_path / "processed.yaml"
        mappings = tmp_path / "mappings.txt"
        gen_tmp = tmp_path / "gen-tmp"

        preprocess(
            input_path=spec_path,
            output_path=processed,
            options_path=options_path,
            spec_key=spec_key,
            mappings_output_path=mappings,
        )

        template_dir = config_path.parent / "custom-templates"

        cmd = [
            "npx", "--yes", "@openapitools/openapi-generator-cli", "generate",
            "-g", "python",
            "-i", str(processed),
            "-o", str(gen_tmp),
            "-c", str(config_path),
            "--additional-properties", f"packageName={leaf}",
        ]
        if template_dir.is_dir():
            cmd += ["--template-dir", str(template_dir)]
        cmd += _build_opid_flags(mappings)

        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            sys.exit(result.returncode)

        generated_src = gen_tmp / leaf
        if not generated_src.exists():
            print(f"ERROR: expected generated output at {generated_src}", file=sys.stderr)
            sys.exit(1)

        if output_dir.exists():
            shutil.rmtree(output_dir)
        shutil.move(str(generated_src), str(output_dir))

    _fix_numbered_duplicates(output_dir)
    _fix_field_aliases(output_dir)
    _rewrite_imports(output_dir, package_name)
    (output_dir / "py.typed").touch()


def generate(
    input_path: Path,
    output_dir: Path,
    options_per_service_path: Path | None = None,
    config_path: Path | None = None,
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

        service_output = output_dir / directory_name
        # Derive the Python import path from directoryName (slashes → dots)
        python_package_name = directory_name.replace("/", ".")

        generate_one(
            spec_path=spec,
            output_dir=service_output,
            package_name=python_package_name,
            options_path=options_per_service_path,
            spec_key=key,
            config_path=config_path,
        )
        print(f"Generated: {key} → {service_output}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Python API clients from OpenAPI specs (SAP Cloud SDK style)."
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
    parser.add_argument(
        "--config", type=Path, default=None,
        help=f"openapi-generator config YAML (default: {_DEFAULT_CONFIG})",
    )
    args = parser.parse_args()
    generate(
        input_path=args.input,
        output_dir=args.outputDir,
        options_per_service_path=args.optionsPerService,
        config_path=args.config,
    )


if __name__ == "__main__":
    main()
