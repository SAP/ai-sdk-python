# OpenAPI Generator for Context Registry

## Status

Under discussion

## Context

The [context registry service](https://github.tools.sap/AI/context-registry) is currently not supported in the Python SDK. The Java and JS SDKs heavily rely on code generation and will generate the new client for context registry from [the spec](https://github.tools.sap/AI/context-registry/tree/main/src/spec). The Python SDK, on the other hand, is currently fully manually written. Code generation has been explored as a future option, see [ADR 0004](https://github.com/SAP/ai-sdk-python/blob/main/adr/0004-openapi-generators.md) and [this PoC](https://github.com/SAP/ai-sdk-python/pull/99) introducing the OpenAPI generator including a working client for the context registry service. This ADR decides how the context registry client will be added to the Python SDK: with code generation or as a manually written client.

## Decision

TBD

## Consequences

TBD

## Appendix

### Option A (Handwritten Client)

Pros:

- Fully aligned with the current general approach and coding style in the SDK
- For the context registry spec on its own, adding the client manually would be faster than first introducing a code generator

Cons:

- Higher maintenance effort
- More difficult to keep up-to-date with spec changes (no automation)

### Option B (Generated Client)

Pros:

- Lower maintenance effort, in particular if code generation is used for multiple services (not only context registry)
- Easy to regenerate client code in case of spec changes
- Consistent with the approach in the Java and JS SDK

Cons:

- Need to maintain code generator including customizations (however, Java and JS SDKs report this cost being lower than keeping the clients up-to-date manually)
- Initially adding the generator takes time and effort
- The generated client will stylistically not be fully consistent with the manually written clients in the SDK (for example with regard to how the `ai_resource_group` header is handled)
