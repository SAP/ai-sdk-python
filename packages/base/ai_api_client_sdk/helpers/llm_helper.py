import copy
from typing import Dict, List
from functools import partial

from ai_api_client_sdk.helpers.constants import SCENARIO_LABEL_NAME_PATTERN
from ai_api_client_sdk.models.model import Model


def get_attr(obj, attr):
    if isinstance(obj, dict):
        return obj.get(attr)
    else:
        return getattr(obj, attr, None)


class _NamedPartial(partial):
    def __repr__(self):
        return f"functools.partial(get_attr, attr={self.keywords['attr']!r})"


get_labels = _NamedPartial(get_attr, attr='labels')
get_key = _NamedPartial(get_attr, attr='key')
get_value = _NamedPartial(get_attr, attr='value')


def check_if_llm_scenario(scenario):
    labels = get_labels(scenario)
    if not labels:
        return False
    for label in labels:
        key = get_key(label)
        value = get_value(label)
        if SCENARIO_LABEL_NAME_PATTERN.match(key) and value:
            return True
    return False


def filter_for_llm_scenarios(response_dict):
    res_dict = {}
    filtered_scenarios = []
    for scenario in response_dict['resources']:
        if check_if_llm_scenario(scenario=scenario):
            filtered_scenarios.append(scenario)
    res_dict['count'] = len(filtered_scenarios)
    res_dict['resources'] = filtered_scenarios
    return res_dict


def filter_foundation_models_by_capability(models: List[Model], capability: str) -> List[Model]:
    """Filters models by a model capability (e.g. ``'vision'``).

    :param models: The list of models to filter
    :type models: List[class:`ai_api_client_sdk.models.model.Model`]
    :param capability: The capability to filter by
    :type capability: str
    :return: Models where at least one non-deprecated version declares the given capability
    :rtype: List[class:`ai_api_client_sdk.models.model.Model`]
    """
    return [
        m
        for m in models
        if any(
            not v.deprecated
            and v.capabilities
            and capability in v.capabilities
            for v in (m.versions or [])
        )
    ]


def filter_foundation_models_non_deprecated(models: List[Model]) -> List[Model]:
    """Removes deprecated versions from each model. Models with no remaining active versions are excluded.

    :param models: The list of models to filter
    :type models: List[class:`ai_api_client_sdk.models.model.Model`]
    :return: Models with deprecated versions removed
    :rtype: List[class:`ai_api_client_sdk.models.model.Model`]
    """
    result: List[Model] = []
    for m in models:
        active = [v for v in (m.versions or []) if not v.deprecated]
        if active:
            filtered = copy.copy(m)
            filtered.versions = active
            result.append(filtered)
    return result


def get_foundation_model_latest_versions(models: List[Model]) -> List[Dict]:
    """Gets the latest version(s) of each model. If a version is marked ``is_latest=True``, only that version is
    returned for the model. If no version is marked as latest, all versions are returned.

    :param models: The list of models
    :type models: List[class:`ai_api_client_sdk.models.model.Model`]
    :return: A list of dicts with keys ``model``, ``executable_id``, and ``latest_versions``
    :rtype: List[Dict]
    """
    result = []
    for m in models:
        versions = m.versions or []
        marked = [v for v in versions if v.is_latest]
        latest = marked if marked else versions
        result.append(
            {
                "model": m.model,
                "executable_id": m.executable_id,
                "latest_versions": latest,
            }
        )
    return result
