from typing import Any, Dict, List

from ai_api_client_sdk.models.model_version import ModelVersion
from ai_api_client_sdk.models.model_base_data_allowed_scenarios import ModelBaseDataAllowedScenarios


class Model:
    """The Model object defines a model
    :param executable_id: ID of the executable
    :type executable_id: str
    :param model: Unique name of the model
    :type model: str
    :param description: Description of the model, defaults to None
    :type description: str, optional
    :param versions: List of available model versions, defaults to None
    :type versions: List[class:`ai_api_client_sdk.models.model_version.ModelVersion`], optional
    :param display_name: Display name of the model, defaults to None
    :type display_name: str, optional
    :param access_type: Access type of the model, defaults to None
    :type access_type: str, optional
    :param provider: Provider of the model, defaults to None
    :type provider: str, optional
    :param allowed_scenarios: List of allowed scenarios for the model, defaults to None
    :type allowed_scenarios:
        List[ai_api_client_sdk.models.model_base_data_allowed_scenarios.ModelBaseDataAllowedScenarios], optional
    :param `**kwargs`: The keyword arguments are there in case there are additional attributes returned from server
    """

    def __init__(
        self,
        executable_id: str,
        model: str,
        description: str = None,
        versions: List[ModelVersion] = None,
        display_name: str = None,
        access_type: str = None,
        provider: str = None,
        allowed_scenarios: List[ModelBaseDataAllowedScenarios] = None,
        **kwargs,
    ):
        self.executable_id: str = executable_id
        self.model: str = model
        self.description: str = description
        self.versions: List[ModelVersion] = versions
        self.display_name: str = display_name
        self.access_type: str = access_type
        self.provider: str = provider
        self.allowed_scenarios: List[ModelBaseDataAllowedScenarios] = allowed_scenarios

    @staticmethod
    def from_dict(model_dict: Dict[str, Any]):
        """Returns a :class:`ai_api_client_sdk.models.model.Model` object, created from the values in the dict
        provided as parameter

        :param model_dict: Dict which includes the necessary values to create the object
        :type model_dict: Dict[str, Any]
        :return: An object, created from the values provided
        :rtype: class:`ai_api_client_sdk.models.model.Model`
        """
        if model_dict.get("versions"):
            model_dict["versions"] = [
                ModelVersion.from_dict(ia) for ia in model_dict["versions"]
            ]
        return Model(**model_dict)
