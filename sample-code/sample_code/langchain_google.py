from gen_ai_hub.proxy.langchain.google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser


def invoke():
    """
    Ask Gemini about the capital of Germany.

    Returns:
        The answer from Gemini.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")
    response = llm.invoke("Where is the capital of Germany?")
    parser = StrOutputParser()
    return parser.invoke(response)
