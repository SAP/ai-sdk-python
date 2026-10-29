"""End-to-end generation pipeline using the custom Java `sap-python` generator.

Mirrors the sap-generate / sap-kiota-generate interface so all generators are
interchangeable:

    sap-generate-java -i <inputDir> -o <outputDir> [-s <optionsPerService>]

Unlike `sap-openapi-generator`, this driver does NO spec pre-processing and NO code
post-processing: the vendor-extension resolution (x-sap-cloud-sdk-api-name,
x-sap-cloud-sdk-operation-name), basePath injection, and the `serialization_alias`
rewrite all live inside the custom Java codegen `SapPythonCodegen` (generator name
`sap-python`). This driver only:

  1. Reads per-service options from options-per-service.json (directoryName, basePath)
  2. Invokes the custom generator via `java -cp <custom.jar>:<deps> OpenAPIGenerator generate`
  3. Moves the dotted-package subtree into place under <outputDir>/<directoryName>/
  4. Touches py.typed (the httpx template omits it)

The custom generator jar is built by `mvn package` in this package (see the Makefile);
its classpath (jar + copied runtime dependencies) lives under target/.

options-per-service.json keys are paths relative to <inputDir>. Supported fields:
  directoryName  - output subdirectory under <outputDir> (required); also the dotted packageName
  basePath       - overrides the servers[0].url baked into Configuration (optional)
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

_PKG_ROOT = Path(__file__).parent.parent.parent
_DEFAULT_CONFIG = _PKG_ROOT / "config" / "python-config.yaml"
_TEMPLATE_DIR = _PKG_ROOT / "src" / "main" / "resources" / "sap-python"
_JAR = _PKG_ROOT / "target" / "sap-python-openapi-generator.jar"
_DEPS_DIR = _PKG_ROOT / "target" / "dependency"

_GENERATOR_NAME = "sap-python"
_MAIN_CLASS = "org.openapitools.codegen.OpenAPIGenerator"

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


def _classpath() -> str:
    if not _JAR.exists():
        print(
            f"ERROR: custom generator jar not found at {_JAR}.\n"
            f"Build it first:  make -C {_PKG_ROOT} build  (runs `mvn package`).",
            file=sys.stderr,
        )
        sys.exit(1)
    # <jar>:<target/dependency/*>  — the dependency glob is expanded by the JVM.
    return f"{_JAR}:{_DEPS_DIR}/*"


def generate_one(
    spec_path: Path,
    output_dir: Path,
    package_name: str,
    base_path: str | None = None,
    config_path: Path | None = None,
) -> None:
    config_path = config_path or _DEFAULT_CONFIG

    with tempfile.TemporaryDirectory(prefix="sap-java-") as tmp:
        gen_tmp = Path(tmp) / "gen-tmp"

        additional = f"packageName={package_name}"
        if base_path:
            additional += f",basePath={base_path}"

        cmd = [
            "java", "-cp", _classpath(),
            _MAIN_CLASS, "generate",
            "-g", _GENERATOR_NAME,
            "-i", str(spec_path),
            "-o", str(gen_tmp),
            "-c", str(config_path),
            "--additional-properties", additional,
        ]
        if _TEMPLATE_DIR.is_dir():
            cmd += ["-t", str(_TEMPLATE_DIR)]

        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            sys.exit(result.returncode)

        # With a dotted packageName the generator nests the source under the matching path
        # (e.g. gen_ai_hub/context_registry/generated). Follow it down; the surrounding
        # scaffold stays in temp.
        generated_src = gen_tmp / Path(*package_name.split("."))
        if not generated_src.exists():
            print(f"ERROR: expected generated output at {generated_src}", file=sys.stderr)
            sys.exit(1)

        if output_dir.exists():
            shutil.rmtree(output_dir)
        shutil.move(str(generated_src), str(output_dir))

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
            base_path=opts.get("basePath"),
            config_path=config_path,
        )
        print(f"Generated (sap-python/java): {key} → {service_output}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Python API clients from OpenAPI specs using the custom Java sap-python generator."
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
