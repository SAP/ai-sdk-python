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
    from ......models.document_response import DocumentResponse
    from ......models.document_response400_error import DocumentResponse400Error
    from ......models.document_response404_error import DocumentResponse404Error
    from ......models.document_response422_error import DocumentResponse422Error
    from ......models.with_document400_error import WithDocument400Error
    from ......models.with_document404_error import WithDocument404Error
    from ......models.with_document422_error import WithDocument422Error

class WithDocumentItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /vector/collections/{collection-id}/documents/{documentId}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithDocumentItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/vector/collections/{collection%2Did}/documents/{documentId}", path_parameters)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> None:
        """
        Deletes a specific document of a collection.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from ......models.document_response400_error import DocumentResponse400Error
        from ......models.document_response404_error import DocumentResponse404Error
        from ......models.document_response422_error import DocumentResponse422Error
        from ......models.with_document400_error import WithDocument400Error
        from ......models.with_document404_error import WithDocument404Error
        from ......models.with_document422_error import WithDocument422Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": WithDocument400Error,
            "404": WithDocument404Error,
            "422": WithDocument422Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[DocumentResponse]:
        """
        Gets a specific document in a collection by ID.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[DocumentResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ......models.document_response400_error import DocumentResponse400Error
        from ......models.document_response404_error import DocumentResponse404Error
        from ......models.document_response422_error import DocumentResponse422Error
        from ......models.with_document400_error import WithDocument400Error
        from ......models.with_document404_error import WithDocument404Error
        from ......models.with_document422_error import WithDocument422Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": DocumentResponse400Error,
            "404": DocumentResponse404Error,
            "422": DocumentResponse422Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ......models.document_response import DocumentResponse

        return await self.request_adapter.send_async(request_info, DocumentResponse, error_mapping)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Deletes a specific document of a collection.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Gets a specific document in a collection by ID.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> WithDocumentItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithDocumentItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithDocumentItemRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class WithDocumentItemRequestBuilderDeleteRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithDocumentItemRequestBuilderGetRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

