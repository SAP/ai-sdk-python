# OpenAPI Generator for New Clients

## Status

agreed

## Context

There are multiple new clients that will be added to the SDK in the upcoming quarters. The Java and JS SDKs heavily rely on code generation and will generate the new clients to a large degree. The Python SDK, on the other hand, is currently fully manually written. Code generation has been explored as a future option, see [ADR 0004](https://github.com/SAP/ai-sdk-python/blob/main/adr/0004-openapi-generators.md) and [this PoC](https://github.com/SAP/ai-sdk-python/pull/99) introducing the OpenAPI generator including a working client for the context registry service. This ADR decides on the approach for adding new clients to the Python SDK: with code generation or as manually written clients.

## Decision

Use the code generation approach for new clients (Option B below).

## Consequences

- Lower effort in the future for staying up-to-date with specs.
- Closer alignment between Python and the other SDKs.
- Easier to add and maintain multiple new services.
- There is an initial effort for introducing the generation approach.

## Appendix

### Option A (Manually-written Client)

Pros:

- Fully aligned with the current general approach and coding style in the SDK
- Easier approach in the short-term (but higher cost in the long term when more and more clients need to be added)

Cons:

- Higher maintenance effort
- More difficult to keep up-to-date with spec changes (no automation)

### Option B (Generated Client)

Pros:

- Lower overall maintenance effort, in particular when maintaining many clients
- Easy to regenerate client code in case of spec changes
- Consistent with the approach in the Java and JS SDK

Cons:

- Need to maintain code generator including customizations (however, Java and JS SDKs report this cost being lower than keeping the clients up-to-date manually)
- Initially adding the generator takes time and effort
- The generated client will stylistically not be fully consistent with the manually written clients in the SDK, for example how the `ai_resource_group` header is handled (however, a remedy for this can be a wrapper layer around the client)
