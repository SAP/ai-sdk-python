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
    FilteringModuleConfig,
    GlobalStreamOptions,
    ImageItem,
    InputFiltering,
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
    ProfileEntity,
    PromptTemplatingModuleConfig,
    Template,
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
