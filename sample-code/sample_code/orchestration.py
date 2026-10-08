from fastapi import Query
from fastapi.responses import StreamingResponse
from gen_ai_hub.orchestration_v2 import (
    AzureContentSafetyInput,
    AzureContentSafetyInputFilterConfig,
    AzureContentSafetyOutput,
    AzureContentSafetyOutputFilterConfig,
    AzureThreshold,
    DPICustomEntity,
    DPIMethodConstant,
    DPIStandardEntity,
    EmbeddingsInput,
    EmbeddingsModelConfig,
    EmbeddingsModelDetails,
    EmbeddingsModuleConfigs,
    EmbeddingsOrchestrationConfig,
    FilteringModuleConfig,
    FunctionObject,
    FunctionTool,
    GlobalStreamOptions,
    ImageItem,
    InputFiltering,
    InputTranslationConfig,
    JSONResponseSchema,
    LlamaGuard38bFilter,
    LlamaGuard38bFilterConfig,
    LLMModelDetails,
    MaskingMethod,
    MaskingModuleConfig,
    MaskingProviderConfig,
    ModuleConfig,
    OrchestrationConfig,
    OrchestrationError,
    OrchestrationService,
    OutputFiltering,
    OutputTranslationConfig,
    ProfileEntity,
    PromptTemplatingModuleConfig,
    ResponseFormatJsonSchema,
    SAPDocumentTranslationInput,
    SAPDocumentTranslationOutput,
    SystemMessage,
    Template,
    ToolChatMessage,
    TranslationModuleConfig,
    UserMessage,
    function_tool,
)


def completion(
    message: str = Query(default="What is the longest river on planet earth?", description="User message to send to the LLM."),
    model: str = Query(default="gpt-5.4-nano", description="LLM model name."),
):
    """Run a single-turn chat completion through the Orchestration Service."""
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(template=[UserMessage(content=message)]),
                model=LLMModelDetails(name=model),
            )
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


async def completion_async(
    message: str = Query(default="What is the longest river on planet earth?"),
    model: str = Query(default="gpt-5.4-nano"),
):
    """Run an async single-turn chat completion through the Orchestration Service."""
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(template=[UserMessage(content=message)]),
                model=LLMModelDetails(name=model),
            )
        )
    )
    service = OrchestrationService(config=config)
    result = await service.arun()
    await service.aclose_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def completion_stream(
    message: str = Query(default="What is the longest river on planet earth?"),
    model: str = Query(default="gpt-5.4-nano"),
):
    """Stream a chat completion response token by token."""
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(template=[UserMessage(content=message)]),
                model=LLMModelDetails(name=model),
            )
        ),
        stream=GlobalStreamOptions(enabled=True),
    )
    service = OrchestrationService(config=config)

    def generate():
        stream = service.stream()
        for chunk in stream:
            if chunk.final_result:
                content = chunk.final_result.choices[0].delta.content
                if content:
                    yield content
        service.close_http_connection()

    return StreamingResponse(generate(), media_type="text/plain")


def completion_json(
    model: str = Query(default="gpt-5.4-nano"),
):
    """
    Run a structured-output (JSON) chat completion.

    Returns a JSON object matching the Person schema: { firstName, lastName }.
    The question is fixed: "Who was the first person on the moon?"
    """
    json_schema = {
        "title": "Person",
        "type": "object",
        "properties": {
            "firstName": {"type": "string", "description": "The person's first name."},
            "lastName": {"type": "string", "description": "The person's last name."},
        },
    }
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        SystemMessage(content="Format the response as json."),
                        UserMessage(content="Who was the first person on the moon?"),
                    ],
                    response_format=ResponseFormatJsonSchema(
                        json_schema=JSONResponseSchema(
                            name="person",
                            description="person mapping",
                            schema=json_schema,
                        )
                    ),
                ),
                model=LLMModelDetails(name=model),
            )
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def completion_template(
    country: str = Query(default="Denmark", description="Value to substitute into the {{?country}} placeholder."),
    model: str = Query(default="gpt-5.4-nano"),
):
    """
    Run a templated chat completion.

    The template is: "What is the capital of {{?country}}?"
    Supply a different `country` query parameter to customise the prompt.
    """
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[UserMessage(content="What is the capital of {{?country}}?")]
                ),
                model=LLMModelDetails(name=model),
            )
        )
    )
    service = OrchestrationService(config=config)
    result = service.run(placeholder_values={"country": country})
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def completion_with_fallback(
    message: str = Query(default="What is the longest river on planet earth?"),
    primary_model: str = Query(default="dummy-model", description="Primary model. Use an invalid name to trigger fallback."),
    fallback_model: str = Query(default="anthropic--claude-4.6-sonnet", description="Fallback model, used when the primary fails."),
):
    """
    Run a chat completion with automatic model fallback.

    If `primary_model` fails (e.g. invalid name, quota exceeded), the service
    automatically retries with `fallback_model`.
    """
    config = OrchestrationConfig(
        modules=[
            ModuleConfig(
                prompt_templating=PromptTemplatingModuleConfig(
                    prompt=Template(template=[UserMessage(content=message)]),
                    model=LLMModelDetails(name=primary_model),
                )
            ),
            ModuleConfig(
                prompt_templating=PromptTemplatingModuleConfig(
                    prompt=Template(template=[UserMessage(content=message)]),
                    model=LLMModelDetails(name=fallback_model),
                )
            ),
        ]
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def completion_abap(
    message: str = Query(default="Explain the concept of internal tables in ABAP"),
    model: str = Query(default="sap-abap-1"),
):
    """Run a chat completion using the SAP ABAP-specialised model."""
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(template=[UserMessage(content=message)]),
                model=LLMModelDetails(name=model),
            )
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def message_history():
    """
    Run a two-turn conversation demonstrating message history.

    Turn 1: "What is the capital of France?"
    Turn 2: "What is the typical food there?" (uses turn 1 history for context)
    Both turns use gpt-5.4-nano. The prompts are fixed to keep the demo coherent.
    """
    service = OrchestrationService()
    first_config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(template=[UserMessage(content="What is the capital of France?")]),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            )
        )
    )
    first_response = service.run(config=first_config)
    history = first_response.intermediate_results.templating or []
    history.append(first_response.final_result.choices[0].message)

    second_config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(template=[UserMessage(content="What is the typical food there?")]),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            )
        )
    )
    second_response = service.run(config=second_config, history=history)
    service.close_http_connection()
    return {"result": second_response.final_result.choices[0].message.content}


def completion_image():
    """
    Run a multimodal completion with an image input.

    Sends a publicly accessible image and asks the model to describe prominent objects.
    The image URL is fixed for demo purposes.
    """
    image = ImageItem(url="https://picsum.photos/id/1/200/300")
    multimodal_content = [image, "What objects are prominent in this image?"]
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(template=[UserMessage(content=multimodal_content)]),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            )
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def input_filtering(
    message: str = Query(
        default="My social insurance number is ABC123456789.",
        description="Input prompt to test. Should contain PII or sensitive content to trigger the filter.",
    ),
):
    """
    Test input filtering with LlamaGuard (privacy category) and Azure Content Safety.

    A 400 response from the Orchestration Service indicates the input was correctly blocked.
    """
    content_filter_config = FilteringModuleConfig(
        input=InputFiltering(
            filters=[
                AzureContentSafetyInputFilterConfig(
                    config=AzureContentSafetyInput(
                        hate=AzureThreshold.ALLOW_SAFE,
                        violence=AzureThreshold.ALLOW_SAFE,
                    )
                ),
                LlamaGuard38bFilterConfig(config=LlamaGuard38bFilter(privacy=True)),
            ]
        )
    )
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(template=[UserMessage(content=message)]),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            ),
            filtering=content_filter_config,
        )
    )
    service = OrchestrationService(config=config)
    try:
        service.run()
        raise RuntimeError("Input was not filtered as expected")
    except OrchestrationError as e:
        if e.code == 400:
            return {"result": "Input was filtered as expected."}
        else:
            raise
    finally:
        service.close_http_connection()


def output_filtering(
    message: str = Query(
        default="Reparaphrase the sentence in 30 ways with strong feelings: 'I hate you!'.",
        description="Prompt expected to produce harmful output that will be suppressed.",
    ),
):
    """
    Test output filtering with Azure Content Safety (hate/violence).

    The model response is suppressed if it violates the configured policy.
    """
    content_filter_config = FilteringModuleConfig(
        output=OutputFiltering(
            filters=[
                AzureContentSafetyOutputFilterConfig(
                    config=AzureContentSafetyOutput(
                        hate=AzureThreshold.ALLOW_SAFE,
                        violence=AzureThreshold.ALLOW_SAFE,
                    )
                ),
                LlamaGuard38bFilterConfig(config=LlamaGuard38bFilter(privacy=True)),
            ]
        )
    )
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(template=[UserMessage(content=message)]),
                model=LLMModelDetails(name="anthropic--claude-4.6-sonnet"),
            ),
            filtering=content_filter_config,
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    if result.final_result.choices[0].message.content:
        raise RuntimeError("Output was not filtered as expected")
    else:
        return {"result": "Output was filtered as expected"}


def completion_masking(
    message: str = Query(
        default=(
            "Generate HTML that shows the contact info for Jane Doe, born on 1975-03-05, "
            "living at 10 Downing Street, London UK with email 'jane.doe@mailprovider.com' "
            "and phone number +4902044123221."
        ),
        description="Prompt that may contain PII. PII is pseudonymized before reaching the LLM.",
    ),
    model: str = Query(default="gpt-5.4-nano"),
):
    """
    Run a chat completion with DPI data masking (pseudonymization).

    PII entities (name, address, email, phone, date) are replaced with stable
    pseudonyms before the prompt is sent to the LLM.
    """
    data_masking_config = MaskingModuleConfig(
        providers=[
            MaskingProviderConfig(
                method=MaskingMethod.PSEUDONYMIZATION,
                entities=[
                    DPIStandardEntity(type=ProfileEntity.ADDRESS),
                    DPIStandardEntity(type=ProfileEntity.EMAIL),
                    DPIStandardEntity(type=ProfileEntity.PHONE),
                    DPIStandardEntity(type=ProfileEntity.PERSON),
                    DPICustomEntity(
                        regex="[0-9]{4}[-/][0-9]{2}[-/][0-9]{2}",
                        replacement_strategy=DPIMethodConstant(value="MASKED_DATE"),
                    ),
                ],
            )
        ]
    )
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(template=[UserMessage(content=message)]),
                model=LLMModelDetails(name=model),
            ),
            masking=data_masking_config,
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def reasoning_content(
    message: str = Query(default="What is the longest river on planet earth?"),
    model: str = Query(default="gemini-3.5-flash"),
    reasoning_effort: str = Query(default="high", description="Reasoning effort level: 'low', 'medium', or 'high'."),
):
    """Run a completion with extended reasoning and return both the answer and reasoning content."""
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(template=[UserMessage(content=message)]),
                model=LLMModelDetails(name=model, params={"reasoning_effort": reasoning_effort}),
            )
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {
        "result": result.final_result.choices[0].message.content,
        "reasoning_content": result.final_result.choices[0].message.reasoning_content,
    }


def reasoning_content_stream(
    message: str = Query(default="What is the longest river on planet earth?"),
    model: str = Query(default="gemini-3.5-flash"),
    reasoning_effort: str = Query(default="high"),
):
    """Stream the reasoning content chunks from a high-effort completion."""
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(template=[UserMessage(content=message)]),
                model=LLMModelDetails(name=model, params={"reasoning_effort": reasoning_effort}),
            )
        ),
        stream=GlobalStreamOptions(enabled=True),
    )
    service = OrchestrationService(config=config)

    def generate():
        stream = service.stream()
        for chunk in stream:
            if chunk.final_result:
                rc = chunk.final_result.choices[0].delta.reasoning_content
                if rc:
                    yield "".join([block.content for block in rc])
        service.close_http_connection()

    return StreamingResponse(generate(), media_type="text/plain")


def translation():
    """
    Run a completion with SAP Document Translation on both input and output.

    Input is translated EN→DE before reaching the model; output is translated DE→FR.
    The prompt and language pair are fixed for the demo.
    """
    translation_config = TranslationModuleConfig(
        input=SAPDocumentTranslationInput(
            config=InputTranslationConfig(source_language="en-US", target_language="de-DE")
        ),
        output=SAPDocumentTranslationOutput(
            config=OutputTranslationConfig(source_language="de-DE", target_language="fr-FR")
        ),
    )
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(template=[UserMessage(content="What is the longest river on planet earth?")]),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            ),
            translation=translation_config,
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def sonar_with_citations(
    message: str = Query(default="What are the latest developments in quantum computing?"),
):
    """Run a completion using the Sonar model and return the response with web citations."""
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(template=[UserMessage(content=message)]),
                model=LLMModelDetails(name="sonar"),
            )
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {
        "result": {
            "text": result.final_result.choices[0].message.content,
            "citations": result.final_result.citations,
        }
    }


def embedding(
    text: str = Query(default="Hello World!", description="Text to embed."),
    model: str = Query(default="text-embedding-3-small"),
):
    """Generate a single text embedding vector."""
    embedding_config = EmbeddingsOrchestrationConfig(
        modules=EmbeddingsModuleConfigs(
            embeddings=EmbeddingsModelConfig(model=EmbeddingsModelDetails(name=model))
        )
    )
    service = OrchestrationService()
    response = service.embed(config=embedding_config, input=EmbeddingsInput(text=text))
    service.close_http_connection()
    return {"result": response.final_result.data[0].embedding}


def embedding_batched():
    """
    Generate embeddings for a fixed batch of two texts.

    The input texts are fixed for this demo endpoint:
    ["Hello World!", "This is your captain speaking"]
    """
    embedding_config = EmbeddingsOrchestrationConfig(
        modules=EmbeddingsModuleConfigs(
            embeddings=EmbeddingsModelConfig(model=EmbeddingsModelDetails(name="text-embedding-3-small"))
        )
    )
    service = OrchestrationService()
    response = service.embed(
        config=embedding_config,
        input=EmbeddingsInput(text=["Hello World!", "This is your captain speaking"]),
    )
    service.close_http_connection()
    return {"result": response.final_result.data}


def embedding_masked(
    text: str = Query(
        default="Contact John Smith at john.smith@example.com or call 555-123-4567.",
        description="Text with PII. Person, email, and phone will be anonymized before embedding.",
    ),
):
    """Generate an embedding with PII anonymized before the text reaches the embedding model."""
    embedding_config = EmbeddingsOrchestrationConfig(
        modules=EmbeddingsModuleConfigs(
            embeddings=EmbeddingsModelConfig(model=EmbeddingsModelDetails(name="text-embedding-3-small")),
            masking=MaskingModuleConfig(
                providers=[
                    MaskingProviderConfig(
                        method=MaskingMethod.ANONYMIZATION,
                        entities=[
                            DPIStandardEntity(type=ProfileEntity.PERSON),
                            DPIStandardEntity(type=ProfileEntity.EMAIL),
                            DPIStandardEntity(type=ProfileEntity.PHONE),
                        ],
                    )
                ]
            ),
        )
    )
    service = OrchestrationService()
    response = service.embed(config=embedding_config, input=EmbeddingsInput(text=text))
    service.close_http_connection()
    return {"result": response.final_result.data[0].embedding}


def tool_call_decorator(
    a: int = Query(default=279, description="First operand."),
    b: int = Query(default=929, description="Second operand."),
):
    """
    Run a tool-call completion using the @function_tool decorator.

    The LLM calls add(a, b) and uses the result to answer the question.
    """

    @function_tool
    def add(x: int, y: int) -> int:
        """Add two numbers."""
        return x + y

    question = f"What is {a} + {b}?"
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        SystemMessage(content="You are a helpful AI that performs addition."),
                        UserMessage(content=question),
                    ],
                    tools=[add],
                ),
                model=LLMModelDetails(name="gpt-4o"),
            )
        )
    )
    service = OrchestrationService()
    result = service.run(config=config)
    tool_calls = result.final_result.choices[0].message.tool_calls
    if not tool_calls:
        raise RuntimeError("Unexpectedly no tool calls in response")

    history = list(result.intermediate_results.templating or [])
    history.append(result.final_result.choices[0].message)
    for tc in tool_calls:
        args = tc.function.parse_arguments()
        tool_result = add.execute(**args)
        history.append(ToolChatMessage(content=str(tool_result), tool_call_id=tc.id))

    result = service.run(config=config, history=history)
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def tool_call_function_tool(
    a: int = Query(default=279, description="First operand."),
    b: int = Query(default=929, description="Second operand."),
):
    """
    Run a tool-call completion using the FunctionTool class.

    Equivalent to tool_call_decorator but uses explicit FunctionTool construction.
    """

    def add(x: int, y: int) -> int:
        """Add two numbers."""
        return x + y

    add_tool = FunctionTool(
        function=FunctionObject(
            name="add",
            description="Add two numbers.",
            parameters={
                "type": "object",
                "properties": {
                    "x": {"type": "number", "description": "First operand."},
                    "y": {"type": "number", "description": "Second operand."},
                },
                "required": ["x", "y"],
                "additionalProperties": False,
            },
            strict=True,
            function=add,
        )
    )

    question = f"What is {a} + {b}?"
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        SystemMessage(content="You are a helpful AI that performs addition."),
                        UserMessage(content=question),
                    ],
                    tools=[add_tool],
                ),
                model=LLMModelDetails(name="gpt-4o"),
            )
        )
    )
    service = OrchestrationService()
    result = service.run(config=config)
    tool_calls = result.final_result.choices[0].message.tool_calls
    if tool_calls is None:
        raise RuntimeError("Unexpectedly no tool calls in response")

    history = list(result.intermediate_results.templating or [])
    history.append(result.final_result.choices[0].message)
    for tc in tool_calls:
        tool_result = add_tool.execute(**tc.function.parse_arguments())
        history.append(ToolChatMessage(content=str(tool_result), tool_call_id=tc.id))

    result = service.run(config=config, history=history)
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def tool_call_json(
    a: int = Query(default=279, description="First operand."),
    b: int = Query(default=929, description="Second operand."),
):
    """
    Run a tool-call completion using a raw JSON tool schema dict.

    Useful when the tool does not map to a local Python function.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add",
                "description": "Add two numbers.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First operand."},
                        "b": {"type": "number", "description": "Second operand."},
                    },
                    "required": ["a", "b"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }
    ]
    question = f"What is {a} + {b}?"
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        SystemMessage(content="You are a helpful AI that performs addition."),
                        UserMessage(content=question),
                    ],
                    tools=tools,
                ),
                model=LLMModelDetails(name="gpt-4o"),
            )
        )
    )
    service = OrchestrationService()
    result = service.run(config=config)
    tool_calls = result.final_result.choices[0].message.tool_calls
    if tool_calls is None:
        raise RuntimeError("Unexpectedly no tool calls in response")

    history = list(result.intermediate_results.templating or [])
    history.append(result.final_result.choices[0].message)
    for tc in tool_calls:
        tool_result = sum(tc.function.parse_arguments().values())
        history.append(ToolChatMessage(content=str(tool_result), tool_call_id=tc.id))

    result = service.run(config=config, history=history)
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}
