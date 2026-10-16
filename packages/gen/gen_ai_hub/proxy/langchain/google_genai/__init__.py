from gen_ai_hub._alias import alias

# Legacy path for the Google LangChain adapter, which moved into the google package.
# Requires the ``[google]`` extra (``pip install "sap-ai-sdk-gen[google]"``) — which in
# turn needs ``sap-ai-sdk-google[langchain]`` for the adapter itself.
alias(__name__, "sap_ai_sdk_google.langchain")
