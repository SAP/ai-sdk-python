#!/usr/bin/env python3
import sys

package, version, body = sys.argv[1], sys.argv[2], sys.argv[3]
path = f"packages/{package}/RELEASE_NOTES.md"
content = open(path).read()
sections = content.split("## ")
match = next((s for s in sections if s.startswith(version)), None)

if not match:
    sys.exit(f"No changelog entry found for version {version}")

open(path, "w").write(content.replace(match, f"{version}\n\n{body.strip()}\n\n"))
