import os

from gen_ai_hub.context_registry import (
    ContextRegistryApiClient,
    DataDestinationsApi,
    ScenarioConfigurationManagerApi,
    TabularArtifactsApi,
    AutoDefinition,
    CSNDefinition,
    CreateDataDestination,
    CreateScenarioConfiguration,
    CreateTARequest,
    CreateTARequestCsnMetadata,
    DefinitionType,
    HDLConnectionConfig,
    HDLDataDestinationCreateRequest,
    Label,
    LabelKeyValuePair,
    PatchDataDestination,
    PatchScenarioConfiguration,
    SearchDestinationsRequest,
    SearchScenarioConfiguration,
    TabularArtifactConfig,
)


# Data Destinations

def create_hdl_data_destination():
    client = ContextRegistryApiClient()
    api = DataDestinationsApi(client)

    return api.create_update_data_destination_sync(
        data_destination_name="my-hdl-dest",
        create_data_destination=CreateDataDestination(
        actual_instance=HDLDataDestinationCreateRequest(
            type="HDL",
            config=HDLConnectionConfig(
                host=os.environ["HDL_HOST"]
            ),
            description="My HDL destination",
            labels=[LabelKeyValuePair(key="ext.ai.sap.com/environment", value="prod")],
        )
    )
,
    )


def list_data_destinations():
    client = ContextRegistryApiClient()
    api = DataDestinationsApi(client)

    return api.get_all_data_destinations_sync()


def search_data_destinations():
    client = ContextRegistryApiClient()
    api = DataDestinationsApi(client)

    return api.search_destinations_sync(
        search_destinations_request=SearchDestinationsRequest(
            labels=[LabelKeyValuePair(key="ext.ai.sap.com/environment", value="staging")]
        ),
    )


def get_data_destination():
    client = ContextRegistryApiClient()
    api = DataDestinationsApi(client)

    return api.get_data_destination_by_name_sync(
        data_destination_name="test1",
    )


def patch_data_destination():
    client = ContextRegistryApiClient()
    api = DataDestinationsApi(client)

    api.patch_data_destination_by_name_sync(
        data_destination_name="test1",
        patch_data_destination=PatchDataDestination(
            description="Updated description",
            labels=[LabelKeyValuePair(key="ext.ai.sap.com/environment", value="staging")],
        ),
    )


def delete_data_destination():
    client = ContextRegistryApiClient()
    api = DataDestinationsApi(client)

    api.delete_data_destination_by_name_sync(
        data_destination_name="test2",
    )


# Tabular Artifacts

def create_tabular_artifact():
    client = ContextRegistryApiClient()
    api = TabularArtifactsApi(client)

    return api.create_tabular_artifact_sync(
        tabular_artifact_name="ta-test1",
        create_ta_request=CreateTARequest(
            data_destination_name="test1",
            type="CSV",
            path="/data/customers.csv",
            csn_metadata=CreateTARequestCsnMetadata(
                definition=CSNDefinition(
                    actual_instance=AutoDefinition(definition_type=DefinitionType("AUTO"))
                ),
            ),
        ),
    )


def list_tabular_artifacts():
    client = ContextRegistryApiClient()
    api = TabularArtifactsApi(client)

    return api.get_all_tabular_artifacts_sync()


def get_tabular_artifact():
    client = ContextRegistryApiClient()
    api = TabularArtifactsApi(client)

    return api.get_tabular_artifact_by_name_sync(
        tabular_artifact_name="ta-test1",
    )


def get_tabular_artifact_data_preview():
    client = ContextRegistryApiClient()
    api = TabularArtifactsApi(client)

    return api.get_tabular_artifact_data_sync(
        tabular_artifact_name="ta-test1",
    )


def delete_tabular_artifact():
    client = ContextRegistryApiClient()
    api = TabularArtifactsApi(client)

    api.delete_tabular_artifact_sync(
        tabular_artifact_name="hdl",
    )


# Scenario Configurations

def create_scenario_configuration():
    client = ContextRegistryApiClient()
    api = ScenarioConfigurationManagerApi(client)

    return api.create_scenario_configuration_sync(
        scenario_configuration_name="scenario-test1",
        create_scenario_configuration=CreateScenarioConfiguration(
            description="Production scenario for customer data",
            tabular_artifacts=[TabularArtifactConfig(name="ta-test1")],
            labels=[Label(key="ext.ai.sap.com/environment", value="prod")],
        ),
    )


def list_scenario_configurations():
    client = ContextRegistryApiClient()
    api = ScenarioConfigurationManagerApi(client)

    return api.get_all_scenario_configurations_sync()


def search_scenario_configurations():
    client = ContextRegistryApiClient()
    api = ScenarioConfigurationManagerApi(client)

    return api.search_scenario_configurations_by_label_sync(
        search_scenario_configuration=SearchScenarioConfiguration(
            labels=[Label(key="ext.ai.sap.com/environment", value="prod")]
        ),
    )


def get_scenario_configuration():
    client = ContextRegistryApiClient()
    api = ScenarioConfigurationManagerApi(client)

    return api.get_scenario_configuration_by_name_sync(
        scenario_configuration_name="scenario-test1",
    )


def patch_scenario_configuration():
    client = ContextRegistryApiClient()
    api = ScenarioConfigurationManagerApi(client)

    api.patch_scenario_configuration_by_name_sync(
        scenario_configuration_name="scenario-test1",
        patch_scenario_configuration=PatchScenarioConfiguration(
            description="Updated description",
            tabular_artifacts=[TabularArtifactConfig(name="ta-test1")],
        ),
    )


def delete_scenario_configuration():
    client = ContextRegistryApiClient()
    api = ScenarioConfigurationManagerApi(client)

    api.delete_scenario_configuration_by_name_sync(
        scenario_configuration_name="scenario-test1",
    )
