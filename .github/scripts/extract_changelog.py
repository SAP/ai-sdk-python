#!/usr/bin/env python3
import sys

package, version = sys.argv[1], sys.argv[2]
sections = open(f"packages/{package}/RELEASE_NOTES.md").read().split("## ")
match = next((s for s in sections if s.startswith(version)), None)

if not match:
    sys.exit(f"No changelog entry found for version {version}")
print(match[len(version):].strip())
