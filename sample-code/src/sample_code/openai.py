from fastapi.responses import StreamingResponse
from gen_ai_hub.proxy.native.openai import chat, embeddings, responses
from pydantic import BaseModel


def chat_completion():
    """
    Run chat example for GPT-5.4-nano with the ChatCompletions API.

    Returns:
        JSON object containing the model response as result.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
        {
            "role": "assistant",
            "content": "Yes, customer managed keys are supported by Azure OpenAI.",
        },
        {
            "role": "user",
            "content": "Do other Azure Cognitive Services support this too?",
        },
    ]
    response = chat.completions.create(model_name="gpt-5.4-nano", messages=messages)
    return {"result": response.choices[0].message.content}


def chat_completion_structured():
    """
    Run structured output (JSON) example for GPT-5.4-nano with the ChatCompletions API.

    Returns:
        JSON object response from the model.
    """

    class Person(BaseModel):
        name: str
        age: int

    response = chat.completions.parse(
        model_name="gpt-5.4-nano",
        messages=[{"role": "user", "content": "Tell me about John Doe, aged 30."}],
        response_format=Person,
    )
    return response.choices[0].message.parsed


def chat_completion_stream():
    """
    Run chat example with streaming response for GPT-5.4-nano with the ChatCompletions API.

    Returns:
        Streaming response emitting the produced text.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Count from 1 to 10, one number per line."},
    ]

    def generate():
        stream = chat.completions.create(
            model_name="gpt-5.4-nano",
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

    return StreamingResponse(generate(), media_type="text/plain")


def responses_simple():
    """
    Run chat example for GPT-5.4-nano with the Responses API.

    Returns:
        JSON object containing the model response as result.
    """
    response = responses.create(
        model="gpt-5.4-nano",
        instructions="You are a helpful assistant.",
        input="What is the capital of France?",
    )
    return {"result": response.output[0].content[0].text}


def responses_structured():
    """
    Run structured output (JSON) example for GPT-5.4-nano with the Responses API.

    Returns:
        JSON object response from the model.
    """

    class Person(BaseModel):
        name: str
        age: int

    response = responses.parse(
        model="gpt-5.4-nano",
        input="Tell me about John Doe aged 30.",
        text_format=Person,
    )
    return response.output_parsed


def embedding():
    """
    Run embedding example.

    Returns:
        JSON object containing the embedding.
    """
    result = embeddings.create(
        model_name="text-embedding-3-small",
        input="The quick brown fox jumps over the lazy dog.",
    )
    return {
        "result": result.data[0].embedding,
    }
