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
    from ...models.data_repositories import DataRepositories
    from ...models.data_repositories400_error import DataRepositories400Error
    from .item.with_repository_item_request_builder import WithRepositoryItemRequestBuilder

class DataRepositoriesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /retrieval/dataRepositories
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new DataRepositoriesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/retrieval/dataRepositories{?%24count*,%24skip*,%24top*}", path_parameters)
    
    def by_repository_id(self,repository_id: UUID) -> WithRepositoryItemRequestBuilder:
        """
        Gets an item from the gen_ai_hub.document_grounding_generation_kiota.generated.retrieval.dataRepositories.item collection
        param repository_id: Repository ID
        Returns: WithRepositoryItemRequestBuilder
        """
        if repository_id is None:
            raise TypeError("repository_id cannot be null.")
        from .item.with_repository_item_request_builder import WithRepositoryItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["repositoryId"] = repository_id
        return WithRepositoryItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[DataRepositoriesRequestBuilderGetQueryParameters]] = None) -> Optional[DataRepositories]:
        """
        List all Data Repositories
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[DataRepositories]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ...models.data_repositories400_error import DataRepositories400Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": DataRepositories400Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.data_repositories import DataRepositories

        return await self.request_adapter.send_async(request_info, DataRepositories, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[DataRepositoriesRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        List all Data Repositories
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> DataRepositoriesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: DataRepositoriesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return DataRepositoriesRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class DataRepositoriesRequestBuilderGetQueryParameters():
        """
        List all Data Repositories
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
    class DataRepositoriesRequestBuilderGetRequestConfiguration(RequestConfiguration[DataRepositoriesRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

