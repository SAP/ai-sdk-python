import unittest

from ai_api_client_sdk.helpers.llm_helper import (
    filter_foundation_models_by_capability,
    filter_foundation_models_non_deprecated,
    get_foundation_model_latest_versions,
)
from ai_api_client_sdk.models.model import Model
from ai_api_client_sdk.models.model_version import ModelVersion


def _make_version(name, is_latest=False, deprecated=False, capabilities=None):
    return ModelVersion(
        name=name,
        is_latest=is_latest,
        deprecated=deprecated,
        capabilities=capabilities,
    )


def _make_model(model_name, executable_id, versions):
    return Model(
        executable_id=executable_id,
        model=model_name,
        description=f"{model_name} description",
        versions=versions,
    )


class TestFilterFoundationModelsByCapability(unittest.TestCase):
    def setUp(self):
        self.models = [
            _make_model(
                "gpt-4o",
                "azure-openai",
                [
                    _make_version("2024-11-20", is_latest=True, capabilities=["vision", "tools"]),
                    _make_version("2024-05-13", deprecated=True, capabilities=["vision"]),
                ],
            ),
            _make_model(
                "text-embedding-3-large",
                "azure-openai",
                [
                    _make_version("1", is_latest=True, capabilities=["embedding"]),
                ],
            ),
        ]

    def test_returns_models_with_capability(self):
        result = filter_foundation_models_by_capability(self.models, "vision")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].model, "gpt-4o")

    def test_returns_empty_when_no_match(self):
        result = filter_foundation_models_by_capability(self.models, "nonexistent")
        self.assertEqual(len(result), 0)

    def test_ignores_deprecated_versions(self):
        # Only deprecated version has "vision" → should be excluded
        models = [
            _make_model(
                "old-model",
                "azure-openai",
                [_make_version("1.0", deprecated=True, capabilities=["vision"])],
            ),
        ]
        result = filter_foundation_models_by_capability(models, "vision")
        self.assertEqual(len(result), 0)


class TestFilterFoundationModelsNonDeprecated(unittest.TestCase):
    def setUp(self):
        self.models = [
            _make_model(
                "gpt-4o",
                "azure-openai",
                [
                    _make_version("2024-11-20", is_latest=True),
                    _make_version("2024-05-13", deprecated=True),
                ],
            ),
            _make_model(
                "text-embedding-3-large",
                "azure-openai",
                [_make_version("1", is_latest=True)],
            ),
        ]

    def test_removes_deprecated_versions(self):
        result = filter_foundation_models_non_deprecated(self.models)
        gpt4o = next(m for m in result if m.model == "gpt-4o")
        self.assertEqual(len(gpt4o.versions), 1)
        self.assertEqual(gpt4o.versions[0].name, "2024-11-20")

    def test_excludes_models_with_all_deprecated(self):
        models = [
            _make_model(
                "old-model",
                "azure-openai",
                [_make_version("1", deprecated=True)],
            ),
        ]
        result = filter_foundation_models_non_deprecated(models)
        self.assertEqual(len(result), 0)

    def test_keeps_models_with_active_versions(self):
        result = filter_foundation_models_non_deprecated(self.models)
        self.assertEqual(len(result), 2)

    def test_does_not_mutate_original(self):
        original_len = len(self.models[0].versions)
        filter_foundation_models_non_deprecated(self.models)
        self.assertEqual(len(self.models[0].versions), original_len)


class TestGetFoundationModelLatestVersions(unittest.TestCase):
    def test_returns_one_entry_per_model(self):
        models = [
            _make_model("a", "x", [_make_version("1", is_latest=True)]),
            _make_model("b", "y", [_make_version("1", is_latest=True)]),
        ]
        result = get_foundation_model_latest_versions(models)
        self.assertEqual(len(result), 2)

    def test_returns_marked_latest(self):
        models = [
            _make_model(
                "gpt-4o",
                "azure-openai",
                [
                    _make_version("2024-11-20", is_latest=True),
                    _make_version("2024-05-13"),
                ],
            ),
        ]
        result = get_foundation_model_latest_versions(models)
        self.assertEqual(len(result[0]["latest_versions"]), 1)
        self.assertEqual(result[0]["latest_versions"][0].name, "2024-11-20")

    def test_returns_all_when_none_marked_latest(self):
        models = [
            _make_model(
                "no-latest",
                "azure-openai",
                [
                    _make_version("1"),
                    _make_version("2"),
                ],
            ),
        ]
        result = get_foundation_model_latest_versions(models)
        self.assertEqual(len(result[0]["latest_versions"]), 2)

    def test_includes_model_and_executable_id(self):
        models = [
            _make_model("gpt-4o", "azure-openai", [_make_version("1", is_latest=True)]),
        ]
        result = get_foundation_model_latest_versions(models)
        self.assertEqual(result[0]["model"], "gpt-4o")
        self.assertEqual(result[0]["executable_id"], "azure-openai")
