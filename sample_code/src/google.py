from fastapi.responses import StreamingResponse
from gen_ai_hub.proxy import get_proxy_client
from gen_ai_hub.proxy.native.google_genai import Client
from google.genai import types


def generate():
    """
    Run chat example for Gemini 3.5 Flash.

    Returns:
        JSON object containing the model response as result.
    """
    proxy_client = get_proxy_client("gen-ai-hub")
    client = Client(proxy_client=proxy_client)
    response = client.models.generate_content(
        model="gemini-3.5-flash", contents="How many paws are there for a dog?"
    )
    return {"result": response.candidates[0].content.parts[0].text}


def generate_stream():
    """
    Run chat example with streaming response for Gemini 3.5 Flash.

    Returns:
        Streaming response emitting the produced text.
    """
    proxy_client = get_proxy_client("gen-ai-hub")

    client = Client(
        proxy_client=proxy_client,
    )

    def stream():
        stream = client.models.generate_content_stream(
            model="gemini-3.5-flash", contents="Explain singularity in short terms."
        )
        for chunk in stream:
            if chunk.text:
                yield chunk.text

    return StreamingResponse(stream(), media_type="text/plain")


def tool_call():
    """
    Run chat example including a tool call for Gemini 3.5 Flash.

    Returns:
        JSON object containing the model response as result.
    """

    # addition tool to call
    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    proxy_client = get_proxy_client("gen-ai-hub")

    client = Client(
        proxy_client=proxy_client,
    )
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="What is 769 + 348?",
        config=types.GenerateContentConfig(tools=[add]),
    )
    return {"result": response.candidates[0].content.parts[0].text}
