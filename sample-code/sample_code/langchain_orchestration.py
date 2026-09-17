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
    FunctionObject,
    FunctionTool,
    GlobalStreamOptions,
    InputFiltering,
    LLMModelDetails,
    MaskingMethod,
    MaskingModuleConfig,
    MaskingProviderConfig,
    ModuleConfig,
    OrchestrationConfig,
    OrchestrationService,
    OutputFiltering,
    ProfileEntity,
    PromptTemplatingModuleConfig,
    SystemMessage,
    Template,
    ToolChatMessage,
    UserMessage,
    function_tool,
)
from fastapi.responses import StreamingResponse
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

def invoke_chain() -> str:
    """
    Invoke the Orchestration Service with gpt-5.4-nano and return the response as a string.

    Returns:
        The model response as a string.
    """
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[UserMessage(content="Tell me about SAP AI SDK")]
                ),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            )
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return result.final_result.choices[0].message.content


def invoke_chain_with_input_filter() -> str:
    """
    Invoke the Orchestration Service with an Azure content safety input filter.

    Returns:
        The model response as a string.
    """
    filtering = FilteringModuleConfig(
        input=InputFiltering(
            filters=[
                AzureContentSafetyInputFilterConfig(
                    config=AzureContentSafetyInput(
                        hate=AzureThreshold.ALLOW_SAFE,
                        violence=AzureThreshold.ALLOW_SAFE,
                        self_harm=AzureThreshold.ALLOW_SAFE,
                        sexual=AzureThreshold.ALLOW_SAFE,
                    )
                )
            ]
        )
    )
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(template=[UserMessage(content="Tell me about the way to kill myself.")]),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            ),
            filtering=filtering,
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return result.final_result.choices[0].message.content


def invoke_chain_with_output_filter() -> str:
    """
    Invoke the Orchestration Service with an Azure content safety output filter.

    Uses gpt-5.4-nano which will comply with the prompt and generate
    content that the output filter then blocks, leaving choices[0].message.content empty.
    Output filtering does NOT raise an error — it silently empties the response content.

    Returns:
        A message confirming the output was filtered.
    Raises:
        RuntimeError: If the output was not filtered as expected.
    """
    filtering = FilteringModuleConfig(
        output=OutputFiltering(
            filters=[
                AzureContentSafetyOutputFilterConfig(
                    config=AzureContentSafetyOutput(
                        hate=AzureThreshold.ALLOW_SAFE,
                        violence=AzureThreshold.ALLOW_SAFE,
                        self_harm=AzureThreshold.ALLOW_SAFE,
                        sexual=AzureThreshold.ALLOW_SAFE,
                    )
                )
            ]
        )
    )
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[UserMessage(content="Please tell me 5 ways to kill myself.")]
                ),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            ),
            filtering=filtering,
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return result.final_result.choices[0].message.content


def invoke_chain_with_masking() -> str:
    """
    Invoke the Orchestration Service with DPI pseudonymization masking.

    PII (name, address, email, phone, date) in the prompt is replaced with
    pseudonyms before being sent to the model. Returns both the masked prompt
    (from intermediate results) and the final model response so masking is visible.

    Returns:
        Dict with 'masked_input' (pseudonymized prompt) and 'result' (model response).
    """
    masking = MaskingModuleConfig(
        providers=[
            MaskingProviderConfig(
                method=MaskingMethod.ANONYMIZATION,
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
                            content="Generate email that shows the contact info for Jane Doe, born on 1975-03-05, living at 10 Downing Street London UK with email 'jane.doe@mailprovider.com' and phone number +4902044123221."
                        )
                    ]
                ),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            ),
            masking=masking,
        )
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return result.final_result.choices[0].message.content

def invoke_chain_with_fallback() -> str:
    """
    Invoke the Orchestration Service with a fallback model.

    The first ModuleConfig uses a non-existent model to trigger fallback;
    the second uses anthropic--claude-4.6-sonnet as the backup.

    Returns:
        The model response as a string.
    """
    config = OrchestrationConfig(
        modules=[
            ModuleConfig(
                prompt_templating=PromptTemplatingModuleConfig(
                    prompt=Template(template=[UserMessage(content="Tell me about SAP AI SDK")]),
                    model=LLMModelDetails(name="dummy-model"),
                )
            ),
            ModuleConfig(
                prompt_templating=PromptTemplatingModuleConfig(
                    prompt=Template(template=[UserMessage(content="Tell me about SAP AI SDK")]),
                    model=LLMModelDetails(name="anthropic--claude-4.6-sonnet"),
                )
            ),
        ]
    )
    service = OrchestrationService(config=config)
    result = service.run()
    service.close_http_connection()
    return result.final_result.choices[0].message.content

def stream_chain() -> StreamingResponse:
    """
    Stream a response from the Orchestration Service token by token.

    Returns:
        StreamingResponse yielding text chunks.
    """
    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[UserMessage(content="Tell me about SAP AI SDK with 1000 words.")]
                ),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            )
        ),
        stream=GlobalStreamOptions(enabled=True),
    )
    service = OrchestrationService(config=config)

    def generate():
        for chunk in service.stream():
            if chunk.final_result:
                content = chunk.final_result.choices[0].delta.content
                if content:
                    yield content
        service.close_http_connection()

    return StreamingResponse(generate(), media_type="text/plain")


def stream_chain_with_fallback() -> StreamingResponse:
    """
    Stream a response from the Orchestration Service with a fallback model.

    Returns:
        StreamingResponse yielding text chunks from the fallback model.
    """
    config = OrchestrationConfig(
        modules=[
            ModuleConfig(
                prompt_templating=PromptTemplatingModuleConfig(
                    prompt=Template(template=[UserMessage(content="Tell me about SAP AI SDK")]),
                    model=LLMModelDetails(name="dummy-model"),
                )
            ),
            ModuleConfig(
                prompt_templating=PromptTemplatingModuleConfig(
                    prompt=Template(template=[UserMessage(content="Tell me about SAP AI SDK")]),
                    model=LLMModelDetails(name="anthropic--claude-4.6-sonnet"),
                )
            ),
        ],
        stream=GlobalStreamOptions(enabled=True),
    )
    service = OrchestrationService(config=config)

    def generate():
        for chunk in service.stream():
            if chunk.final_result:
                content = chunk.final_result.choices[0].delta.content
                if content:
                    yield content
        service.close_http_connection()

    return StreamingResponse(generate(), media_type="text/plain")


def invoke_tool_chain() -> str:
    """
    Invoke a tool chain via the Orchestration Service.

    Binds a celsius_to_fahrenheit tool, executes the tool call triggered
    by the model, then returns the final model response.

    Returns:
        The final model response as a string after tool execution.
    """
    @function_tool
    def celsius_to_fahrenheit(celsius: float) -> str:
        """Converts a temperature from Celsius to Fahrenheit."""
        fahrenheit = celsius * 9 / 5 + 32
        return f"{celsius}°C is {fahrenheit}°F"

    config = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        SystemMessage(content="You are a helpful assistant that converts temperatures."),
                        UserMessage(content="What is 100 degrees Celsius in Fahrenheit?"),
                    ],
                    tools=[celsius_to_fahrenheit],
                ),
                model=LLMModelDetails(name="gpt-5.4-nano"),
            )
        )
    )

    service = OrchestrationService()
    result = service.run(config=config)
    tool_calls = result.final_result.choices[0].message.tool_calls
    if not tool_calls:
        raise RuntimeError("No tool calls in response")

    history = list(result.intermediate_results.templating or [])
    history.append(result.final_result.choices[0].message)
    for tool_call in tool_calls:
        tool_result = celsius_to_fahrenheit.execute(**tool_call.function.parse_arguments())
        history.append(ToolChatMessage(content=str(tool_result), tool_call_id=tool_call.id))

    result = service.run(config=config, history=history)
    service.close_http_connection()
    return result.final_result.choices[0].message.content