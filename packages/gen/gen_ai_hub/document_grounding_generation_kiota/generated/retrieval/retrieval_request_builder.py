from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .data_repositories.data_repositories_request_builder import DataRepositoriesRequestBuilder
    from .search.search_request_builder import SearchRequestBuilder

class RetrievalRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /retrieval
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new RetrievalRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/retrieval", path_parameters)
    
    @property
    def data_repositories(self) -> DataRepositoriesRequestBuilder:
        """
        The dataRepositories property
        """
        from .data_repositories.data_repositories_request_builder import DataRepositoriesRequestBuilder

        return DataRepositoriesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def search(self) -> SearchRequestBuilder:
        """
        The search property
        """
        from .search.search_request_builder import SearchRequestBuilder

        return SearchRequestBuilder(self.request_adapter, self.path_parameters)
    

