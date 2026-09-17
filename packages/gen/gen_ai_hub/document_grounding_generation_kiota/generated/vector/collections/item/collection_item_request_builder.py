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
    from ....models.collection import Collection
    from ....models.collection400_error import Collection400Error
    from ....models.collection404_error import Collection404Error
    from ....models.collection422_error import Collection422Error
    from .creation_status.creation_status_request_builder import CreationStatusRequestBuilder
    from .deletion_status.deletion_status_request_builder import DeletionStatusRequestBuilder
    from .documents.documents_request_builder import DocumentsRequestBuilder

class CollectionItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /vector/collections/{collection-id}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new CollectionItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/vector/collections/{collection%2Did}", path_parameters)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> None:
        """
        Deletes a specific collection by ID. This operation is asynchronous. Poll the collection for a 404 status code.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from ....models.collection400_error import Collection400Error
        from ....models.collection404_error import Collection404Error
        from ....models.collection422_error import Collection422Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": Collection400Error,
            "404": Collection404Error,
            "422": Collection422Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[Collection]:
        """
        Gets a specific collection by ID.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Collection]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ....models.collection400_error import Collection400Error
        from ....models.collection404_error import Collection404Error
        from ....models.collection422_error import Collection422Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": Collection400Error,
            "404": Collection404Error,
            "422": Collection422Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.collection import Collection

        return await self.request_adapter.send_async(request_info, Collection, error_mapping)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Deletes a specific collection by ID. This operation is asynchronous. Poll the collection for a 404 status code.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Gets a specific collection by ID.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> CollectionItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: CollectionItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return CollectionItemRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def creation_status(self) -> CreationStatusRequestBuilder:
        """
        The creationStatus property
        """
        from .creation_status.creation_status_request_builder import CreationStatusRequestBuilder

        return CreationStatusRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def deletion_status(self) -> DeletionStatusRequestBuilder:
        """
        The deletionStatus property
        """
        from .deletion_status.deletion_status_request_builder import DeletionStatusRequestBuilder

        return DeletionStatusRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def documents(self) -> DocumentsRequestBuilder:
        """
        The documents property
        """
        from .documents.documents_request_builder import DocumentsRequestBuilder

        return DocumentsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class CollectionItemRequestBuilderDeleteRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class CollectionItemRequestBuilderGetRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

