# SAP Cloud SDK for AI (Python) - generative

With this SDK you can leverage the power of generative models available in the generative AI Hub of SAP AI Core.
The SDK provides model access by wrapping the native SDKs of the model providers (OpenAI, Amazon, Google), through langchain, or through the orchestration service.

## Installation

To install this SDK, use the following pip command, which includes support for all models including langchain support:

    pip install "sap-ai-sdk-gen[all]"

The default installation only includes OpenAI models (without langchain support):

    pip install sap-ai-sdk-gen

You can install a subset of the extra libraries (without langchain support) by specifying them in square brackets:

    pip install "sap-ai-sdk-gen[google, amazon]"

## Configuration, Usage

### OpenAI parameter compatibility

The native OpenAI proxy and its LangChain wrapper omit `temperature` for
GPT-5/6 reasoning models, including versioned and `-pro`/`-sol` variants, as
well as o-series and Cohere reasoning models. Temperature is preserved for
GPT chat variants, GPT-6 Astra, and newer GPT models when reasoning effort is
explicitly `none` (`reasoning_effort` in Chat Completions or `reasoning.effort`
in Responses). The original GPT-5, GPT-5 mini/nano, o-series, and Cohere
reasoning models remain filtered regardless of the requested effort.

The Responses API proxy always omits `n`, which is a Chat Completions-only
parameter. This applies to synchronous and asynchronous `create` and `parse`
calls, including requests routed to Responses by LangChain. Chat Completions
continues to forward `n` except for Cohere models.

Please refer to the official documentation hosted on [help.sap.com](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html) for details on how to configure and use the SAP Cloud SDK for AI (Python).
