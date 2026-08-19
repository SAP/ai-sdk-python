from fastapi.responses import StreamingResponse
from gen_ai_hub.orchestration_v2 import (
    GlobalStreamOptions,
    ImageItem,
    LLMModelDetails,
    ModuleConfig,
    OrchestrationConfig,
    OrchestrationService,
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


# from fastapi.responses import StreamingResponse
# from gen_ai_hub.orchestration.models.azure_content_filter import (
#     AzureContentFilter,
#     AzureThreshold,
# )
# from gen_ai_hub.orchestration.models.config import OrchestrationConfig

# from gen_ai_hub.orchestration.models.content_filtering import (
#     ContentFiltering,
#     InputFiltering,
#     OutputFiltering,
# )
# from gen_ai_hub.orchestration.models.llm import LLM
# from gen_ai_hub.orchestration.models.message import (
#     AssistantMessage,
#    SystemMessage,
#    UserMessage,
# )

# from gen_ai_hub.orchestration.models.template import Template, TemplateValue
# from gen_ai_hub.orchestration.service import OrchestrationService

# def input_filtering():
#     azure_filter = AzureContentFilter(
#         hate=AzureThreshold.ALLOW_SAFE,
#         sexual=AzureThreshold.ALLOW_SAFE,
#         violence=AzureThreshold.ALLOW_SAFE,
#         self_harm=AzureThreshold.ALLOW_SAFE,
#     )
#     config = OrchestrationConfig(
#         template=Template(
#             messages=[
#                 SystemMessage("You are a helpful assistant."),
#                 UserMessage("Tell me a fun fact about elephants."),
#             ]
#         ),
#         llm=_LLM,
#         filtering=ContentFiltering(
#             input_filtering=InputFiltering(filters=[azure_filter])
#         ),
#     )
#     service = OrchestrationService(config=config)
#     response = service.run()
#     return {"content": response.content}
#
#
# def output_filtering():
#     azure_filter = AzureContentFilter(
#         hate=AzureThreshold.ALLOW_SAFE,
#         sexual=AzureThreshold.ALLOW_SAFE,
#         violence=AzureThreshold.ALLOW_SAFE,
#         self_harm=AzureThreshold.ALLOW_SAFE,
#     )
#     config = OrchestrationConfig(
#         template=Template(
#             messages=[
#                 SystemMessage("You are a helpful assistant."),
#                 UserMessage("Tell me a fun fact about dolphins."),
#             ]
#         ),
#         llm=_LLM,
#         filtering=ContentFiltering(
#             output_filtering=OutputFiltering(filters=[azure_filter])
#         ),
#     )
#     service = OrchestrationService(config=config)
#     response = service.run()
#     return {"content": response.content}
