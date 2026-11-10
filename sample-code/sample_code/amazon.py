import json

from fastapi.responses import StreamingResponse
from gen_ai_hub.proxy.native.amazon import Session


def converse():
    """
    Run chat example for Claude 4.6 Sonnet.

    Returns:
        JSON object containing the model response as result.
    """
    bedrock = Session().client(model_name="anthropic--claude-4.6-sonnet")
    conversation = [
        {
            "role": "user",
            "content": [
                {
                    "text": "Describe the purpose of a 'Hello World' program in one sentence."
                }
            ],
        }
    ]
    response = bedrock.converse(
        messages=conversation,
    )
    return {"result": response["output"]["message"]["content"][0]["text"]}

def converse_stream():
    """
    Run chat example with streaming response for Claude 4.6 Sonnet.

    Returns:
        Streaming response emitting the produced text.
    """
    bedrock = Session().client(model_name="anthropic--claude-4.6-sonnet")
    conversation = [
        {
            "role": "user",
            "content": [
                {
                    "text": "Describe the purpose of a 'Hello World' program in one sentence."
                }
            ],
        }
    ]

    def stream():
        response = bedrock.converse_stream(
            messages=conversation,
        )
        for chunk in response["stream"]:
            if "contentBlockDelta" in chunk:
                yield chunk["contentBlockDelta"]["delta"]["text"]

    return StreamingResponse(stream(), media_type="text/plain")

def embedding():
    """
    Run embedding example with Amazon Titan Embed Text.

    Returns:
        JSON object containing the embedding.
    """
    bedrock = Session().client(model_name="amazon--titan-embed-text")
    body = json.dumps({"inputText": "Please recommend books with a theme similar to the movie 'Inception'."})
    response = bedrock.invoke_model(body=body)
    response_body = json.loads(response.get("body").read())
    return response_body
