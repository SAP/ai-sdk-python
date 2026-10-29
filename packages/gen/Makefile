PKG_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SPECS   := $(wildcard $(PKG_DIR)specs/*)

.PHONY: generate generate-kiota generate-java

generate:
	$(foreach spec,$(SPECS), \
		uv run --package sap-openapi-generator sap-generate \
			-i $(spec) \
			-o $(PKG_DIR) \
			-s $(spec)/options-per-service.json; \
	)

generate-kiota:
	$(foreach spec,$(SPECS), \
		uv run --package sap-kiota-generator sap-kiota-generate \
			-i $(spec) \
			-o $(PKG_DIR) \
			-s $(spec)/options-per-service.json; \
	)

# Custom Java `sap-python` generator. Build the jar first:
#   make -C ../openapi-generator-java build   (requires JDK 11+ and Maven)
generate-java:
	$(foreach spec,$(SPECS), \
		uv run --package sap-openapi-generator-java sap-generate-java \
			-i $(spec) \
			-o $(PKG_DIR) \
			-s $(spec)/options-per-service.json; \
	)
