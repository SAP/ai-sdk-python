# Release Notes
## evaluations-v1.0.0

### Features
- Initial release of `sap-ai-sdk-evaluations`, split out from `sap-ai-sdk-gen`. Contains the evaluations client, config models, and helpers. Depends on `sap-ai-sdk-orchestration` and `sap-ai-sdk-prompt-registry`.
- AWS S3 artifact storage (`boto3`/`botocore`) is now an optional `[amazon]` extra; `boto3`/`botocore` are imported lazily and raise an actionable `ImportError` when the extra is not installed.
