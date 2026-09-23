from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from pydantic import BaseModel

from gen_ai_hub.proxy.langchain.openai import ChatOpenAI, OpenAIEmbeddings


class SampleSchema(BaseModel):
    """A sample structured output schema."""

    content: str
    language: str


def invoke():
    """
    Ask GPT about the capital of Germany.

    Returns:
        The answer from the GPT
    """
    llm = ChatOpenAI(proxy_model_name="gpt-5.4-nano")
    response = llm.invoke("Where is the capital of Germany?")
    parser = StrOutputParser()
    return parser.invoke(response)


def invoke_chain():
    """
    Chain a prompt template, LLM, and output parser to answer in German.

    Returns:
        The model response as a string.
    """
    llm = ChatOpenAI(proxy_model_name="gpt-5.4-nano")
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "Answer the following in {language}:"),
        ("user", "{text}"),
    ])
    chain = prompt_template | llm | StrOutputParser()
    return chain.invoke({"language": "german", "text": "What is the capital of Germany?"})


def invoke_with_structured_output_json_schema():
    """
    Invoke the LLM with structured output using JSON schema (Pydantic model).

    Returns:
        SampleSchema instance with content and language fields.
    """
    llm = ChatOpenAI(proxy_model_name="gpt-5.4-nano")
    structured_llm = llm.with_structured_output(method="json_schema", schema=SampleSchema, strict=True)
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "Answer the following question. Respond with the answer text and the language you answered in."),
        ("user", "{text}"),
    ])
    chain = prompt_template | structured_llm
    return chain.invoke({"text": "What is the capital of France?"})


def invoke_tool_chain():
    """
    Invoke a tool chain: bind an add tool to the LLM, execute any tool calls,
    then return the final answer.

    Returns:
        The final model response as a string after tool execution.
    """
    @tool
    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    llm = ChatOpenAI(proxy_model_name="gpt-5.4-nano")
    llm_with_tools = llm.bind_tools([add])

    messages = [HumanMessage(content="What is 279 + 929?")]
    response = llm_with_tools.invoke(messages)
    messages.append(response)

    for tool_call in response.tool_calls:
        if tool_call["name"] == "add":
            result = add.invoke(tool_call["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))

    final_response = llm_with_tools.invoke(messages)
    parser = StrOutputParser()
    return parser.invoke(final_response)


def invoke_rag_chain():
    """
    Build a RAG chain using SAP AI SDK embeddings and chat model with LangChain.

    Documents are embedded with OpenAIEmbeddings from gen_ai_hub and stored in an
    in-memory vector store. A retriever feeds relevant context into a prompt template
    that is then answered by ChatOpenAI.

    Returns:
        The answer to "What is the best sdk in the world?" grounded in the provided documents.
    """
    documents = [
        "SAP BTP provides cloud-native platform services for building enterprise applications.",
        "The SAP AI Core service lets you train and deploy machine learning models at scale.",
        "The SAP Cloud SDK for Python is the best SDK in the world.",
        "SAP Joule is the AI copilot embedded across the SAP portfolio of business applications.",
    ]

    embedding_model = OpenAIEmbeddings(proxy_model_name="text-embedding-3-small")
    vectorstore = InMemoryVectorStore.from_texts(documents, embedding=embedding_model)
    retriever = vectorstore.as_retriever()

    llm = ChatOpenAI(proxy_model_name="gpt-5.4-nano")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the question using only the context below.\n\nContext:\n{context}"),
        ("user", "{question}"),
    ])

    def format_docs(docs):
        return "\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain.invoke("What is the best sdk in the world?")


def stream_chain() -> StreamingResponse:
    """
    Stream chunks from the LLM about SAP Cloud SDK.

    Returns:
        StreamingResponse yielding text chunks.
    """
    llm = ChatOpenAI(proxy_model_name="gpt-5.4-nano")
    messages = [HumanMessage(content="Write a 1000 word explanation about SAP AI SDK and its capabilities")]

    async def generate():
        async for chunk in llm.astream(messages):
            if chunk.content:
                yield chunk.content

    return StreamingResponse(generate(), media_type="text/plain")

