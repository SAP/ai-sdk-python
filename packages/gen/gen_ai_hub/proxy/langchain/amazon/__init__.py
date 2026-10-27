from gen_ai_hub._alias import alias

# Legacy path for the Bedrock LangChain adapter, which now lives in the langchain
# package. Requires the ``[amazon]`` extra (``pip install "sap-ai-sdk-gen[amazon]"``) —
# which in turn pulls ``sap-ai-sdk-langchain[amazon]`` for the adapter itself.
alias(__name__, "sap_ai_sdk_langchain.amazon")
