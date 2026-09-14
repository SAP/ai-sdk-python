#!/usr/bin/env python3
import re
import sys

package, version, body = sys.argv[1], sys.argv[2], sys.argv[3]
path = f"packages/{package}/RELEASE_NOTES.md"
content = open(path).read()
# Split on level-2 headers only ("## " at line start), not "### " subheaders.
sections = re.split(r"^## ", content, flags=re.MULTILINE)


def matches(section: str) -> bool:
    # Header is commitizen-generated ("gen-v7.3.0 (2026-09-07)"); tolerate a bare
    # version too ("7.3.0") for any hand-written entries.
    head = section.split(None, 1)[0] if section.split() else ""
    return head == version or head.endswith(f"-v{version}")


match = next((s for s in sections if matches(s)), None)

if not match:
    sys.exit(f"No changelog entry found for version {version}")

# Keep the generated header line, replace only the body with the published notes.
header = match.split("\n", 1)[0]
open(path, "w").write(content.replace(f"## {match}", f"## {header}\n\n{body.strip()}\n\n"))
