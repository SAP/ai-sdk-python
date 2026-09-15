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
    from ...models.document_bulk_delete_request import DocumentBulkDeleteRequest
    from ...models.document_bulk_delete_response import DocumentBulkDeleteResponse
    from ...models.document_bulk_delete_response400_error import DocumentBulkDeleteResponse400Error
    from ...models.document_bulk_delete_response404_error import DocumentBulkDeleteResponse404Error
    from ...models.document_bulk_delete_response422_error import DocumentBulkDeleteResponse422Error
    from .metadata.metadata_request_builder import MetadataRequestBuilder

class DocumentsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /vector/documents
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new DocumentsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/vector/documents", path_parameters)
    
    async def delete(self,body: DocumentBulkDeleteRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[DocumentBulkDeleteResponse]:
        """
        Deletes list of documents across collections.
        param body: A request to delete documents by their IDs.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[DocumentBulkDeleteResponse]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_delete_request_information(
            body, request_configuration
        )
        from ...models.document_bulk_delete_response400_error import DocumentBulkDeleteResponse400Error
        from ...models.document_bulk_delete_response404_error import DocumentBulkDeleteResponse404Error
        from ...models.document_bulk_delete_response422_error import DocumentBulkDeleteResponse422Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": DocumentBulkDeleteResponse400Error,
            "404": DocumentBulkDeleteResponse404Error,
            "422": DocumentBulkDeleteResponse422Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.document_bulk_delete_response import DocumentBulkDeleteResponse

        return await self.request_adapter.send_async(request_info, DocumentBulkDeleteResponse, error_mapping)
    
    def to_delete_request_information(self,body: DocumentBulkDeleteRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Deletes list of documents across collections.
        param body: A request to delete documents by their IDs.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> DocumentsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: DocumentsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return DocumentsRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def metadata(self) -> MetadataRequestBuilder:
        """
        The metadata property
        """
        from .metadata.metadata_request_builder import MetadataRequestBuilder

        return MetadataRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class DocumentsRequestBuilderDeleteRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

