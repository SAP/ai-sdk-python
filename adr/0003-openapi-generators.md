# OpenAPI Generators

## Status

proposed

## Context

The Python SDK code is currently fully manually written and maintained. The Java and JS SDKs use a code generator to generate low-level clients. It is planned to introduce code generation to the Python SDK as well.

## Decision

Use the [OpenAPI generator](https://openapi-generator.tech/) for code generation in the Python SDK in favor of other code generators. The extent to which the generator will be used will to be decided in future ADRs.

## Consequences

- For integrating the OpenAPI generator it is necessary to write and maintain preprocessing and postprocessing scripts as well as template files.
- For running the generator a Java runtime needs to be installed during development and in related workflows.
- The generator can be used to automatically monitor spec changes.
- Reduces maintenance efforts for the generated portions of the SDK.
- Aligns the Python SDK with the other SDKs, in particular Java, which uses the OpenAPI generator, too.

## Appendix

The following generators were considered (all except two were immediately ruled out):

- [OpenAPI Generator](https://openapi-generator.tech/)
- [Kiota](https://github.com/microsoft/kiota)
- [OpenAPI Python Client](https://github.com/openapi-generators/openapi-python-client): ruled out because it is only sporadically maintained and has no Pydantic support
- [Datamodel Code Generator](https://github.com/koxudaxi/datamodel-code-generator): ruled out because it only generates models and not the full client
- [Hey API](https://github.com/hey-api/hey-api): ruled out because the Python generator is in alpha (as of September 2026) and not stable yet
- [Fern](https://github.com/fern-api/fern): ruled out because (despite being Open-source) it is a commercial product and has been acquired by Postman
- [Speakeasy](https://www.speakeasy.com): ruled out because it is a commercial product
- [Stainless](https://www.stainless.com/): not available anymore (as of September 2026)

Commercial generators are not considered for multiple reasons, one of them being that this would make external contributions to the SDK more difficult.

### Option A: OpenAPI Generator

Pros:

- well-established codebase/project
- Open-Source (Apache 2.0 license)
- has support for Pydantic, httpx and async

Cons:

- written in Java (however, templates can be used to control output)
- generated code is not Pythonic nor up-to-date to current typing conventions

### Option B: Kiota

Pros:

- modern, actively maintained/developed generator
- Open-Source (MIT license)

Cons:

- written in C# with no templating support (limited customization options)
- no Pydantic support
- generated code is not Pythonic
