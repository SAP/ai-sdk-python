from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from kiota_abstractions.default_query_parameters import QueryParameters
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.serialization import Parsable, ParsableFactory
from typing import Any, Optional, TYPE_CHECKING, Union
from warnings import warn

if TYPE_CHECKING:
    from ..models.get_pipelines import GetPipelines
    from ..models.get_pipelines400_error import GetPipelines400Error
    from ..models.pipeline_id import PipelineId
    from ..models.pipeline_id400_error import PipelineId400Error
    from .create_pipeline import CreatePipeline
    from .item.with_pipeline_item_request_builder import WithPipelineItemRequestBuilder
    from .metadata.metadata_request_builder import MetadataRequestBuilder
    from .search.search_request_builder import SearchRequestBuilder
    from .trigger.trigger_request_builder import TriggerRequestBuilder

class PipelinesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /pipelines
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new PipelinesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/pipelines{?%24count*,%24skip*,%24top*,metadataConfigId*}", path_parameters)
    
    def by_pipeline_id(self,pipeline_id: str) -> WithPipelineItemRequestBuilder:
        """
        Gets an item from the gen_ai_hub.document_grounding_generation_kiota.generated.pipelines.item collection
        param pipeline_id: The ID of the pipeline to get.
        Returns: WithPipelineItemRequestBuilder
        """
        if pipeline_id is None:
            raise TypeError("pipeline_id cannot be null.")
        from .item.with_pipeline_item_request_builder import WithPipelineItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["pipelineId"] = pipeline_id
        return WithPipelineItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[PipelinesRequestBuilderGetQueryParameters]] = None) -> Optional[GetPipelines]:
        """
        Get all pipelines
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[GetPipelines]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ..models.get_pipelines400_error import GetPipelines400Error
        from ..models.pipeline_id400_error import PipelineId400Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": GetPipelines400Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ..models.get_pipelines import GetPipelines

        return await self.request_adapter.send_async(request_info, GetPipelines, error_mapping)
    
    async def post(self,body: CreatePipeline, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[PipelineId]:
        """
        Create a pipeline
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[PipelineId]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ..models.get_pipelines400_error import GetPipelines400Error
        from ..models.pipeline_id400_error import PipelineId400Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": PipelineId400Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ..models.pipeline_id import PipelineId

        return await self.request_adapter.send_async(request_info, PipelineId, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[PipelinesRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Get all pipelines
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: CreatePipeline, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Create a pipeline
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> PipelinesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: PipelinesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return PipelinesRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def metadata(self) -> MetadataRequestBuilder:
        """
        The metadata property
        """
        from .metadata.metadata_request_builder import MetadataRequestBuilder

        return MetadataRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def search(self) -> SearchRequestBuilder:
        """
        The search property
        """
        from .search.search_request_builder import SearchRequestBuilder

        return SearchRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def trigger(self) -> TriggerRequestBuilder:
        """
        The trigger property
        """
        from .trigger.trigger_request_builder import TriggerRequestBuilder

        return TriggerRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class PipelinesRequestBuilderGetQueryParameters():
        """
        Get all pipelines
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "count":
                return "%24count"
            if original_name == "metadata_config_id":
                return "metadataConfigId"
            if original_name == "skip":
                return "%24skip"
            if original_name == "top":
                return "%24top"
            return original_name
        
        # When the $count field is set to false, the response contains a count of the items present in the response. When the $count field is set to true, the response contains a count of all the items present on the server, and not just the ones in the response. When the $count field is not passed, it is false by default.
        count: Optional[bool] = None

        # Filter pipelines based on metadataConfigId
        metadata_config_id: Optional[str] = None

        # Number of results to be skipped from the ordered list of results
        skip: Optional[int] = None

        # Number of results to display
        top: Optional[int] = None

    
    @dataclass
    class PipelinesRequestBuilderGetRequestConfiguration(RequestConfiguration[PipelinesRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class PipelinesRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

