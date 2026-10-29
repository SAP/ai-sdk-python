PKG_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

.PHONY: build test clean

# Build the custom generator jar + copy runtime dependencies into target/dependency.
# Requires JDK 11+ and Maven. Pins openapi-generator 7.26.0 (see pom.xml).
build:
	cd $(PKG_DIR) && mvn -q -B package

test:
	uv run --package sap-openapi-generator-java pytest $(PKG_DIR)tests/ -v

clean:
	cd $(PKG_DIR) && mvn -q clean
