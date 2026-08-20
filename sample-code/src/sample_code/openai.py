from fastapi.responses import StreamingResponse
from gen_ai_hub.proxy.native.openai import chat, embeddings, responses
from pydantic import BaseModel

# MISSING
# - add async examples


def chat_completion():
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
    return chat.completions.create(model_name="gpt-5.4-nano", messages=messages)


class Person(BaseModel):
    name: str
    age: int


def chat_completion_structured():
    response = chat.completions.parse(
        model_name="gpt-5.4-nano",
        messages=[{"role": "user", "content": "Tell me about John Doe, aged 30."}],
        response_format=Person,
    )
    return response.choices[0].message.parsed


def chat_completion_stream():
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

    return StreamingResponse(generate(), media_type="text/event-stream")


def chat_completion_structured_stream():
    with chat.completions.with_streaming_response.parse(
        model_name="gpt-5.4-nano",
        messages=[{"role": "user", "content": "Tell me about John Doe, aged 30."}],
        response_format=Person,
    ) as stream:
        response = stream.parse()
    return response.choices[0].message.parsed


def responses_simple():
    return responses.create(
        model="gpt-5.4-nano",
        instructions="You are a helpful assistant.",
        input="What is the capital of France?",
    )


def responses_structured():
    response = responses.parse(
        model="gpt-5.4-nano",
        input="Tell me about John Doe aged 30.",
        text_format=Person,
    )
    return response.output_parsed


def embedding():
    result = embeddings.create(
        model_name="text-embedding-3-small",
        input="The quick brown fox jumps over the lazy dog.",
    )
    return {
        "model": result.model,
        "embedding": result.data[0].embedding,
        "usage": {
            "prompt_tokens": result.usage.prompt_tokens,
            "total_tokens": result.usage.total_tokens,
        },
    }
