from gen_ai_hub.proxy.langchain.amazon import ChatBedrockConverse
from langchain_core.output_parsers import StrOutputParser


def invoke():
    """
    Ask Claude about the capital of Germany.

    Returns:
        The answer from Claude.
    """
    llm = ChatBedrockConverse(model_name="anthropic--claude-4.6-sonnet")
    response = llm.invoke("Where is the capital of Germany?")
    parser = StrOutputParser()
    return parser.invoke(response)
