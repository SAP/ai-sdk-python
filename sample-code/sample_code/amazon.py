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
