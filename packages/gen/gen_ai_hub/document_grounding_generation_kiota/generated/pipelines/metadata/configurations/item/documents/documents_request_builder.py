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
    from ......models.batch_update_documents_response400_error import BatchUpdateDocumentsResponse400Error
    from ......models.document_metadata_batch_request import DocumentMetadataBatchRequest
    from ......models.list_configuration_documents import ListConfigurationDocuments
    from .batch_update_documents_response import BatchUpdateDocumentsResponse
    from .item.with_document_item_request_builder import WithDocumentItemRequestBuilder

class DocumentsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /pipelines/metadata/configurations/{metadataConfigId}/documents
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new DocumentsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/pipelines/metadata/configurations/{metadataConfigId}/documents{?%24count*,%24skip*,%24top*,absolutePath*}", path_parameters)
    
    def by_document_id(self,document_id: str) -> WithDocumentItemRequestBuilder:
        """
        Gets an item from the gen_ai_hub.document_grounding_generation_kiota.generated.pipelines.metadata.configurations.item.documents.item collection
        param document_id: Document ID
        Returns: WithDocumentItemRequestBuilder
        """
        if document_id is None:
            raise TypeError("document_id cannot be null.")
        from .item.with_document_item_request_builder import WithDocumentItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["documentId"] = document_id
        return WithDocumentItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[DocumentsRequestBuilderGetQueryParameters]] = None) -> Optional[ListConfigurationDocuments]:
        """
        List the documents for a configuration
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[ListConfigurationDocuments]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ......models.list_configuration_documents import ListConfigurationDocuments

        return await self.request_adapter.send_async(request_info, ListConfigurationDocuments, None)
    
    async def patch(self,body: DocumentMetadataBatchRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[list[BatchUpdateDocumentsResponse]]:
        """
        Patch the documents of a configuration in batch
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[list[BatchUpdateDocumentsResponse]]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_patch_request_information(
            body, request_configuration
        )
        from ......models.batch_update_documents_response400_error import BatchUpdateDocumentsResponse400Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": BatchUpdateDocumentsResponse400Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .batch_update_documents_response import BatchUpdateDocumentsResponse

        return await self.request_adapter.send_collection_async(request_info, BatchUpdateDocumentsResponse, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[DocumentsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        List the documents for a configuration
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_patch_request_information(self,body: DocumentMetadataBatchRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Patch the documents of a configuration in batch
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.PATCH, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/merge-patch+json", body)
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
    
    @dataclass
    class DocumentsRequestBuilderGetQueryParameters():
        """
        List the documents for a configuration
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "absolute_path":
                return "absolutePath"
            if original_name == "count":
                return "%24count"
            if original_name == "skip":
                return "%24skip"
            if original_name == "top":
                return "%24top"
            return original_name
        
        # Absolute path of the resource. Supports wildcard values (e.g., `/folder/*`).
        absolute_path: Optional[str] = None

        # When the $count field is set to false, the response contains a count of the items present in the response. When the $count field is set to true, the response contains a count of all the items present on the server, and not just the ones in the response. When the $count field is not passed, it is false by default.
        count: Optional[bool] = None

        # Number of results to be skipped from the ordered list of results
        skip: Optional[int] = None

        # Number of results to display
        top: Optional[int] = None

    
    @dataclass
    class DocumentsRequestBuilderGetRequestConfiguration(RequestConfiguration[DocumentsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class DocumentsRequestBuilderPatchRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

