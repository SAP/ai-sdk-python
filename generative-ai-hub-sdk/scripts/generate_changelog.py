#!/usr/bin/env python3
"""
Generate changelog entries from git commits using conventional commits format.
Commits should follow the format: type(scope): description
Types: feat, fix, docs, style, refactor, perf, test, chore, ci, build
"""

import subprocess
import re
from datetime import datetime
from typing import Dict, List, Tuple


def get_git_commits(since_tag: str = None) -> List[str]:
    """Get git commits since the last tag or a specific tag."""
    try:
        if since_tag:
            cmd = ['git', 'log', f'{since_tag}..HEAD', '--oneline', '--pretty=format:%B']
        else:
            # Get commits since the last tag
            cmd = ['git', 'log', '--oneline', '--decorate', '--all']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')
            
            # Find the last tag
            tag_line = None
            for line in lines:
                if 'tag:' in line:
                    tag_line = line
                    break
            
            if tag_line:
                # Extract tag name
                tag_match = re.search(r'tag: (v[\d.]+)', tag_line)
                if tag_match:
                    last_tag = tag_match.group(1)
                    cmd = ['git', 'log', f'{last_tag}..HEAD', '--pretty=format:%B%n---COMMIT---']
            else:
                cmd = ['git', 'log', '--pretty=format:%B%n---COMMIT---']
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        commits = result.stdout.strip().split('---COMMIT---')
        return [c.strip() for c in commits if c.strip()]
    except subprocess.CalledProcessError as e:
        print(f"Error getting git commits: {e}")
        return []


def parse_conventional_commit(message: str) -> Tuple[str, str, str]:
    """
    Parse a conventional commit message.
    Returns: (type, scope, description)
    """
    # First line is the commit message
    first_line = message.split('\n')[0]
    
    # Pattern: type(scope): description or type: description
    pattern = r'^(feat|fix|docs|style|refactor|perf|test|chore|ci|build)(?:\(([^)]*)\))?: (.*)$'
    match = re.match(pattern, first_line)
    
    if match:
        commit_type = match.group(1)
        scope = match.group(2) or ''
        description = match.group(3)
        return commit_type, scope, description
    
    return None, None, first_line


def group_commits(commits: List[str]) -> Dict[str, List[Tuple[str, str]]]:
    """Group commits by type."""
    grouped = {
        'features': [],
        'bugfixes': [],
        'docs': [],
        'other': []
    }
    
    for commit in commits:
        commit_type, scope, description = parse_conventional_commit(commit)
        
        if commit_type == 'feat':
            if scope:
                grouped['features'].append((scope, description))
            else:
                grouped['features'].append(('', description))
        elif commit_type == 'fix':
            if scope:
                grouped['bugfixes'].append((scope, description))
            else:
                grouped['bugfixes'].append(('', description))
        elif commit_type == 'docs':
            grouped['docs'].append(('', description))
        else:
            if commit_type:
                grouped['other'].append((commit_type, description))
    
    return grouped


def generate_changelog(version: str, grouped_commits: Dict[str, List[Tuple[str, str]]]) -> str:
    """Generate a changelog entry."""
    changelog = f"## {version}\n\n"
    
    if grouped_commits['features']:
        changelog += "### Features\n"
        for scope, desc in grouped_commits['features']:
            if scope:
                changelog += f"- ({scope}) {desc}\n"
            else:
                changelog += f"- {desc}\n"
        changelog += "\n"
    
    if grouped_commits['bugfixes']:
        changelog += "### Bugfixes\n"
        for scope, desc in grouped_commits['bugfixes']:
            if scope:
                changelog += f"- ({scope}) {desc}\n"
            else:
                changelog += f"- {desc}\n"
        changelog += "\n"
    
    if grouped_commits['docs']:
        changelog += "### Documentation\n"
        for _, desc in grouped_commits['docs']:
            changelog += f"- {desc}\n"
        changelog += "\n"
    
    if grouped_commits['other']:
        changelog += "### Other Changes\n"
        for commit_type, desc in grouped_commits['other']:
            changelog += f"- ({commit_type}) {desc}\n"
        changelog += "\n"
    
    return changelog.rstrip() + "\n"


def update_release_notes(version: str, new_entry: str, release_notes_file: str = 'RELEASE_NOTES.md'):
    """Prepend the new changelog entry to RELEASE_NOTES.md."""
    try:
        with open(release_notes_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    except FileNotFoundError:
        existing_content = "# Release Notes\n\n"
    
    # Ensure there's a header
    if not existing_content.startswith('# Release Notes'):
        existing_content = '# Release Notes\n\n' + existing_content
    
    # Split header from rest
    parts = existing_content.split('\n', 1)
    header = parts[0] + '\n'
    rest = parts[1] if len(parts) > 1 else ''
    
    # Prepend new entry
    new_content = header + '\n' + new_entry + '\n' + rest
    
    with open(release_notes_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated {release_notes_file}")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate_changelog.py <version> [--update]")
        print("  <version>: Version number (e.g., 6.9.0)")
        print("  --update: Update RELEASE_NOTES.md file")
        sys.exit(1)
    
    version = sys.argv[1]
    should_update = '--update' in sys.argv
    
    # Get commits since last tag
    commits = get_git_commits()
    
    if not commits:
        print(f"No commits found since last tag")
        return
    
    # Group and parse commits
    grouped = group_commits(commits)
    
    # Generate changelog
    changelog = generate_changelog(version, grouped)
    
    print("Generated changelog:")
    print(changelog)
    
    if should_update:
        update_release_notes(version, changelog)
    else:
        print("\nRun with --update flag to update RELEASE_NOTES.md")


if __name__ == '__main__':
    main()
