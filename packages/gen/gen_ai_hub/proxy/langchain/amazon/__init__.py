from gen_ai_hub._alias import alias

# Legacy path for the Bedrock LangChain adapter, which moved into the amazon package.
# Requires the ``[amazon]`` extra (``pip install "sap-ai-sdk-gen[amazon]"``) — which in
# turn needs ``sap-ai-sdk-amazon[langchain]`` for the adapter itself.
alias(__name__, "sap_ai_sdk_amazon.langchain")
