"""End-to-end OpenAPI generation pipeline for SAP Cloud SDK Python packages.

Runs the full pipeline in one command:
  1. Pre-process the spec (vendor extension resolution, base-path injection)
  2. Invoke openapi-generator-cli via npx
  3. Rewrite bare `generated.*` imports to a fully-qualified package path
  4. Touch py.typed (httpx template omits it)

Usage:
    sap-generate \\
        --spec path/to/api.yaml \\
        --output path/to/output/dir \\
        --package-name my_pkg.sub.generated \\
        [--options path/to/options-per-service.json] \\
        [--spec-key src/spec/api.yaml] \\
        [--config path/to/python-config.yaml]
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from sap_openapi_generator.preprocess_spec import preprocess

_DEFAULT_CONFIG = Path(__file__).parent.parent.parent / "config" / "python-config.yaml"


def _build_opid_flags(mappings_path: Path) -> list[str]:
    if not mappings_path.exists() or not mappings_path.stat().st_size:
        return []
    flags = []
    for line in mappings_path.read_text().splitlines():
        line = line.strip()
        if line:
            flags += ["--operation-id-name-mappings", line]
    return flags


def _rewrite_imports(output_dir: Path, package_name: str) -> None:
    """Rewrite bare 'generated' imports to the fully-qualified package path."""
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


def generate(
    spec_path: Path,
    output_dir: Path,
    package_name: str,
    options_path: Path | None = None,
    spec_key: str | None = None,
    config_path: Path | None = None,
) -> None:
    config_path = config_path or _DEFAULT_CONFIG
    # The leaf package name used internally by the generator (always "generated")
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

        cmd = [
            "npx", "--yes", "@openapitools/openapi-generator-cli", "generate",
            "-g", "python",
            "-i", str(processed),
            "-o", str(gen_tmp),
            "-c", str(config_path),
            "--additional-properties", f"packageName={leaf}",
        ]
        cmd += _build_opid_flags(mappings)

        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            sys.exit(result.returncode)

        generated_src = gen_tmp / leaf
        if not generated_src.exists():
            print(
                f"ERROR: expected generated output at {generated_src} but it was not found.",
                file=sys.stderr,
            )
            sys.exit(1)

        if output_dir.exists():
            shutil.rmtree(output_dir)
        shutil.move(str(generated_src), str(output_dir))

    _rewrite_imports(output_dir, package_name)
    (output_dir / "py.typed").touch()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the full SAP OpenAPI generation pipeline."
    )
    parser.add_argument("--spec", required=True, type=Path, help="Source spec file (.yaml or .json)")
    parser.add_argument(
        "--output", required=True, type=Path,
        help="Output directory for generated Python files",
    )
    parser.add_argument(
        "--package-name", required=True,
        help="Fully-qualified Python package name for import rewriting (e.g. my_pkg.sub.generated)",
    )
    parser.add_argument(
        "--options", type=Path, default=None,
        help="Path to options-per-service.json",
    )
    parser.add_argument(
        "--spec-key", default=None,
        help="Key in options-per-service.json for this spec (e.g. 'src/spec/api.yaml')",
    )
    parser.add_argument(
        "--config", type=Path, default=None,
        help=f"openapi-generator config YAML (default: {_DEFAULT_CONFIG})",
    )
    args = parser.parse_args()
    generate(
        spec_path=args.spec,
        output_dir=args.output,
        package_name=args.package_name,
        options_path=args.options,
        spec_key=args.spec_key,
        config_path=args.config,
    )


if __name__ == "__main__":
    main()
