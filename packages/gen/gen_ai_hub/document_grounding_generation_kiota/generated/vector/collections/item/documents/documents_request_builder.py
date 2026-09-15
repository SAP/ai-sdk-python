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
    from .....models.documents import Documents
    from .....models.documents400_error import Documents400Error
    from .....models.documents404_error import Documents404Error
    from .....models.documents422_error import Documents422Error
    from .....models.documents_list_response import DocumentsListResponse
    from .....models.documents_list_response400_error import DocumentsListResponse400Error
    from .....models.documents_list_response404_error import DocumentsListResponse404Error
    from .....models.documents_list_response422_error import DocumentsListResponse422Error
    from .....models.document_create_request import DocumentCreateRequest
    from .....models.document_update_request import DocumentUpdateRequest
    from .item.with_document_item_request_builder import WithDocumentItemRequestBuilder

class DocumentsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /vector/collections/{collection-id}/documents
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new DocumentsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/vector/collections/{collection%2Did}/documents{?%24count*,%24skip*,%24top*}", path_parameters)
    
    def by_document_id(self,document_id: UUID) -> WithDocumentItemRequestBuilder:
        """
        Gets an item from the gen_ai_hub.document_grounding_generation_kiota.generated.vector.collections.item.documents.item collection
        param document_id: Document ID
        Returns: WithDocumentItemRequestBuilder
        """
        if document_id is None:
            raise TypeError("document_id cannot be null.")
        from .item.with_document_item_request_builder import WithDocumentItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["documentId"] = document_id
        return WithDocumentItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[DocumentsRequestBuilderGetQueryParameters]] = None) -> Optional[Documents]:
        """
        Gets a list of documents of a collection.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Documents]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from .....models.documents400_error import Documents400Error
        from .....models.documents404_error import Documents404Error
        from .....models.documents422_error import Documents422Error
        from .....models.documents_list_response400_error import DocumentsListResponse400Error
        from .....models.documents_list_response404_error import DocumentsListResponse404Error
        from .....models.documents_list_response422_error import DocumentsListResponse422Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": Documents400Error,
            "404": Documents404Error,
            "422": Documents422Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.documents import Documents

        return await self.request_adapter.send_async(request_info, Documents, error_mapping)
    
    async def patch(self,body: DocumentUpdateRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[DocumentsListResponse]:
        """
        Upserts the data of multiple documents into a collection.
        param body: An update request containing one or more documents to update existing documents in a collection by ID.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[DocumentsListResponse]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_patch_request_information(
            body, request_configuration
        )
        from .....models.documents400_error import Documents400Error
        from .....models.documents404_error import Documents404Error
        from .....models.documents422_error import Documents422Error
        from .....models.documents_list_response400_error import DocumentsListResponse400Error
        from .....models.documents_list_response404_error import DocumentsListResponse404Error
        from .....models.documents_list_response422_error import DocumentsListResponse422Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": DocumentsListResponse400Error,
            "404": DocumentsListResponse404Error,
            "422": DocumentsListResponse422Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.documents_list_response import DocumentsListResponse

        return await self.request_adapter.send_async(request_info, DocumentsListResponse, error_mapping)
    
    async def post(self,body: DocumentCreateRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[DocumentsListResponse]:
        """
        Create and stores one or multiple documents into a collection. If omitted, 'id' will be auto-generated.
        param body: A create request containing one or more new documents to create and store in a collection.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[DocumentsListResponse]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from .....models.documents400_error import Documents400Error
        from .....models.documents404_error import Documents404Error
        from .....models.documents422_error import Documents422Error
        from .....models.documents_list_response400_error import DocumentsListResponse400Error
        from .....models.documents_list_response404_error import DocumentsListResponse404Error
        from .....models.documents_list_response422_error import DocumentsListResponse422Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": DocumentsListResponse400Error,
            "404": DocumentsListResponse404Error,
            "422": DocumentsListResponse422Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.documents_list_response import DocumentsListResponse

        return await self.request_adapter.send_async(request_info, DocumentsListResponse, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[DocumentsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Gets a list of documents of a collection.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_patch_request_information(self,body: DocumentUpdateRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Upserts the data of multiple documents into a collection.
        param body: An update request containing one or more documents to update existing documents in a collection by ID.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.PATCH, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def to_post_request_information(self,body: DocumentCreateRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Create and stores one or multiple documents into a collection. If omitted, 'id' will be auto-generated.
        param body: A create request containing one or more new documents to create and store in a collection.
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
        Gets a list of documents of a collection.
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
    
    @dataclass
    class DocumentsRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

