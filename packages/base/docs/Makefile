SHELL := /bin/bash

.PHONY: all api_doc build comment_out_lines

all: api_doc build comment_out_lines

api_doc:
	python -m sphinx.ext.apidoc -o source/_api_doc ../ai_api_client_sdk -d 1 -T -f -M

build:
	python -m sphinx -b html ./source ./build/html

comment_out_lines:
	@if [ "$$(uname)" = "Darwin" ]; then \
		sed -i '' '/window\.location/s/^/\/\/ /' ./build/html/_static/doctools.js; \
	else \
		sed -i '/window\.location/s/^/\/\/ /' ./build/html/_static/doctools.js; \
	fi
