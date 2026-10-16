from gen_ai_hub._alias import alias

# Requires the ``[amazon]`` extra (``pip install "sap-ai-sdk-gen[amazon]"``). Without it,
# importing this module raises ModuleNotFoundError for ``sap_ai_sdk_amazon``.
alias(__name__, "sap_ai_sdk_amazon")
