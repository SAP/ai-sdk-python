from gen_ai_hub._alias import alias

# Legacy path for the Google LangChain adapter, which now lives in the langchain
# package. Requires the ``[google]`` extra (``pip install "sap-ai-sdk-gen[google]"``) —
# which in turn pulls ``sap-ai-sdk-langchain[google]`` for the adapter itself.
alias(__name__, "sap_ai_sdk_langchain.google")
