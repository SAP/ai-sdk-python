from datetime import datetime
from typing import Any, Dict, Optional, List


class ModelVersion:
    """The ModelVersion object defines a version for a model
    :param name: Name of the model version
    :type name: str
    :param is_latest: True if model version is latest, otherwise false
    :type is_latest: bool
    :param deprecated: True if model version is deprecated, otherwise false
    :type deprecated: bool
    :param retirement_date: Retirement date of the model version, defaults to None
    :type retirement_date: datetime, optional
    :param context_length: Context length of the model version, defaults to None
    :type context_length: int, optional
    :param input_types: Input types supported by the model version, defaults to None
    :type input_types: List[str], optional
    :param capabilities: Capabilities of the model version, defaults to None
    :type capabilities: List[str], optional
    :param metadata: Metadata of the model version, defaults to None
    :type metadata: List[Dict[str, str]], optional
    :param cost: Cost of the model version, defaults to None
    :type cost: List[Dict[str, str]], optional
    :param suggested_replacements: Suggested replacements for the model version, defaults to None
    :type suggested_replacements: List[str], optional
    :param streaming_supported: True if streaming is supported, otherwise false
    :type streaming_supported: bool, optional
    :param orchestration_capabilities: Orchestration capabilities of the model version, defaults to None
    :type orchestration_capabilities: List[str], optional
    :param `**kwargs`: The keyword arguments are there in case there are additional attributes returned from server
    """

    def __init__(
        self,
        name: str,
        is_latest: bool,
        deprecated: bool,
        retirement_date: Optional[datetime] = None,
        context_length: Optional[int] = None,
        input_types: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
        cost: Optional[Dict[str, str]] = None,
        suggested_replacements: Optional[List[str]] = None,
        streaming_supported: Optional[bool] = None,
        orchestration_capabilities: Optional[List[str]] = None,
        **kwargs,
    ):
        self.name: str = name
        self.is_latest: bool = is_latest
        self.deprecated: bool = deprecated
        self.retirement_date: Optional[datetime] = retirement_date
        self.context_length: Optional[int] = context_length
        self.input_types: Optional[List[str]] = input_types
        self.capabilities: Optional[List[str]] = capabilities
        self.metadata: Optional[Dict[str, str]] = metadata
        self.cost: Optional[Dict[str, str]] = cost
        self.suggested_replacements: Optional[List[str]] = suggested_replacements
        self.streaming_supported: Optional[bool] = streaming_supported
        self.orchestration_capabilities: Optional[List[str]] = orchestration_capabilities

    def __eq__(self, other):
        if not isinstance(other, ModelVersion):
            return False
        for k in self.__dict__.keys():
            if getattr(self, k) != getattr(other, k):
                return False
        return True

    @staticmethod
    def from_dict(model_version_dict: Dict[str, Any]):
        """Returns a :class:`ai_api_client_sdk.models.model_version.ModelVersion` object, created from the values in the dict
        provided as parameter

        :param model_version_dict: Dict which includes the necessary values to create the object
        :type model_version_dict: Dict[str, Any]
        :return: An object, created from the values provided
        :rtype: class:`ai_api_client_sdk.models.model_version.ModelVersion`
        """
        return ModelVersion(**model_version_dict)
