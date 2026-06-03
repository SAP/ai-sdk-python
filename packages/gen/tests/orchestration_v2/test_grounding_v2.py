import unittest

from gen_ai_hub.orchestration_v2.models.document_grounding import (DocumentGroundingFilter, DocumentGroundingConfig,
                                                                   DataRepositoryType, DocumentGroundingPlaceholders,
                                                                   DocumentMetadataKeyValueListPairs, GroundingType,
                                                                   GroundingModuleConfig, GroundingSearchConfig)


class TestGrounding(unittest.TestCase):

    def test_document_metadata(self):
        metadata = DocumentMetadataKeyValueListPairs(key="key", value=["value"], select_mode=["ignoreIfKeyAbsent"])
        metadata_json = metadata.model_dump()
        self.assertEqual(metadata_json["key"], "key")
        self.assertEqual(metadata_json["value"], ["value"])
        self.assertEqual(metadata_json["select_mode"], ["ignoreIfKeyAbsent"])

    def test_grounding_filter_search_configuration(self):
        search_config = GroundingSearchConfig(max_chunk_count=10)
        search_config_json = search_config.model_dump()
        self.assertEqual(search_config_json["max_chunk_count"], 10)
        self.assertIsNone(search_config_json.get("max_document_count"))

    def test_grounding_filter(self):
        grounding_filter = DocumentGroundingFilter(id="id",
                                                   data_repository_type=DataRepositoryType.VECTOR,
                                                   data_repositories=["46b508c9-e490-4808-893b-b8e3361c4213"],
                                                   data_repository_metadata=[{
                                                       "key": "data_repository_key",
                                                       "value": ["data_repository_value"],
                                                   }],
                                                   search_config=GroundingSearchConfig(max_chunk_count=3),
                                                   document_metadata=[DocumentMetadataKeyValueListPairs(
                                                       key="keyTest",
                                                       value=["ValueTest1"],
                                                       select_mode=["ignoreIfKeyAbsent"]
                                                   )],
                                                   chunk_metadata=[{
                                                       "key": "chunk_metadata_key",
                                                       "value": ["chunk_metadata_value"],
                                                   }]
                                                   )
        filter_json = grounding_filter.model_dump()
        self.assertEqual(filter_json["id"], "id")
        self.assertEqual(filter_json["data_repository_type"], "vector")

    def test_grounding_configuration(self):
        filters = [DocumentGroundingFilter(id="id", data_repository_type=DataRepositoryType.VECTOR)]
        grounding_config = GroundingModuleConfig(
            type=GroundingType.DOCUMENT_GROUNDING_SERVICE,
            config=DocumentGroundingConfig(
                                     filters=filters, metadata_params=["metadata_param"],
                placeholders=DocumentGroundingPlaceholders(input=["user_query"], output="grounding_response"))
        )
        config_json = grounding_config.model_dump()
        self.assertEqual(config_json["type"], "document_grounding_service")
        self.assertEqual(config_json["config"]["placeholders"]["input"], ["user_query"])
        self.assertEqual(config_json["config"]["placeholders"]["output"], "grounding_response")
        self.assertEqual(config_json["config"]["filters"][0]["id"], "id")
        self.assertEqual(config_json["config"]["filters"][0]["data_repository_type"], "vector")
        self.assertEqual(config_json["config"]["metadata_params"], ["metadata_param"])
