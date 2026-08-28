PKG_DIR      := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SPEC_DIR     := $(PKG_DIR)specs/document-grounding
OPTIONS_FILE := $(SPEC_DIR)/options-per-service.json
SPEC_KEY     := src/spec/api.yaml
SPEC_INPUT   := $(SPEC_DIR)/api.yaml
PROCESSED    := $(PKG_DIR).cache/processed.yaml
MAPPINGS     := $(PKG_DIR).cache/mappings.yaml
GEN_TMP      := $(PKG_DIR).cache/gen-tmp
GEN_OUT      := $(PKG_DIR)../../gen/gen_ai_hub/document_grounding_generation/generated
CONFIG       := $(PKG_DIR)config/python-config.yaml
# Fully-qualified import prefix used inside the generated files after rewriting
GEN_PKG      := gen_ai_hub.document_grounding_generation.generated

.PHONY: generate test

generate:
	mkdir -p $(PKG_DIR).cache
	uv run --package sap-openapi-generator python -m sap_openapi_generator.preprocess_spec \
		--input $(SPEC_INPUT) \
		--output $(PROCESSED) \
		--options $(OPTIONS_FILE) \
		--spec-key "$(SPEC_KEY)" \
		--mappings-output $(MAPPINGS)
	npx --yes @openapitools/openapi-generator-cli generate \
		-g python \
		-i $(PROCESSED) \
		-o $(GEN_TMP) \
		-c $(CONFIG) \
		$$([ -f $(MAPPINGS) ] && echo "--config $(MAPPINGS)") \
		--additional-properties packageName=generated
	rm -rf $(GEN_OUT)
	mv $(GEN_TMP)/generated $(GEN_OUT)
	rm -rf $(GEN_TMP) $(PROCESSED) $(MAPPINGS)
	# Rewrite bare 'generated' imports to fully-qualified package path
	find $(GEN_OUT) -name "*.py" -exec \
		sed -i '' \
			's/from generated\./from $(GEN_PKG)./g; s/import generated\./import $(GEN_PKG)./g; s/from generated import /from $(GEN_PKG) import /g' \
		{} +

test:
	uv run --package sap-openapi-generator pytest $(PKG_DIR)tests/ -v
