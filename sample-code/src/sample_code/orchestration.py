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


def completion():
    """
    Run chat example through the Orchestration Service API.

    Returns:
        JSON object containing the model response as result.
    """
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        UserMessage(
                            content="What is the longest river on planet earth?"
                        )
                    ]
                ),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            )
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


async def completion_async():
    """
    Run async chat example through the Orchestration Service API.

    Returns:
        JSON object containing the model response as result.
    """
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        UserMessage(
                            content="What is the longest river on planet earth?"
                        )
                    ]
                ),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            )
        )
    )
    service = OrchestrationService(config=config)
    result = await service.arun()
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def completion_stream():
    """
    Run chat example with a streaming response through the Orchestration Service API.

    Returns:
        JSON object containing the model response as result.
    """
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        UserMessage(
                            content="What is the longest river on planet earth?"
                        )
                    ]
                ),
                model=LLMModelDetails(name="gpt-5.4-nano"),
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

    return StreamingResponse(generate(), media_type="text/event-stream")


def completion_json():
    """
    Run chat example with structured output (JSON) through the Orchestration Service API.

    Returns:
        JSON object containing the model response as result.
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
                    # setting ResponseFormatJsonObject() enables JSON responses without a fixed schema
                    response_format=ResponseFormatJsonSchema(
                        json_schema=JSONResponseSchema(
                            name="person",
                            description="person mapping",
                            schema=json_schema,
                        )
                    ),
                ),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            )
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def completion_template():
    """
    Run chat example with a template including placeholders through the Orchestration Service API.

    Returns:
        JSON object containing the model response as result.
    """
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        # add placeholder by wrapping it with {{?...}}
                        UserMessage(content="What is the capital of {{?country}}?")
                    ]
                ),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            )
        )
    )
    service = OrchestrationService(config=config)
    # provide placeholder values
    result = service.run(placeholder_values={"country": "Denmark"})
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def completion_with_fallback():
    """
    Run chat example with fallback configurations through the Orchestration Service API.

    Returns:
        JSON object containing the model response as result.
    """
    config = OrchestrationConfig(
        modules=[
            # Trigger fallback with non-orchestration model
            ModuleConfig(
                prompt_templating=PromptTemplatingModuleConfig(
                    prompt=Template(
                        template=[
                            UserMessage(
                                content="What is the longest river on planet earth?"
                            )
                        ]
                    ),
                    model=LLMModelDetails(name="sap-rpt-1-small"),
                )
            ),
            # Second configuration will succeed
            ModuleConfig(
                prompt_templating=PromptTemplatingModuleConfig(
                    prompt=Template(
                        template=[
                            UserMessage(
                                content="What is the longest river on planet earth?"
                            )
                        ]
                    ),
                    model=LLMModelDetails(name="anthropic--claude-4.5-haiku"),
                )
            ),
        ]
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def completion_abap():
    """
    Run chat example with SAP ABAP through the Orchestration Service API.

    Returns:
        JSON object containing the model response as result.
    """
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        UserMessage(
                            content="Explain the concept of internal tables in ABAP"
                        )
                    ]
                ),
                model=LLMModelDetails(name="sap-abap-1"),
            )
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def message_history():
    """
    Run chat example with message history through the Orchestration Service API.

    Returns:
        JSON object containing the model response as result.
    """
    # the service can also be started without providing a default config
    # in this case, each call to service.run has to pass a config to use
    service = OrchestrationService()
    first_config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[UserMessage(content="What is the capital of France?")]
                ),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            )
        )
    )

    first_response = service.run(config=first_config)
    # first_response.intermediate_results.templating contains the history including the one that was passed in (here this part is still empty)
    history = first_response.intermediate_results.templating or []
    history.append(first_response.final_result.choices[0].message)

    second_config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[UserMessage(content="What is the typical food there?")]
                ),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            )
        )
    )
    second_response = service.run(config=second_config, history=history)
    service.close_http_connection()
    return {"result": second_response.final_result.choices[0].message.content}


def completion_image():
    """
    Run multimodal example with image input through the Orchestration Service API.

    Returns:
        JSON object containing the model response as result.
    """
    # First option: load image from a standard, publicly accessible url
    image = ImageItem(url="https://picsum.photos/id/1/200/300")
    # Second option: pass the image content as base64-encoded data url
    # with the format "data:[<mediatype>][;base64],<data>"
    # image = ImageItem(
    #    url="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAIAAAACUFjqAAAAE0lEQVR4nGP8z4APMOGVZRip0gBBLAETee26JgAAAABJRU5ErkJggg=="
    # )
    # Third option: load the image from a local file path
    # try:
    #     image = ImageItem.from_file("path/to/your/local/image.jpeg")
    # except FileNotFoundError:
    #     print("Error: The specified image file was not found.")
    # except Exception as e:
    #     print(f"An error occurred while loading the image: {e}")
    multimodal_content = [image, "What objects are prominent in this image?"]
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        # add placeholder by wrapping it with {{?...}}
                        UserMessage(content=multimodal_content)
                    ]
                ),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            )
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def input_filtering():
    """
    Run input filtering example through the Orchestration Service API.

    Returns:
        JSON object containing a message confirming successful filtering.
    Raises:
        RuntimeError: Raised if the filtering is unsuccesful.
    """
    content_filter_config = FilteringModuleConfig(
        input=InputFiltering(
            filters=[
                AzureContentSafetyInputFilterConfig(
                    # only safe content allowed for hate and violence
                    config=AzureContentSafetyInput(
                        hate=AzureThreshold.ALLOW_SAFE,
                        violence=AzureThreshold.ALLOW_SAFE,
                    )
                ),
                # category 'privacy' enabled
                LlamaGuard38bFilterConfig(config=LlamaGuard38bFilter(privacy=True)),
            ]
        )
    )
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        UserMessage(
                            # should be filtered by Llama Guard
                            content="My social insurance number is ABC123456789."
                        )
                    ]
                ),
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
            service.close_http_connection()
            return {"result": "Input was filtered as expected."}
        else:
            raise


def output_filtering():
    """
    Run output filtering example through the Orchestration Service API.

    Returns:
        JSON object containing a message confirming successful filtering.
    Raises:
        RuntimeError: Raised if the filtering is unsuccesful.
    """
    content_filter_config = FilteringModuleConfig(
        output=OutputFiltering(
            filters=[
                AzureContentSafetyOutputFilterConfig(
                    # only safe content allowed for hate and violence
                    config=AzureContentSafetyOutput(
                        hate=AzureThreshold.ALLOW_SAFE,
                        violence=AzureThreshold.ALLOW_SAFE,
                    )
                ),
                # category 'privacy' enabled
                LlamaGuard38bFilterConfig(config=LlamaGuard38bFilter(privacy=True)),
            ]
        )
    )
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        UserMessage(
                            # should be filtered by Azure content filter
                            content="Reparaphrase the sentence in 30 ways with strong feelings: 'I hate you!'."
                        )
                    ]
                ),
                model=LLMModelDetails(name="anthropic--claude-4.5-haiku"),
            ),
            filtering=content_filter_config,
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    # should be filtered by the Azure content filter, hence content should be empty
    if result.final_result.choices[0].message.content:
        raise RuntimeError("Output was not filtered as expected")
    else:
        return {"result": "Output was filtered as expected"}


def completion_masking():
    """
    Run masked (pseudonymized) chat example through the Orchestration Service API.

    Returns:
        JSON object containing the model response as result.
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
                prompt=Template(
                    template=[
                        UserMessage(
                            content="Generate HTML that shows the contact info for Jane Doe, born on 1975-03-05, living at 10 Downing Street, London UK with email 'jane.doe@mailprovider.com' and phone number +4902044123221."
                        )
                    ]
                ),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            ),
            masking=data_masking_config,
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def translation():
    """
    Run chat example with prompt and output translation through the Orchestration Service API.

    Returns:
        JSON object containing the model response as result.
    """
    translation_config = TranslationModuleConfig(
        input=SAPDocumentTranslationInput(
            config=InputTranslationConfig(
                source_language="en-US", target_language="de-DE"
            )
        ),
        output=SAPDocumentTranslationOutput(
            config=OutputTranslationConfig(
                source_language="de-DE", target_language="fr-FR"
            )
        ),
    )
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        UserMessage(
                            content="What is the longest river on planet earth?"
                        )
                    ]
                ),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            ),
            translation=translation_config,
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def sonar_with_citations():
    """
    Run chat example with citations (Sonar model) through the Orchestration Service API.

    Returns:
        JSON object containing the model response (text and citations) as result.
    """
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        UserMessage(
                            content="What are the latest developments in quantum computing?"
                        )
                    ]
                ),
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


def embedding():
    """
    Run embedding example through the Orchestration Service API.

    Returns:
        JSON object containing the embedding as result.
    """
    embdding_config = EmbeddingsOrchestrationConfig(
        modules=EmbeddingsModuleConfigs(
            embeddings=EmbeddingsModelConfig(
                model=EmbeddingsModelDetails(name="text-embedding-3-small")
            )
        )
    )

    service = OrchestrationService()
    response = service.embed(
        config=embdding_config, input=EmbeddingsInput(text="Hello World!")
    )
    return {"result": response.final_result.data[0].embedding}


def embedding_batched():
    """
    Run masked (anonymized )embedding example through the Orchestration Service API.

    Returns:
        JSON object containing the embedding as result.
    """
    embdding_config = EmbeddingsOrchestrationConfig(
        modules=EmbeddingsModuleConfigs(
            embeddings=EmbeddingsModelConfig(
                model=EmbeddingsModelDetails(name="text-embedding-3-small")
            )
        )
    )

    input_list = ["Hello World!", "This is your captain speaking"]

    service = OrchestrationService()
    response = service.embed(
        config=embdding_config, input=EmbeddingsInput(text=input_list)
    )
    return {"result": response.final_result.data}


def embedding_masked():
    embdding_config = EmbeddingsOrchestrationConfig(
        modules=EmbeddingsModuleConfigs(
            embeddings=EmbeddingsModelConfig(
                model=EmbeddingsModelDetails(name="text-embedding-3-small")
            ),
            masking=MaskingModuleConfig(
                masking_providers=[
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
    response = service.embed(
        config=embdding_config,
        input=EmbeddingsInput(
            text="Contact John Smith at john.smith@example.com or call 555-123-4567."
        ),
    )
    return {"result": response.final_result.data[0].embedding}


def tool_call_decorator():
    """
    Run chat example with tool calls using the `function_tool` decorator through the Orchestration Service API.

    Returns:
        JSON object containing the model response as result.
    """

    @function_tool
    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    tools = [add]

    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        SystemMessage(
                            content="You are a helpful AI that performs the addition of two numbers."
                        ),
                        UserMessage(content="What is 279 + 929?"),
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
    for tool_call in tool_calls:
        if tool_call.function.name != "add":
            raise RuntimeError(
                f"Unexpectedly called '{tool_call.function.name}' instead of 'add'"
            )
        result = add.execute(**tool_call.function.parse_arguments())
        tool_message = ToolChatMessage(content=str(result), tool_call_id=tool_call.id)
        history.append(tool_message)

    result = service.run(config=config, history=history)
    return {"result": result.final_result.choices[0].message.content}


def tool_call_function_tool():
    """
    Run chat example with tool calls using the `FunctionTool` class through the Orchestration Service API.

    Returns:
        JSON object containing the model response as result.
    """

    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    add_tool = FunctionTool(
        function=FunctionObject(
            name="add",
            description="Add two numbers.",
            parameters={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First operand of the addition function",
                    },
                    "b": {
                        "type": "number",
                        "description": "Second operand of the addition function",
                    },
                },
                "required": ["a", "b"],
                "additionalProperties": False,
            },
            strict=True,
            function=add,
        )
    )

    tools = [add_tool]
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        SystemMessage(
                            content="You are a helpful AI that performs the addition of two numbers."
                        ),
                        UserMessage(content="What is 279 + 929?"),
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
    for tool_call in tool_calls:
        if tool_call.function.name != "add":
            raise RuntimeError(
                f"Unexpectedly called '{tool_call.function.name}' instead of 'add'"
            )
        result = add_tool.execute(**tool_call.function.parse_arguments())
        tool_message = ToolChatMessage(content=str(result), tool_call_id=tool_call.id)
        history.append(tool_message)

    result = service.run(config=config, history=history)
    return {"result": result.final_result.choices[0].message.content}


def tool_call_json():
    """
    Run chat example with tool calls using a JSON schema dictionary through the Orchestration Service API.

    Returns:
        JSON object containing the model response as result.
    """
    # this is helpful if the tool call doesn't map to a Python function
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add",
                "description": "Add two numbers.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "First operand of the addition function",
                        },
                        "b": {
                            "type": "number",
                            "description": "Second operand of the addition function",
                        },
                    },
                    "required": ["a", "b"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }
    ]
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        SystemMessage(
                            content="You are a helpful AI that performs the addition of two numbers."
                        ),
                        UserMessage(content="What is 279 + 929?"),
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
    for tool_call in tool_calls:
        if tool_call.function.name != "add":
            raise RuntimeError(
                f"Unexpectedly called '{tool_call.function.name}' instead of 'add'"
            )
        result = sum(tool_call.function.parse_arguments().values())
        tool_message = ToolChatMessage(content=str(result), tool_call_id=tool_call.id)
        history.append(tool_message)

    result = service.run(config=config, history=history)
    return {"result": result.final_result.choices[0].message.content}
