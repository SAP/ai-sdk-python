from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Union

from langchain_core.embeddings import Embeddings  # pylint: disable=import-error, no-name-in-module
from langchain_core.language_models import BaseLanguageModel

from gen_ai_hub.proxy.core import get_proxy_client
from gen_ai_hub.proxy.core.base import BaseDeployment, BaseProxyClient
from gen_ai_hub.proxy.core.proxy_clients import proxy_clients


@dataclass
class RegisterDeployment:
    """Registry entry for a model deployment."""
    model: Union[BaseLanguageModel, Embeddings]
    init_func: Callable
    # for some Deployments different models are coming from the same deployment but require different parameters
    # Therefore, the model name can not be used to identify the deployment
    # For example:
    #     anthropic-direct-claude-instant-1/anthropic-direct-claude-2
    #     We want to be able to instantiate them like this init_llm('anthropic-direct-claude-instant-1')/init_llm('anthropic-direct-claude-2')
    #     But we have to call Bedrock/BedrockChat(deployment_id='anthropic-direct', model_kwargs={'model': 'claude-2'/'claude-instant-1'})
    # To solve this a custom func to select the correct deployment can be used
    f_select_deployment: Optional[Callable[[BaseProxyClient, Dict[str, str]], BaseDeployment]] = None


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


@dataclass
class RetrievalResult:
    """Result of retrieving a model from the catalog."""
    proxy_client: BaseProxyClient
    deployment: BaseDeployment
    registry_entry: RegisterDeployment


class Catalog:
    """Catalog for registering and retrieving model deployments."""
    def __init__(self):    
        self.models = defaultdict(lambda: {ModelType.LLM: {}, ModelType.EMBEDDINGS: {}})

    def register(self, proxy_client, base_class, *model_names, f_select_deployment: Optional[Callable] = None):
        """Registers a model deployment in the catalog.

        :param proxy_client: the proxy client to register the model for
        :type proxy_client: Union[str, BaseProxyClient]
        :param base_class: the base class of the model (LLM or Embeddings)
        :type base_class: Type[Union[BaseLanguageModel, Embeddings]]
        :param f_select_deployment: function to select the deployment, defaults to None
        :type f_select_deployment: Optional[Callable], optional
        :raises TypeError: if the base class is not supported
        :return: Decorator function for registering the model
        :rtype: Callable
        """
        if isinstance(proxy_client, str):
            proxy_client_name = proxy_client
        else:
            proxy_client_name = proxy_clients.get_proxy_cls_name(proxy_client)
        client_models = self.models[proxy_client_name]
        if issubclass(base_class, BaseLanguageModel):
            model_type = ModelType.LLM
        elif issubclass(base_class, Embeddings):
            model_type = ModelType.EMBEDDINGS
        else:
            raise TypeError('Tried to register unsupported class')

        def wrapper(func):
            for model_name in model_names:
                client_models[model_type][model_name] = RegisterDeployment(model=base_class, init_func=func,
                                                                           f_select_deployment=f_select_deployment)
            return func

        return wrapper

    def _get_registry_entry(self,
                            proxy_client: BaseProxyClient,
                            model_name: Optional[str] = None,
                            only_available: bool = False,
                            model_type: Union[str, ModelType] = None) -> RegisterDeployment:
        proxy_client_name = proxy_clients.get_proxy_cls_name(proxy_client)
        if only_available:
            available_models = [d.model_name for d in proxy_client.deployments]
            if len(available_models) == 0:
                raise KeyError('No models available!')
        else:
            available_models = None
        if available_models and model_name not in available_models:
            raise KeyError(f"Model '{model_name}' is not available!")

        if isinstance(model_type, str):
            model_type = ModelType[model_type.upper()]
            model_type = [model_type]
        elif isinstance(model_type, ModelType):
            pass
        elif model_type is None:
            model_type = [*ModelType]

        if not isinstance(model_type, Sequence):
            model_type = [model_type]
        for type_ in model_type:
            try:
                return self.models[proxy_client_name][type_][model_name]
            except KeyError:
                continue
        raise KeyError(f"Model '{model_name}' is not available!")

    def retrieve(self,
                 proxy_client: Optional[BaseProxyClient] = None,
                 args: List[str] = None,
                 kwargs: Dict[str, str] = None,
                 model_type: Union[str, ModelType] = None) -> RetrievalResult:
        """Retrieves a model deployment from the catalog.

        :param proxy_client: the proxy client to use for retrieving the model
        :type proxy_client: Optional[BaseProxyClient], optional
        :param args: the positional arguments for model identification, defaults to None
        :type args: List[str], optional
        :param kwargs: the keyword arguments for model identification, defaults to None
        :type kwargs: Dict[str, str], optional
        :param model_type: the type of the model to retrieve, defaults to None
        :type model_type: Union[str, ModelType], optional
        :return: The retrieval result containing the proxy client, deployment, and registry entry
        :rtype: RetrievalResult
        """
        proxy_client = proxy_client or get_proxy_client()
        model_name, model_identification_kwargs, kwargs = handle_model_args_kwargs(proxy_client=proxy_client,
                                                                                   args=args, kwargs=kwargs)
        registry_entry = self._get_registry_entry(
            proxy_client=proxy_client,
            model_name=model_name,
            model_type=model_type
        )
        f_select_deployment = registry_entry.f_select_deployment or default_f_select_deployment
        deployment = f_select_deployment(proxy_client, **model_identification_kwargs)
        return RetrievalResult(proxy_client=proxy_client, deployment=deployment, registry_entry=registry_entry)

    def all_llms(self, proxy_client: Optional[Union[str, BaseProxyClient]] = None) -> Dict[str, BaseLanguageModel]:
        """Retrieves all registered language models for the specified proxy client.

        :param proxy_client: the proxy client to retrieve models for, defaults to None
        :type proxy_client: Optional[Union[str, BaseProxyClient]], optional
        :raises TypeError: if the proxy client is invalid
        :return: A dictionary of model names and their corresponding language model instances
        :rtype: Dict[str, BaseLanguageModel]
        """
        if isinstance(proxy_client, str):
            proxy_client_name = proxy_client
        elif proxy_client is None:
            proxy_client_name = proxy_clients.get_proxy_cls_name(get_proxy_client())
        elif isinstance(proxy_client, BaseProxyClient):
            proxy_client_name = proxy_clients.get_proxy_cls_name(proxy_client)
        else:
            raise TypeError('Invalid proxy client')
        return {name: deplyoment.model for name, deplyoment in self.models[proxy_client_name][ModelType.LLM].items()}

    def all_embedding_models(self, proxy_client: Optional[Union[str, BaseProxyClient]] = None) -> Dict[str, Embeddings]:
        """Retrieves all registered embedding models for the specified proxy client.

        :param proxy_client: the proxy client to retrieve models for, defaults to None
        :type proxy_client: Optional[Union[str, BaseProxyClient]], optional
        :raises TypeError: if the proxy client is invalid
        :return: A dictionary of model names and their corresponding embedding model instances
        :rtype: Dict[str, Embeddings]
        """
        if isinstance(proxy_client, str):
            proxy_client_name = proxy_client
        elif proxy_client is None:
            proxy_client_name = proxy_clients.get_proxy_cls_name(get_proxy_client())
        elif isinstance(proxy_client, BaseProxyClient):
            proxy_client_name = proxy_clients.get_proxy_cls_name(proxy_client)
        else:
            raise TypeError('Invalid proxy client')
        return {
            name: deplyoment.model
            for name, deplyoment in self.models[proxy_client_name][ModelType.EMBEDDINGS].items()
        }


catalog = Catalog()


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


def _init_model(proxy_client: Optional[BaseProxyClient],
                model_type: ModelType,
                args: List[Any],
                kwargs: Dict[str, Any],
                init_func: Optional[Callable] = None,
                model_kwargs: Optional[Dict[str, Any]] = None):
    model_kwargs = model_kwargs or {}
    if init_func:
        return _init_custom_model(proxy_client=proxy_client, init_func=init_func, args=args, kwargs=kwargs,
                                  model_kwargs=model_kwargs)
    retrieval_result: RetrievalResult = catalog.retrieve(proxy_client=proxy_client,
                                                         args=args,
                                                         kwargs=kwargs,
                                                         model_type=model_type)
    return retrieval_result.registry_entry.init_func(proxy_client=retrieval_result.proxy_client,
                                                     deployment=retrieval_result.deployment,
                                                     **model_kwargs)


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


def get_model_class(*args,
                    model_type: Union[str, ModelType] = None,
                    proxy_client: Optional[BaseProxyClient] = None,
                    **kwargs) -> Union[BaseLanguageModel, Embeddings]:
    """
    Retrieves the model class for the specified model.

    :param model_type: The type of the model to retrieve (optional)
    :type model_type: Union[str, ModelType]
    :param proxy_client: The proxy client to use for the model (optional)
    :type proxy_client: BaseProxyClient
    :return: The model class
    :rtype: Union[BaseLanguageModel, Embeddings]
    """
    retrieval_result: RetrievalResult = catalog.retrieve(proxy_client=proxy_client,
                                                         args=args,
                                                         kwargs=kwargs,
                                                         model_type=model_type)
    return retrieval_result.registry_entry.model
