PKG_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SPECS   := $(wildcard $(PKG_DIR)specs/*)

.PHONY: generate

generate:
	$(foreach spec,$(SPECS), \
		uv run --package sap-openapi-generator sap-generate \
			-i $(spec) \
			-o $(PKG_DIR) \
			-s $(spec)/options-per-service.json; \
	)
