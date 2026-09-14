import uuid

from fastapi.responses import StreamingResponse
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import BaseModel

from gen_ai_hub.proxy.core import get_proxy_client
from gen_ai_hub.proxy.langchain.init_models import init_embedding_model, init_llm
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI

def _build_langgraph_app(model_name: str = "gpt-5.4-nano"):
    """Build a simple single-node LangGraph app with in-memory checkpointing."""
    llm = ChatOpenAI(proxy_model_name=model_name)

    async def call_model(state: MessagesState):
        response = await llm.ainvoke(state["messages"])
        return {"messages": [response]}

    workflow = (
        StateGraph(MessagesState)
        .add_node("model", call_model)
        .add_edge(START, "model")
        .add_edge("model", END)
    )
    return workflow.compile(checkpointer=MemorySaver())


async def langgraph_chat_completion():
    """
    Invoke the model twice within the same thread to demonstrate memory across turns.

    Returns:
        JSON object containing both responses.
    """
    app = _build_langgraph_app()
    config: RunnableConfig = {"configurable": {"thread_id": str(uuid.uuid4())}}

    output1 = await app.ainvoke(
        {"messages": [HumanMessage(content="Tell me something about the SAP AI SDK")]},
        config=config,
    )
    output2 = await app.ainvoke(
        {"messages": [HumanMessage(content="What is special about it? Tell me in 3 sentences!")]},
        config=config,
    )

    first = output1["messages"][-1].content
    second = output2["messages"][-1].content
    return {"result": f"{first}\n\n{second}"}


async def langgraph_chat_completion_stream():
    """
    Stream two sequential turns through a LangGraph workflow.

    Returns:
        A StreamingResponse that yields both turns separated by a blank line.
    """
    app = _build_langgraph_app()
    thread_config: RunnableConfig = {"configurable": {"thread_id": str(uuid.uuid4())}}

    async def generate():
        async for chunk, _ in app.astream(
            {"messages": [HumanMessage(content="Tell me something about the SAP AI SDK")]},
            config=thread_config,
            stream_mode="messages",
        ):
            content = chunk.content  # type: ignore[union-attr]
            if isinstance(content, str) and content:
                yield content

        yield "\n\n"

        async for chunk, _ in app.astream(
            {"messages": [HumanMessage(content="What is special about it? Tell me in 3 sentences!")]},
            config=thread_config,
            stream_mode="messages",
        ):
            content = chunk.content  # type: ignore[union-attr]
            if isinstance(content, str) and content:
                yield content

    return StreamingResponse(generate(), media_type="text/plain")


def tool_chain():
    """
    Demonstrate tool calling: the model calls a custom Python function and
    the result is fed back for a final natural-language response.

    Returns:
        JSON object containing the final model response.
    """
    llm = ChatOpenAI(proxy_model_name="gpt-5.4")

    @tool
    def shareholder_value(value: float) -> str:
        """Multiplies the shareholder value."""
        return f"The shareholder value has been increased to {value * 2}"

    messages: list[BaseMessage] = [HumanMessage(content="Increase the shareholder value, it is currently at 10")]

    response = llm.bind_tools([shareholder_value]).invoke(messages)
    messages.append(response)

    if response.tool_calls and response.tool_calls[0]["name"] == "shareholder_value":
        tool_call = response.tool_calls[0]
        tool_result = shareholder_value.invoke(tool_call["args"])
        messages.append(
            ToolMessage(content=tool_result, tool_call_id=tool_call["id"] or "default")
        )
    else:
        messages.append(SystemMessage(content="No tool calls were made"))

    final = llm.invoke(messages)
    return {"result": StrOutputParser().invoke(final)}


class SampleSchema(BaseModel):
    """A sample structured output schema."""

    setup: str
    punchline: str
    rating: int


def structured_output():
    """
    Ask the model for a structured response conforming to a Pydantic schema.

    Returns:
        JSON object containing the structured output.
    """
    llm = ChatOpenAI(proxy_model_name="gpt-5.4-nano")
    structured_llm = llm.with_structured_output(SampleSchema)
    result = structured_llm.invoke("Tell me a joke about cats")
    if not isinstance(result, SampleSchema):
        raise RuntimeError("Unexpected structured output type")
    return {"result": result.model_dump()}

def invoke_chain_with_fallback_configs():
    """
    Invoke a chain with fallback model configurations for resilience.

    If the primary model fails, LangChain automatically retries with each
    fallback in order until one succeeds.

    Returns:
        JSON object containing the model response.
    """
    primary_llm = ChatOpenAI(proxy_model_name="gpt-5.4-nano")
    client = get_proxy_client()
    fallback_llms = [
        ChatOpenAI(proxy_model_name="anthropic--claude-4.6-sonnet"),
        init_llm("anthropic--claude-4.6-sonnet", proxy_client=client),
    ]
    llm = primary_llm.with_fallbacks(fallback_llms)
    chain = llm | StrOutputParser()
    result = chain.invoke([HumanMessage(content="Tell me about SAP AI SDK")])
    return {"result": result}


def invoke_dynamic_model_agent():
    """
    Select a model dynamically based on input complexity.

    Short or simple prompts are routed to a lightweight model; longer or more
    complex prompts are routed to a more capable model. The routing decision is
    made at invocation time via a custom selector function.

    Returns:
        JSON object containing the model response.
    """
    simple_chain = ChatOpenAI(proxy_model_name="gpt-5.4-nano") | StrOutputParser()
    complex_chain = ChatOpenAI(proxy_model_name="anthropic--claude-4.6-sonnet") | StrOutputParser()

    def select_chain(messages: list):
        total_words = sum(len(str(m.content).split()) for m in messages)
        return complex_chain if total_words > 20 else simple_chain

    message = (
        "Explain the key architectural differences between microservices and monolithic "
        "applications, covering scalability, maintainability, deployment complexity, and "
        "data management strategies."
    )
    messages = [HumanMessage(content=message)]
    result = select_chain(messages).invoke(messages)
    return {"result": result}