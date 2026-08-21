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
    TranslationModuleConfig,
    UserMessage,
)


def completion():
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


def completion_stream():
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


def reasoning_effort():
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        UserMessage(content="Explain step by step: what is 15 * 17?")
                    ]
                ),
                model=LLMModelDetails(
                    name="gemini-3.5-flash", params={"reasoning_effort": "high"}
                ),
            )
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return {"result": result.final_result.choices[0].message.content}


def message_history():
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
            return {"info": "input was filtered as expected"}
        else:
            raise


def output_filtering():
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
        return {"info": "output was filtered as expected"}


def completion_masking():
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
        "result": result.final_result.choices[0].message.content,
        "citations": result.final_result.citations,
    }


def embedding():
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
