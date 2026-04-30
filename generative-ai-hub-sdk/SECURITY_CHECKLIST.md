# Pre-Release Security Checklist

**Repository**: ai-sdk-python  
**Audit Date**: April 15, 2026  
**Target Release**: [Insert your target date]

Use this checklist to track progress on security fixes before public release.

---

## 🔴 CRITICAL (Must Complete Before Release)

- [ ] **Remove internal infrastructure URLs** ✅ DONE
  - [x] Fixed `scripts/prompt_template_registry_cleanup.py`
  - [ ] Review other scripts for similar patterns
  - **Status**: Ready

- [ ] **Run dependency security scan**
  ```bash
  pip install safety
  safety check -r requirements.txt
  safety check -r requirements-test.txt
  ```
  - [ ] Scan completed
  - [ ] No HIGH/CRITICAL CVEs found
  - [ ] Document findings in [DEPENDENCY_SCAN_RESULTS.txt](#)

- [ ] **Review Dockerfiles for hardcoded secrets**
  ```bash
  grep -r "password\|secret\|token\|key\|credential" Dockerfile*
  grep -E "ENV.*=.*[a-zA-Z0-9]{20,}" Dockerfile*
  ```
  - [ ] Audit completed
  - [ ] No secrets found or removed
  - [ ] Document review in [DOCKERFILE_SECURITY_REVIEW.txt](#)

- [ ] **Review Jenkinsfile for exposed credentials**
  ```bash
  grep -r "credentials\|secret\|password" Jenkinsfile
  ```
  - [ ] Audit completed
  - [ ] No exposed credentials
  - [ ] Document review in [JENKINSFILE_SECURITY_REVIEW.txt](#)

---

## 🟡 HIGH PRIORITY (Complete Before First Release)

- [ ] **Enable branch protection rules**
  - [ ] Require code reviews (1 approver minimum)
  - [ ] Require status checks to pass before merge
  - [ ] Dismiss stale reviews when new commits pushed

- [ ] **Set up GitHub Dependabot** (if using GitHub)
  - [ ] Enable in Settings → Code security → Dependabot
  - [ ] Configure automated PRs for version updates
  - [ ] Configure security alerts

- [ ] **Install and configure pre-commit hooks**
  - [ ] Create `.pre-commit-config.yaml`
  - [ ] Run `pre-commit install`
  - [ ] Test with `pre-commit run --all-files`

- [ ] **Run final security scan**
  ```bash
  # If tools installed
  bandit -r gen_ai_hub/ scripts/ -f json -o bandit_report.json
  ```
  - [ ] Code security scan completed
  - [ ] No SEVERITY: HIGH issues remain

---

## 🟢 MEDIUM PRIORITY (Nice to Have Before Release)

- [ ] **Create SECURITY.md** with:
  - [ ] Vulnerability disclosure instructions
  - [ ] Supported versions table
  - [ ] Security contact information
  - [ ] Security practices overview

- [ ] **Update CONTRIBUTING.md** with:
  - [ ] Security guidelines for contributors
  - [ ] Pre-commit hook setup instructions
  - [ ] Testing and validation requirements

- [ ] **Verify git history** is clean
  ```bash
  git log --all --oneline | head -50
  ```
  - [ ] Spot-checked commits for secrets
  - [ ] No suspicious commits found

---

## 🔵 NICE TO HAVE (Long-term)

- [ ] **Set up code scanning** (SAST)
  - [ ] GitHub Advanced Security (if available)
  - [ ] CodeQL scanning
  - [ ] Snyk integration for dependencies

- [ ] **Create CHANGELOG.md** documenting:
  - [ ] Security-related changes
  - [ ] Dependency updates
  - [ ] Bug fixes

- [ ] **Document security practices** in README.md:
  - [ ] How to report vulnerabilities
  - [ ] Supported versions
  - [ ] Known limitations

---

## Remediation Notes

### Item 1: ✅ Infrastructure URLs
**Status**: DONE
- File: `scripts/prompt_template_registry_cleanup.py`
- Changed: Specific SAP URLs → Generic placeholders
- Verification: Changed on [Date]
- Reviewer: [Name] ✓

### Item 2: Dependency Scan
**Status**: PENDING
- Command to run: `safety check -r requirements.txt`
- Findings: [To be filled]
- CVEs found: [Count]
- Resolved: [Yes/No]
- Verification date: _______________

### Item 3: Docker/Kubernetes Review
**Status**: PENDING
- Files reviewed: [List]
- Findings: [Summary]
- Issues found: [Count]
- Resolved: [Yes/No]
- Verification date: _______________

### Item 4: Jenkins CI/CD Review
**Status**: PENDING
- Jenkinsfile reviewed: [Yes/No]
- Findings: [Summary]
- Issues found: [Count]
- Resolved: [Yes/No]
- Verification date: _______________

---

## Stakeholder Sign-Off

- [ ] **Security Lead** : _________________ Date: _______
- [ ] **DevOps Lead** : _________________ Date: _______
- [ ] **Project Lead** : _________________ Date: _______
- [ ] **Legal Review** : _________________ Date: _______

---

## Final Sign-Off Before Release

**Ready for Public Release?** ☐ YES ☐ NO

- All CRITICAL items completed: ☐
- All HIGH PRIORITY items completed: ☐
- No HIGH/CRITICAL security findings remain: ☐
- Git commit hash for release: _________________________
- Tag name for release: _________________________
- Release date: _________________________
- Authorized by: _________________ Date: _______

---

## Quick Reference Commands

```bash
# Run all security checks
echo "=== Dependency Scan ===" && \
pip install safety && \
safety check -r requirements.txt && \
safety check -r requirements-test.txt && \
echo "=== Code Scan ===" && \
pip install bandit && \
bandit -r gen_ai_hub/ scripts/ -f json -o bandit_report.json && \
echo "=== Docker Check ===" && \
grep -r "password\|secret\|token\|key" Dockerfile* && \
echo "=== All scans completed ===" || echo "Check each scan output"
```

---

## Reference Documents

- 📋 **SECURITY_AUDIT_REPORT.md** - Full audit findings
- 📋 **SECURITY_REMEDIATION_GUIDE.md** - Detailed remediation steps
- 📋 **SECURITY_SUMMARY.txt** - Quick overview

---

## Questions?

See the detailed remediation guide: `SECURITY_REMEDIATION_GUIDE.md`

---

**Last Updated**: April 15, 2026  
**Next Review**: [Insert date for follow-up]

