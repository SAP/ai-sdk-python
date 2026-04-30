# Security Remediation Guide

This guide covers the findings from `SECURITY_AUDIT_REPORT.md` and provides step-by-step remediation.

## Issue 1: Remove Internal Infrastructure URLs (Priority: HIGH)

### Location
**File**: `scripts/prompt_template_registry_cleanup.py`  
**Lines**: 8-9

### Current Code
```python
# os.environ["AICORE_AUTH_URL"] = "https://mlfwdftest.authentication.sap.hana.ondemand.com/oauth/token"
# os.environ["AICORE_BASE_URL"] = "https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2"
```

### Problem
- Exposes internal SAP test infrastructure URLs
- Could allow attackers to probe internal systems
- Violates security best practice of not exposing infrastructure details

### Solutions (Choose One)

#### Option A: Generic Examples (Recommended)
Replace with generic placeholders that don't expose infrastructure:

```python
# os.environ["AICORE_AUTH_URL"] = "https://your-aicore-auth-url/oauth/token"
# os.environ["AICORE_BASE_URL"] = "https://your-aicore-api-url/v2"
```

#### Option B: Point to Documentation
Replace with reference to documentation:

```python
# Set these environment variables to your AI Core instance URLs.
# See README.md for configuration instructions.
# os.environ["AICORE_AUTH_URL"] = "<your-auth-url>/oauth/token"
# os.environ["AICORE_BASE_URL"] = "<your-api-url>/v2"
```

#### Option C: Move to Documentation
Remove from code entirely and document in `README.md` or `CONTRIBUTING.md`.

---

## Issue 2: Dependency Security Scan (Priority: HIGH)

### Steps to Execute

1. **Install security scanning tools** (if not already installed):
```bash
pip install safety bandit
```

2. **Check Python dependencies for vulnerabilities**:
```bash
# Check production dependencies
safety check -r requirements.txt --json > dependency_report.json

# Check test dependencies
safety check -r requirements-test.txt --json >> dependency_report.json
```

3. **Run Bandit for code security issues**:
```bash
# Scan main source code
bandit -r gen_ai_hub/ -f json -o bandit_report.json

# Scan scripts
bandit -r scripts/ -f json -o bandit_scripts_report.json
```

4. **Review Reports**:
   - Open `dependency_report.json` and check for any CVEs marked as "CRITICAL" or "HIGH"
   - Open `bandit_report.json` and check "SEVERITY: HIGH" issues
   - For each finding, decide: Ignore, Upgrade, or Patch

5. **Update Vulnerable Dependencies**:
```bash
# Example: If Pillow has security issues
pip install --upgrade Pillow

# Update requirements.txt
pip freeze > requirements.txt
```

6. **Pin Specific Versions**:
   - For critical dependencies, use `==` instead of `>=` to prevent unexpected updates:
   
   **Before**:
   ```
   pillow
   httpx>=0.27.0
   ```
   
   **After**:
   ```
   pillow==11.0.0
   httpx==0.27.2
   ```

---

## Issue 3: Review Dockerfiles and Jenkinsfile (Priority: HIGH)

### Steps to Execute

1. **Check Dockerfiles for hardcoded secrets**:
```bash
# Search for patterns
grep -r "password\|secret\|token\|key\|credential" Dockerfile*
grep -r "ENV.*=.*[a-zA-Z0-9]{20,}" Dockerfile*
```

2. **Check Jenkinsfile for exposed credentials**:
```bash
grep -r "credentials\|secret\|password" Jenkinsfile
```

3. **If secrets found**:
   - Remove from Dockerfiles
   - Use Docker build arguments (`--build-arg`) or secrets management
   - Use Jenkins credentials plugin instead of hardcoding

---

## Issue 4: Verify Git History (Priority: MEDIUM)

### Steps to Execute

1. **Check recent commits for secrets**:
```bash
# See recent commits
git log --oneline -20

# Check for common secret patterns in commit messages
git log --all --source --grep="password\|secret\|token" -i
```

2. **If old secrets found in history**:
   - Use BFG Repo-Cleaner: `bfg --replace-text sensitive-data.txt`
   - Or use `git filter-branch` with caution
   - Force-push to repository only if you have full control

---

## Issue 5: Set Up Pre-Commit Hooks (Priority: MEDIUM)

### Install Pre-Commit Framework
```bash
pip install pre-commit
```

### Create `.pre-commit-config.yaml`
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: detect-private-key
      - id: detect-secrets
  
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

### Initialize Pre-Commit
```bash
pre-commit install
pre-commit run --all-files
```

---

## Issue 6: Create Security Policy (Priority: LOW)

### Create `SECURITY.md` in Repository Root
```markdown
# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in this project, please email security@example.com 
instead of using the public issue tracker.

**Do not** disclose the vulnerability publicly until we've had time to investigate and patch.

## Supported Versions

This project supports the following versions with security updates:

| Version | Status |
|---------|--------|
| 1.x     | Active Support |
| 0.x     | No longer supported |

## Security Measures

- All dependencies are regularly scanned for vulnerabilities
- Code is reviewed for security issues before release
- [See CONTRIBUTING.md for development guidelines](/CONTRIBUTING.md)
```

---

## Step-by-Step Remediation Checklist

- [ ] **HIGH PRIORITY**
  - [ ] Remove internal URLs from `scripts/prompt_template_registry_cleanup.py`
  - [ ] Run `safety check` on all requirements files
  - [ ] Review and fix any HIGH/CRITICAL vulnerabilities
  - [ ] Check Dockerfiles for hardcoded secrets
  - [ ] Review Jenkinsfile for exposed credentials

- [ ] **MEDIUM PRIORITY**
  - [ ] Verify recent git history for secrets
  - [ ] Set up `.pre-commit-config.yaml` with secret detection
  - [ ] Enable branch protection rules (require reviews)

- [ ] **LOW PRIORITY**
  - [ ] Create `SECURITY.md` with vulnerability disclosure policy
  - [ ] Enable GitHub Dependabot (Settings → Code security)
  - [ ] Document security practices in `CONTRIBUTING.md`

---

## Validation

After applying fixes, verify with:

```bash
# 1. No internal URLs exposed
grep -r "mlfwdftest\|internalprod\|sap.hana.ondemand" . --include="*.py" --include="Dockerfile*"

# 2. No obvious secrets
grep -r "password\|secret\|token" scripts/ --include="*.py" | grep -v "test\|mock\|example\|placeholder"

# 3. Dependencies are clean
safety check -r requirements.txt
safety check -r requirements-test.txt

# 4. Code quality check
pylint gen_ai_hub/ --fail-under=8.0 2>/dev/null | head -20
```

---

## Timeline for Release

**Recommended Timeline**:
1. **Week 1**: Fix HIGH priority items (2-4 hours)
2. **Week 2**: Address MEDIUM priority items (1-2 hours)
3. **Week 3**: Final review and LOW priority items (1 hour)
4. **Before Public Release**: Final security audit + legal review

---

## Questions?

For more details on any of these issues, refer back to `SECURITY_AUDIT_REPORT.md`.

