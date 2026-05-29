
class ModelBaseDataAllowedScenarios:
    """
    This class defines the allowed scenarios for the model base data.
    """

    def __init__(self, scenario_id: str, executable_id: str):
        """
        :param scenario_id: ID of the scenario
        :type scenario_id: str
        :param executable_id: ID of the executable
        :type executable_id: str
        """
        self._scenario_id: str = scenario_id
        self._executable_id: str = executable_id

    @staticmethod
    def from_dict(allowed_scenarios_dict: dict[str, any]):
        """
        Returns a :class:`ai_api_client_sdk.models.model_base_data_allowed_scenarios.ModelBaseDataAllowedScenarios`
        object, created from the values in the dict provided as parameter

        :param allowed_scenarios_dict: Dict which includes the necessary values to create the object
        :type allowed_scenarios_dict: Dict[str, Any]
        :return: An object, created from the values provided
        :rtype: class:`ai_api_client_sdk.models.model_base_data_allowed_scenarios.ModelBaseDataAllowedScenarios`
        """
        return ModelBaseDataAllowedScenarios(**allowed_scenarios_dict)
