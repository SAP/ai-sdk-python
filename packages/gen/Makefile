PKG_DIR  := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SPEC_DIR := $(PKG_DIR)specs/document-grounding

.PHONY: generate

generate:
	uv run --package sap-openapi-generator sap-generate \
		--spec $(SPEC_DIR)/api.yaml \
		--output $(PKG_DIR)gen_ai_hub/document_grounding_generation/generated \
		--package-name gen_ai_hub.document_grounding_generation.generated \
		--options $(SPEC_DIR)/options-per-service.json \
		--spec-key src/spec/api.yaml
