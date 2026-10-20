from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

from gen_ai_hub.proxy.core import get_proxy_client
from gen_ai_hub.proxy.core.base import BaseDeployment, BaseProxyClient

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings
    from langchain_core.language_models import BaseLanguageModel


def default_f_select_deployment(proxy_client: BaseProxyClient,
                                **model_identification_kwargs: Dict[str, str]) -> BaseDeployment:
    """Default function to select a deployment based on model identification kwargs.

    :param proxy_client: The proxy client to use for selecting the deployment
    :type proxy_client: BaseProxyClient
    :return: The selected deployment
    :rtype: BaseDeployment
    """
    return proxy_client.select_deployment(**model_identification_kwargs)


def handle_model_args_kwargs(proxy_client, args: List[Any], kwargs: Dict[str, Any]):
    """Handles model identification arguments and keyword arguments.

    :param proxy_client: the proxy client to use for model identification
    :type proxy_client: _type_
    :param args: list of positional arguments
    :type args: List[Any]
    :param kwargs: dictionary of keyword arguments
    :type kwargs: Dict[str, Any]
    :raises ValueError: if no model identification argument is provided
    :return: A tuple containing the model name, model identification kwargs, and remaining kwargs
    :rtype: Tuple[str, Dict[str, str], Dict[str, Any]]
    """
    main_kwarg = proxy_client.deployment_class.get_main_model_identification_kwargs()
    kwarg_names = proxy_client.deployment_class.get_model_identification_kwargs()
    if args:
        model_name = args[0]
        kwargs[main_kwarg] = model_name
    elif main_kwarg in kwargs:
        model_name = kwargs[main_kwarg]
    else:
        raise ValueError('No model identification argument provided')
    model_identification_kwargs = {n: kwargs[n] for n in kwarg_names if n in kwargs}
    return model_name, model_identification_kwargs, kwargs


class ModelType(Enum):
    LLM = auto()
    EMBEDDINGS = auto()


def _init_custom_model(proxy_client: BaseProxyClient, init_func: Callable, args: List[Any], kwargs: Dict[str, Any],
                       model_kwargs: Dict[str, Any]):
    proxy_client = proxy_client or get_proxy_client()
    model_name, model_identification_kwargs, kwargs = handle_model_args_kwargs(proxy_client=proxy_client, args=args,
                                                                               kwargs=kwargs)

    try:
        deployment = default_f_select_deployment(proxy_client, **model_identification_kwargs)
    except ValueError:
        proxy_client.update_deployments()
        deployment = default_f_select_deployment(proxy_client, **model_identification_kwargs)
    return init_func(proxy_client=proxy_client, deployment=deployment, **model_kwargs)


def _import_provider(model_name: str, module: str, distribution: str):
    """Lazily import a provider's langchain wrapper module.

    Providers ship in separate distributions (``sap-ai-sdk-openai``,
    ``sap-ai-sdk-amazon``, ``sap-ai-sdk-google``), each with an optional
    ``[langchain]`` extra. Import the wrapper only when a matching model is
    actually requested, and raise an actionable error if it is missing.

    :param model_name: the requested model name (for the error message)
    :param module: the dotted path of the provider's langchain wrapper module
    :param distribution: the pip distribution (with extra) that provides it
    :return: the imported wrapper module
    """
    import importlib
    try:
        return importlib.import_module(module)
    except ImportError as exc:
        raise ImportError(
            f"Model '{model_name}' requires the '{distribution}' package. "
            f"Install it with `pip install '{distribution}'`."
        ) from exc


def _get_init_func(model_name: str, model_type: ModelType):
    if any(model_name.startswith(prefix) for prefix in ['amazon', 'anthropic']):
        provider = _import_provider(
            model_name, 'gen_ai_hub.proxy.native.amazon.langchain', 'sap-ai-sdk-amazon[langchain]')
    elif any(model_name.startswith(prefix) for prefix in ['google', 'gemini']):
        provider = _import_provider(
            model_name, 'gen_ai_hub.proxy.native.google_genai.langchain', 'sap-ai-sdk-google[langchain]')
    else:
        provider = _import_provider(
            model_name, 'gen_ai_hub.proxy.native.openai.langchain', 'sap-ai-sdk-openai[langchain]')
    if model_type == ModelType.EMBEDDINGS:
        return provider.init_embedding_model
    return provider.init_chat_model



def _init_model(proxy_client: Optional[BaseProxyClient],
                model_type: ModelType,
                args: List[Any],
                kwargs: Dict[str, Any],
                init_func: Optional[Callable] = None,
                model_kwargs: Optional[Dict[str, Any]] = None):
    proxy_client = proxy_client or get_proxy_client()
    model_kwargs = model_kwargs or {}
    if init_func:
        return _init_custom_model(proxy_client=proxy_client, init_func=init_func, args=args, kwargs=kwargs,
                                  model_kwargs=model_kwargs)
    model_name, model_identification_kwargs, kwargs = handle_model_args_kwargs(proxy_client=proxy_client, args=args,
                                                                               kwargs=kwargs)
    init_func = _get_init_func(model_name, model_type)
    deployment = default_f_select_deployment(proxy_client, **model_identification_kwargs)
    return init_func(proxy_client=proxy_client, deployment=deployment, **model_kwargs)


def init_llm(*args,
             proxy_client: Optional[BaseProxyClient] = None,
             temperature: float = 0.0,
             max_tokens: int = 256,
             top_k: Optional[int] = None,
             top_p: float = 1.,
             init_func: Optional[Callable] = None,
             model_id: Optional[str] = '',
             **kwargs) -> BaseLanguageModel:
    """
    Initializes a language model using the specified parameters.

    :param proxy_client: The proxy client to use for the model (optional)
    :type proxy_client: ProxyClient
    :param temperature: The temperature parameter for model generation (default: 0.0)
    :type temperature: float
    :param max_tokens: The maximum number of tokens to generate (default: 256)
    :type max_tokens: int
    :param top_k: The top-k parameter for model generation (optional)
    :type top_k: int
    :param top_p: The top-p parameter for model generation (default: 1.0)
    :type top_p: float
    :param init_func: Function to call for initializing the model, optional
    :type init_func: Callable
    :param model_id: id of the Amazon Bedrock model, needed in case a custom Amazon Bedrock model is being
                     initiated (optional)
    :type model_id: str
    :return: The initialized language model
    :rtype: BaseLanguageModel
    """
    model_kwargs = {
        'temperature': temperature,
        'max_tokens': max_tokens,
        'top_k': top_k,
        'top_p': top_p,
    }
    if model_id:
        model_kwargs['model_id'] = model_id
    if 'config' in kwargs:
        model_kwargs['config'] = kwargs["config"]
    return _init_model(args=args,
                       proxy_client=proxy_client,
                       model_type=ModelType.LLM,
                       model_kwargs=model_kwargs,
                       init_func=init_func,
                       kwargs=kwargs)


def init_embedding_model(*args,
                         proxy_client: Optional[BaseProxyClient] = None,
                         init_func: Optional[Callable] = None,
                         model_id: Optional[str] = '',
                         **kwargs) -> Embeddings:
    """
    Initializes an embedding model using the specified parameters.

    :param proxy_client: The proxy client to use for the model (optional)
    :type proxy_client: BaseProxyClient
    :param init_func: Function to call for initializing the model, optional
    :type init_func: Callable
    :param model_id: id of the Amazon Bedrock model, needed in case a custom Amazon Bedrock model is being
                     initiated (optional)
    :type model_id: str
    :return: The initialized embedding model
    :rtype: Embeddings
    """
    model_kwargs = {}
    if model_id:
        model_kwargs['model_id'] = model_id
    return _init_model(args=args,
                       proxy_client=proxy_client,
                       model_type=ModelType.EMBEDDINGS,
                       model_kwargs=model_kwargs,
                       init_func=init_func,
                       kwargs=kwargs)
