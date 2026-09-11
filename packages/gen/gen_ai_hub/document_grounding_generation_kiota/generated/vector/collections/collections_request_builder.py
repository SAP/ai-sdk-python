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
from uuid import UUID
from warnings import warn

if TYPE_CHECKING:
    from ...models.collections400_error import Collections400Error
    from ...models.collections422_error import Collections422Error
    from ...models.collections_list_response import CollectionsListResponse
    from ...models.collections_list_response400_error import CollectionsListResponse400Error
    from ...models.collection_request import CollectionRequest
    from .item.collection_item_request_builder import CollectionItemRequestBuilder
    from .metadata.metadata_request_builder import MetadataRequestBuilder

class CollectionsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /vector/collections
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new CollectionsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/vector/collections{?%24count*,%24skip*,%24top*}", path_parameters)
    
    def by_collection_id(self,collection_id: UUID) -> CollectionItemRequestBuilder:
        """
        Gets an item from the gen_ai_hub.document_grounding_generation_kiota.generated.vector.collections.item collection
        param collection_id: Collection ID
        Returns: CollectionItemRequestBuilder
        """
        if collection_id is None:
            raise TypeError("collection_id cannot be null.")
        from .item.collection_item_request_builder import CollectionItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["collection%2Did"] = collection_id
        return CollectionItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[CollectionsRequestBuilderGetQueryParameters]] = None) -> Optional[CollectionsListResponse]:
        """
        Gets a list of collections.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[CollectionsListResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ...models.collections400_error import Collections400Error
        from ...models.collections422_error import Collections422Error
        from ...models.collections_list_response400_error import CollectionsListResponse400Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": CollectionsListResponse400Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.collections_list_response import CollectionsListResponse

        return await self.request_adapter.send_async(request_info, CollectionsListResponse, error_mapping)
    
    async def post(self,body: CollectionRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> None:
        """
        Creates a collection. This operation is asynchronous. Poll the collection resource and check the status field to understand creation status.
        param body: A request for creating a new, single collection.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ...models.collections400_error import Collections400Error
        from ...models.collections422_error import Collections422Error
        from ...models.collections_list_response400_error import CollectionsListResponse400Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": Collections400Error,
            "422": Collections422Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[CollectionsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Gets a list of collections.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: CollectionRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Creates a collection. This operation is asynchronous. Poll the collection resource and check the status field to understand creation status.
        param body: A request for creating a new, single collection.
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
    
    def with_url(self,raw_url: str) -> CollectionsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: CollectionsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return CollectionsRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def metadata(self) -> MetadataRequestBuilder:
        """
        The metadata property
        """
        from .metadata.metadata_request_builder import MetadataRequestBuilder

        return MetadataRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class CollectionsRequestBuilderGetQueryParameters():
        """
        Gets a list of collections.
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
            if original_name == "skip":
                return "%24skip"
            if original_name == "top":
                return "%24top"
            return original_name
        
        # When the $count field is set to false, the response contains a count of the items present in the response. When the $count field is set to true, the response contains a count of all the items present on the server, and not just the ones in the response. When the $count field is not passed, it is false by default.
        count: Optional[bool] = None

        # Number of results to be skipped from the ordered list of results
        skip: Optional[int] = None

        # Number of results to display
        top: Optional[int] = None

    
    @dataclass
    class CollectionsRequestBuilderGetRequestConfiguration(RequestConfiguration[CollectionsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class CollectionsRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

