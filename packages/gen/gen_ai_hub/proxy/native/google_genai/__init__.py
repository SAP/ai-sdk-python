from gen_ai_hub._alias import alias

# Requires the ``[google]`` extra (``pip install "sap-ai-sdk-gen[google]"``). Without it,
# importing this module raises ModuleNotFoundError for ``sap_ai_sdk_google``.
alias(__name__, "sap_ai_sdk_google")
