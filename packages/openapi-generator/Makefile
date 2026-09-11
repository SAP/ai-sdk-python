PKG_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

.PHONY: test

test:
	uv run --package sap-openapi-generator pytest $(PKG_DIR)tests/ -v
