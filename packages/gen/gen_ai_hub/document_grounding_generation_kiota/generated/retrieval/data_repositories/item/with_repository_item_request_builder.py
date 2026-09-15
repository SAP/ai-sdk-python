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
    from ....models.data_repository import DataRepository
    from ....models.data_repository400_error import DataRepository400Error
    from ....models.data_repository404_error import DataRepository404Error
    from ....models.data_repository422_error import DataRepository422Error

class WithRepositoryItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /retrieval/dataRepositories/{repositoryId}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithRepositoryItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/retrieval/dataRepositories/{repositoryId}{?remoteName*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[WithRepositoryItemRequestBuilderGetQueryParameters]] = None) -> Optional[DataRepository]:
        """
        List data repository by id
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[DataRepository]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ....models.data_repository400_error import DataRepository400Error
        from ....models.data_repository404_error import DataRepository404Error
        from ....models.data_repository422_error import DataRepository422Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": DataRepository400Error,
            "404": DataRepository404Error,
            "422": DataRepository422Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.data_repository import DataRepository

        return await self.request_adapter.send_async(request_info, DataRepository, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[WithRepositoryItemRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        List data repository by id
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> WithRepositoryItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithRepositoryItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithRepositoryItemRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class WithRepositoryItemRequestBuilderGetQueryParameters():
        """
        List data repository by id
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "remote_name":
                return "remoteName"
            return original_name
        
        # Remote name if DataRepository is from remote DG.
        remote_name: Optional[str] = None

    
    @dataclass
    class WithRepositoryItemRequestBuilderGetRequestConfiguration(RequestConfiguration[WithRepositoryItemRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

