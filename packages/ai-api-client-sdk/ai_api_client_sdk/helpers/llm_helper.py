from functools import partial

from ai_api_client_sdk.helpers.constants import SCENARIO_LABEL_NAME_PATTERN


def get_attr(obj, attr):
    if isinstance(obj, dict):
        return obj.get(attr)
    else:
        return getattr(obj, attr, None)


get_labels = partial(get_attr, attr='labels')
get_key = partial(get_attr, attr='key')
get_value = partial(get_attr, attr='value')


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
