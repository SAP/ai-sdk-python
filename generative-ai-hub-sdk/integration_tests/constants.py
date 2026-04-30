# The models below are used for testing purposes in the integration tests.
# The models are chosen based on the following criteria
# - to cover a variety of functionalities and capabilities across different providers, and
# - to save costs by using smaller models where possible, and
# - to ensure that the latest models are used for testing.

AMAZON_NOVA_MICRO_TEST_MODEL = "amazon--nova-micro"
AMAZON_NOVA_PREMIER_TEST_MODEL = "amazon--nova-premier"
CLAUDE_4_SONNET_TEST_MODEL = "anthropic--claude-4-sonnet"
AMAZON_TITAN_EMBEDDING_TEST_MODEL = "amazon--titan-embed-text"
CLAUDE_4_5_SONNET_TEST_MODEL = "anthropic--claude-4.5-sonnet"
CLAUDE_3_7_SONNET_TEST_MODEL = "anthropic--claude-3.7-sonnet"
CLAUDE_4_5_HAIKU_TEST_MODEL = "anthropic--claude-4.5-haiku"
GEMINI_2_FLASH_TEST_MODEL = "gemini-2.0-flash"
GEMINI_2_5_FLASH_LITE_TEST_MODEL = "gemini-2.5-flash-lite"
GOOGLE_EMBEDDING_TEST_MODEL = "gemini-embedding"
IBM_TEST_MODEL= "ibm--granite-13b-chat"
META_LLAMA_TEST_MODEL = "meta--llama3.1-70b-instruct"
NVIDIA_EMBEDDING_TEST_MODEL = "nvidia--llama-3.2-nv-embedqa-1b"
OPENAI_EMBEDDING_TEST_MODEL = "text-embedding-3-small"
OPENAI_GPT_4_1_MINI_TEST_MODEL = "gpt-4.1-mini" # replace with "gpt-5-mini" when available
OPENAI_GPT_4O_MINI_TEST_MODEL = "gpt-4o-mini"
OPENAI_GPT_O3_MINI_TEST_MODEL = "o3-mini"
OPENAI_GPT_O4_MINI_TEST_MODEL = "o4-mini"
OPENAI_GPT_5_TEST_MODEL = "gpt-5-nano"
MISTRAL_TEST_MODEL = "mistralai--mistral-small-instruct"
PERPLEXITY_TEST_MODEL = "sonar"
COHERE_COMMAND_A_TEST_MODEL = "cohere--command-a-reasoning"
COHERE_RERANK_TEST_MODEL = "cohere--command-a-reasoning"
