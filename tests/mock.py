from __future__ import annotations

import asyncio
import json
import os
import pathlib
from contextlib import contextmanager, asynccontextmanager
from typing import Any, Dict, Final, List, Tuple, Type

import numpy as np
import requests_mock
import respx
from httpx import Response, AsyncByteStream

from gen_ai_hub.prompt_registry.models.prompt_template import (PromptTemplateSpec, PromptTemplateListResponse,
                                                               PromptTemplateGetResponse, PromptTemplatePostResponse,
                                                               PromptTemplateDeleteResponse, PromptTemplate,
                                                               PromptTemplateSubstitutionRequest,
                                                               PromptTemplateSubstitutionResponse)
from gen_ai_hub.proxy.core.base import BaseDeployment, BaseProxyClient
from gen_ai_hub.proxy.core.proxy_clients import proxy_clients

PREFIX: Final[str] = 'MOCK_LLM'
MOCK_LLM_DEFAULT_HOME: Final[str] = pathlib.Path('~/.mock_llm').expanduser().__str__()


class MockDeployment(BaseDeployment):
    url: str

    # abstractmethod implementations
    def additional_request_body_kwargs(self) -> Dict[str, Any]:
        return {}

    @staticmethod
    def get_model_identification_kwargs() -> Tuple[str]:
        return ('a', 'b', 'c')

    @property
    def prediction_url(self):
        return self.url + '/predict'


@proxy_clients.register('mock')
class MockProxyClient(BaseProxyClient):
    url: str = 'mock_url'
    token: str = 'mock_token'

    @property
    def request_header(self) -> Dict[str, Any]:
        return {'token': self.token}

    @property
    def deployments(self) -> List[MockDeployment]:
        return [MockDeployment(url=self.url)]

    @property
    def deployment_class(self) -> Type[MockDeployment]:
        return MockDeployment

    def select_deployment(self) -> MockDeployment:
        return self.deployments[0]

    @classmethod
    def get_home(cls):
        return pathlib.Path(os.environ.get(f'{PREFIX}_HOME', MOCK_LLM_DEFAULT_HOME)).expanduser()


# {{auth_url}}/oauth/token
GET_TOKEN_RESPONSE = {'access_token': 'xxx', 'token_type': 'bearer', 'expires_in': 43199, 'scope': '???'}

# {{apiurl}}/v2/lm/deployments
GET_DEPLOYMENTS_RESPONSE = {
    'count':
        7,
    'resources': [
        {
            'configurationId': 'ad4a2c61-875a-416a-96b6-24ed1347a164',
            'configurationName': 'gpt-4o-mini',
            'createdAt': '2023-11-17T13:13:29Z',
            'deploymentUrl':
                'https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/d768512472eae8f4',
            'details': {
                'resources': {
                    'backend_details': {
                        'model': {
                            'name': 'gpt-4o-mini',
                            'version': 'latest'
                        }
                    }
                },
                'scaling': {
                    'backend_details': {}
                }
            },
            'id': 'd768512472eae8f4',
            'lastOperation': 'CREATE',
            'latestRunningConfigurationId': 'ad4a2c61-875a-416a-96b6-24ed1347a164',
            'modifiedAt': '2023-12-29T21:16:45Z',
            'scenarioId': 'foundation-models',
            'startTime': '2023-11-17T13:17:03Z',
            'status': 'RUNNING',
            'submissionTime': '2023-11-17T13:15:19Z',
            'targetStatus': 'RUNNING'
        },
        {
            'configurationId': 'e09e58c3-15bf-42ad-8a5e-5b3273846dda',
            'configurationName': 'text-embedding-ada-002-latest',
            'createdAt': '2023-11-20T11:24:09Z',
            'deploymentUrl':
                'https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/dac9dca90be5213a',
            'details': {
                'resources': {
                    'backend_details': {
                        'model': {
                            'name': 'text-embedding-ada-002',
                            'version': 'latest'
                        }
                    }
                },
                'scaling': {
                    'backend_details': {}
                }
            },
            'id': 'dac9dca90be5213a',
            'lastOperation': 'CREATE',
            'latestRunningConfigurationId': 'e09e58c3-15bf-42ad-8a5e-5b3273846dda',
            'modifiedAt': '2023-12-29T22:19:02Z',
            'scenarioId': 'foundation-models',
            'startTime': '2023-11-20T11:28:32Z',
            'status': 'RUNNING',
            'submissionTime': '2023-11-20T11:26:26Z',
            'targetStatus': 'RUNNING'
        },
        {
            'configurationId': 'cc3a48e2-036b-411f-8dc9-18ee16944754',
            'configurationName': 'nvidia--llama-3.2-nv-embedqa-1b',
            'createdAt': '2025-12-22T15:44:35Z',
            'deploymentUrl':
                'https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/deebf33e5ec3450c',
            'details': {
                'resources': {
                    'backend_details': {
                        'model': {
                            'name': 'nvidia--llama-3.2-nv-embedqa-1b',
                            'version': 'latest'
                        }
                    }
                },
                'scaling': {
                    'backend_details': {}
                }
            },
            'id': 'deebf33e5ec3450c',
            'lastOperation': 'CREATE',
            'latestRunningConfigurationId': 'cc3a48e2-036b-411f-8dc9-18ee16944754',
            'modifiedAt': '2025-12-22T15:48:35Z',
            'scenarioId': 'foundation-models',
            'startTime': '2025-12-22T15:45:35Z',
            'status': 'RUNNING',
            'submissionTime': '2025-12-22T15:46:26Z',
            'targetStatus': 'RUNNING'
        },
        # Mock instruct
        {
            'configurationId': '31987320-54ab-4469-a165-78748fef22b0',
            'configurationName': 'gpt-4-instruct-latest',
            'createdAt': '2023-11-20T11:24:09Z',
            'deploymentUrl':
                'https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/dac9dca90be5213b',
            'details': {
                'resources': {
                    'backend_details': {
                        'model': {
                            'name': 'gpt-4-instruct',
                            'version': 'latest'
                        }
                    }
                },
                'scaling': {
                    'backend_details': {}
                }
            },
            'id': 'dac9dca90be5213b',
            'lastOperation': 'CREATE',
            'latestRunningConfigurationId': '31987320-54ab-4469-a165-78748fef22b0',
            'modifiedAt': '2023-12-29T22:19:02Z',
            'scenarioId': 'foundation-models',
            'startTime': '2023-11-20T11:28:32Z',
            'status': 'RUNNING',
            'submissionTime': '2023-11-20T11:26:26Z',
            'targetStatus': 'RUNNING'
        },
        {
            "configurationId": "7785d039-b3cf-4250-969b-b5ac74047abc",
            "configurationName": "gemini pro",
            "createdAt": "2024-04-18T14:09:58Z",
            "deploymentUrl": "https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/d000a84bce0a333d",
            "details": {
                "resources": {
                    "backend_details": {
                        "model": {
                            "name": "gemini-2.0-flash",
                            "version": "latest"
                        }
                    }
                },
                "scaling": {
                    "backend_details": {}
                }
            },
            "id": "d000a84bce0a333d",
            "lastOperation": "CREATE",
            "latestRunningConfigurationId": "7785d039-b3cf-4250-969b-b5ac74047abc",
            "modifiedAt": "2024-05-07T14:30:43Z",
            "scenarioId": "foundation-models",
            "startTime": "2024-04-18T14:15:21Z",
            "status": "RUNNING",
            "submissionTime": "2024-04-18T14:12:37Z",
            "targetStatus": "RUNNING"
        },
        # Mock amazon--bedrock
        {
            "configurationId": "2cfd83e3-e770-4469-b056-ecab0e0b4e10",
            "configurationName": "amazon--nova-premier",
            "createdAt": "2024-05-28T06:10:58Z",
            "deploymentUrl": "https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/db0c5cf8ae2e09c9",
            "details": {
                "resources": {
                    "backend_details": {
                        "model": {
                            "name": "amazon--nova-premier",
                            "version": "latest"
                        }
                    }
                },
                "scaling": {
                    "backend_details": {}
                }
            },
            "id": "db0c5cf8ae2e09c9",
            "lastOperation": "CREATE",
            "latestRunningConfigurationId": "2cfd83e3-e770-4469-b056-ecab0e0b4e10",
            "modifiedAt": "2024-06-03T08:08:34Z",
            "scenarioId": "foundation-models",
            "startTime": "2024-05-28T06:13:00Z",
            "status": "RUNNING",
            "submissionTime": "2024-05-28T06:11:26Z",
            "targetStatus": "RUNNING"
        },
        # Mock amazon--titan-embed-text
        {
            "configurationId": "f5d65f9e-fb55-400a-a1ea-501f32fd25db",
            "configurationName": "amazon--titan-embed-text",
            "createdAt": "2024-07-03T10:13:07Z",
            "deploymentUrl": "https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/de1b7f924d70a828",
            "details": {
                "resources": {
                    "backend_details": {
                        "model": {
                            "name": "amazon--titan-embed-text",
                            "version": "latest"
                        }
                    }
                },
                "scaling": {
                    "backend_details": {}
                }
            },
            "id": "de1b7f924d70a828",
            "lastOperation": "CREATE",
            "latestRunningConfigurationId": "f5d65f9e-fb55-400a-a1ea-501f32fd25db",
            "modifiedAt": "2024-07-05T06:49:32Z",
            "scenarioId": "foundation-models",
            "startTime": "2024-07-03T10:14:49Z",
            "status": "RUNNING",
            "submissionTime": "2024-07-03T10:13:37Z",
            "targetStatus": "RUNNING"
        },
        # Mock cohere--command-a-reasoning
        {
            "configurationId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "configurationName": "cohere--command-a-reasoning",
            "createdAt": "2024-08-15T09:30:00Z",
            "deploymentUrl": "https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/dc0a1b2c3d4e5f67",
            "details": {
                "resources": {
                    "backend_details": {
                        "model": {
                            "name": "cohere--command-a-reasoning",
                            "version": "latest"
                        }
                    }
                },
                "scaling": {
                    "backend_details": {}
                }
            },
            "id": "dc0a1b2c3d4e5f67",
            "lastOperation": "CREATE",
            "latestRunningConfigurationId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "modifiedAt": "2024-08-20T14:22:15Z",
            "scenarioId": "foundation-models",
            "startTime": "2024-08-15T09:35:42Z",
            "status": "RUNNING",
            "submissionTime": "2024-08-15T09:32:18Z",
            "targetStatus": "RUNNING"
        },
    ]
}

# {{apiurl}}/v2/lm/deployments
GET_DEPLOYMENTS_RESPONSE_ORCHESTRATION = {
    'count':
        2,
    'resources': [
        {
            "id": "d7f9c215310f5a11",
            "createdAt": "2024-11-05T07:52:21Z",
            "modifiedAt": "2025-01-14T15:51:06Z",
            "status": "RUNNING",
            "details": {
                "resources": {
                    "backendDetails": {},
                    "backend_details": {}
                },
                "scaling": {
                    "backendDetails": {},
                    "backend_details": {}
                }
            },
            "scenarioId": "orchestration",
            "configurationId": "c802af4b-64f7-4e8a-955b-3dd49bdd7abb",
            "latestRunningConfigurationId": "c802af4b-64f7-4e8a-955b-3dd49bdd7abb",
            "lastOperation": "CREATE",
            "targetStatus": "RUNNING",
            "submissionTime": "2024-11-05T07:52:58Z",
            "startTime": "2024-11-05T07:54:18Z",
            "configurationName": "orchestration-config-1",
            "deploymentUrl": "https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/d7f9c215310f5a11"
        },
        {
            "id": "dea20c27f7fe0eca",
            "createdAt": "2024-09-11T09:42:32Z",
            "modifiedAt": "2025-01-14T15:51:05Z",
            "status": "RUNNING",
            "details": {
                "resources": {
                    "backendDetails": {},
                    "backend_details": {}
                },
                "scaling": {
                    "backendDetails": {},
                    "backend_details": {}
                }
            },
            "scenarioId": "orchestration",
            "configurationId": "0152d9f0-694f-4bd2-a287-f7d270c9db60",
            "latestRunningConfigurationId": "0152d9f0-694f-4bd2-a287-f7d270c9db60",
            "lastOperation": "CREATE",
            "targetStatus": "RUNNING",
            "submissionTime": "2024-09-11T09:43:16Z",
            "startTime": "2024-09-11T09:45:12Z",
            "configurationName": "orchestration-config-2",
            "deploymentUrl": "https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/dea20c27f7fe0eca"
        }
    ]
}
# Mock custom scenario
GET_DEPLOYMENTS_RESPONSE_CUSTOM_SCENARIO = {
    'count':
        1,
    'resources': [
        {
            "configurationId": "cdcf4374-ba3e-4aa3-9f32-86b90ac57506",
            "configurationName": "dox-llm-cinderella-infer2.l-v0.2.7",
            "createdAt": "2023-12-01T14:53:33Z",
            "deploymentUrl": "https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/df0758c763b18d6e",
            "details": {
                "resources": {
                    "backend_details": {
                        "predictor": {
                            "resource_plan": "infer2.l"
                        }
                    }
                },
                "scaling": {
                    "backend_details": {
                        "predictor": {
                            "max_replicas": "1",
                            "min_replicas": "1",
                            "running_replicas": 1
                        }
                    }
                }
            },
            "id": "df0758c763b18d6e",
            "lastOperation": "CREATE",
            "latestRunningConfigurationId": "cdcf4374-ba3e-4aa3-9f32-86b90ac57506",
            "modifiedAt": "2024-01-19T13:46:46Z",
            "scenarioId": "dox-llm",
            "startTime": "2023-12-27T08:45:28Z",
            "status": "RUNNING",
            "submissionTime": "2023-12-01T14:55:55Z",
            "targetStatus": "RUNNING"
        }
    ]
}
# {{apiurl}}/v2/lm/configurations/.*
GET_CONFIGURATIONS_RESPONSE_GPT35 = {
    'createdAt': '2023-11-17T13:02:28Z',
    'executableId': 'azure-openai',
    'id': 'ad4a2c61-875a-416a-96b6-24ed1347a164',
    'inputArtifactBindings': [],
    'name': 'gpt-4o-mini',
    'parameterBindings': [{
        'key': 'modelName',
        'value': 'gpt-4o-mini'
    }, {
        'key': 'modelVersion',
        'value': 'latest'
    }],
    'scenarioId': 'foundation-models'
}

GET_CONFIGURATIONS_RESPONSE_EMB = {
    'createdAt': '2023-11-20T11:23:47Z',
    'executableId': 'azure-openai',
    'id': 'e09e58c3-15bf-42ad-8a5e-5b3273846dda',
    'inputArtifactBindings': [],
    'name': 'text-embedding-ada-002-latest',
    'parameterBindings': [{
        'key': 'modelName',
        'value': 'text-embedding-ada-002'
    }],
    'scenarioId': 'foundation-models'
}

GET_CONFIGURATIONS_RESPONSE_GPT35_INSTRUCT = {
    'createdAt': '2023-11-20T11:23:47Z',
    'executableId': 'azure-openai',
    'id': '31987320-54ab-4469-a165-78748fef22b0',
    'inputArtifactBindings': [],
    'name': 'gpt-4-instruct-latest',
    'parameterBindings': [{
        'key': 'modelName',
        'value': 'gpt-4-instruct'
    }],
    'scenarioId': 'foundation-models'
}

GET_CONFIGURATIONS_RESPONSE_GEMINI = {
    "createdAt": "2024-05-07T14:35:13Z",
    "executableId": "gcp-vertexai",
    "id": "7785d039-b3cf-4250-969b-b5ac74047abc",
    "inputArtifactBindings": [],
    "name": "gemini pro",
    "parameterBindings": [
        {
            "key": "modelName",
            "value": "gemini-2.0-flash"
        },
        {
            "key": "modelVersion",
            "value": "latest"
        }
    ],
    "scenarioId": "foundation-models"
}

GET_CONFIGURATIONS_RESPONSE_AMAZON_TITAN_EMBED_TEXT = {
    "createdAt": "2024-05-28T06:10:54Z",
    "executableId": "aws-bedrock",
    "id": "f5d65f9e-fb55-400a-a1ea-501f32fd25db",
    "inputArtifactBindings": [],
    "name": "amazon--titan-embed-text",
    "parameterBindings": [
        {"key": "modelVersion", "value": "latest"},
        {"key": "modelName", "value": "amazon--titan-embed-text"},
    ],
    "scenarioId": "foundation-models",
}

GET_CONFIGURATIONS_RESPONSE_AMAZON_BEDROCK_NOVA = {
    "createdAt": "2024-05-28T06:10:54Z",
    "executableId": "aws-bedrock",
    "id": "2cfd83e3-e770-4469-b056-ecab0e0b4e10",
    "inputArtifactBindings": [],
    "name": "amazon--nova-premier",
    "parameterBindings": [
        {"key": "modelVersion", "value": "latest"},
        {"key": "modelName", "value": "amazon--nova-premier"},
    ],
    "scenarioId": "foundation-models",
}

GET_CONFIGURATIONS_RESPONSE_COHERE_COMMAND_A_REASONING = {
    "createdAt": "2024-08-15T09:30:00Z",
    "executableId": "cohere",
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "inputArtifactBindings": [],
    "name": "cohere--command-a-reasoning",
    "parameterBindings": [
        {"key": "modelVersion", "value": "latest"},
        {"key": "modelName", "value": "cohere--command-a-reasoning"},
    ],
    "scenarioId": "foundation-models",
}

GET_CONFIGURATIONS_RESPONSE_ORCHESTRATION_CONFIG_1 = {
    "id": "c802af4b-64f7-4e8a-955b-3dd49bdd7abb",
    "createdAt": "2024-11-05T07:42:52Z",
    "name": "orchestration-config-1",
    "executableId": "orchestration",
    "scenarioId": "orchestration",
    "parameterBindings": [],
    "inputArtifactBindings": []
}

GET_CONFIGURATIONS_RESPONSE_ORCHESTRATION_CONFIG_2 = {
    "id": "0152d9f0-694f-4bd2-a287-f7d270c9db60",
    "createdAt": "2024-09-11T09:42:32Z",
    "name": "orchestration-config-2",
    "executableId": "orchestration",
    "scenarioId": "orchestration",
    "parameterBindings": [],
    "inputArtifactBindings": []
}

GET_CONFIGURATIONS_RESPONSE_CINDERELLA_INSTRUCT = {
    "createdAt": "2023-12-01T14:53:09Z",
    "executableId": "dox-vllm-serve",
    "id": "cdcf4374-ba3e-4aa3-9f32-86b90ac57506",
    "inputArtifactBindings": [
        {
            "artifactId": "33b8ab7f-3726-4a5c-8f32-2ff0cc744429",
            "key": "textmodel"
        }
    ],
    "name": "dox-llm-cinderella-infer2.l-v0.2.7",
    "parameterBindings": [
        {
            "key": "image",
            "value": "dl-coe.common.repositories.cloud.sap/dox-vllm:0.0.2"
        },
        {
            "key": "resourcePlan",
            "value": "infer2.l"
        },
        {
            "key": "minReplicas",
            "value": "1"
        },
        {
            "key": "maxReplicas",
            "value": "1"
        },
        {
            "key": "portNumber",
            "value": "9000"
        },
        {
            "key": "gpu",
            "value": "1"
        },
        {
            "key": "trustRemoteCode",
            "value": "true"
        },
        {
            "key": "disableKernel",
            "value": "False"
        },
        {
            "key": "huggingFaceOffline",
            "value": "0"
        },
        {
            "key": "disableTelemetry",
            "value": "1"
        },
        {
            "key": "revision",
            "value": "main"
        },
        {
            "key": "additionalArgument",
            "value": " "
        },
        {
            "key": "modelName",
            "value": "cinderella/v2"
        },
        {
            "key": "tokenizer",
            "value": "mistralai/Mistral-7B-v0.1"
        }
    ],
    "scenarioId": "dox-llm"
}

GET_CONFIGURATIONS_RESPONSE_NVIDIA_EMBED = {
    "createdAt": "2024-12-01T10:00:00Z",
    "executableId": "azure-openai",
    "id": "cc3a48e2-036b-411f-8dc9-18ee16944754",
    "inputArtifactBindings": [],
    "name": "nvidia--llama-3.2-nv-embedqa-1b",
    "parameterBindings": [
        {
            "key": "modelName",
            "value": "nvidia--llama-3.2-nv-embedqa-1b"
        },
        {
            "key": "modelVersion",
            "value": "latest"
        }
    ],
    "scenarioId": "foundation-models"
}


@contextmanager
def ai_core_ai_api_mocker(auth_url, base_url):
    with requests_mock.Mocker() as mocker:
        mocker.post(auth_url, json=GET_TOKEN_RESPONSE)

        def mock_get_deployments(request, context):
            if 'scenarioid=foundation-models' in request.query:
                return GET_DEPLOYMENTS_RESPONSE
            elif 'scenarioid=dox-llm' in request.query:
                return GET_DEPLOYMENTS_RESPONSE_CUSTOM_SCENARIO
            elif 'orchestration' in request.query:
                return GET_DEPLOYMENTS_RESPONSE_ORCHESTRATION
            else:
                raise ValueError('Unknown scenario')

        mocker.get(f'{base_url.rstrip("/")}/lm/deployments', json=mock_get_deployments)
        mocker.get(f'{base_url.rstrip("/")}/lm/configurations/ad4a2c61-875a-416a-96b6-24ed1347a164',
                   json=GET_CONFIGURATIONS_RESPONSE_GPT35)
        mocker.get(f'{base_url.rstrip("/")}/lm/configurations/e09e58c3-15bf-42ad-8a5e-5b3273846dda',
                   json=GET_CONFIGURATIONS_RESPONSE_EMB)
        mocker.get(f'{base_url.rstrip("/")}/lm/configurations/31987320-54ab-4469-a165-78748fef22b0',
                   json=GET_CONFIGURATIONS_RESPONSE_GPT35_INSTRUCT)
        mocker.get(f'{base_url.rstrip("/")}/lm/configurations/7785d039-b3cf-4250-969b-b5ac74047abc',
                   json=GET_CONFIGURATIONS_RESPONSE_GEMINI)
        mocker.get(f'{base_url.rstrip("/")}/lm/configurations/2cfd83e3-e770-4469-b056-ecab0e0b4e10',
                   json=GET_CONFIGURATIONS_RESPONSE_AMAZON_BEDROCK_NOVA)
        mocker.get(f'{base_url.rstrip("/")}/lm/configurations/f5d65f9e-fb55-400a-a1ea-501f32fd25db',
                   json=GET_CONFIGURATIONS_RESPONSE_AMAZON_TITAN_EMBED_TEXT)
        mocker.get(f'{base_url.rstrip("/")}/lm/configurations/cdcf4374-ba3e-4aa3-9f32-86b90ac57506',
                   json=GET_CONFIGURATIONS_RESPONSE_CINDERELLA_INSTRUCT)
        mocker.get(f'{base_url.rstrip("/")}/lm/configurations/c802af4b-64f7-4e8a-955b-3dd49bdd7abb',
                   json=GET_CONFIGURATIONS_RESPONSE_ORCHESTRATION_CONFIG_1)
        mocker.get(f'{base_url.rstrip("/")}/lm/configurations/0152d9f0-694f-4bd2-a287-f7d270c9db60',
                   json=GET_CONFIGURATIONS_RESPONSE_ORCHESTRATION_CONFIG_2)
        mocker.get(f'{base_url.rstrip("/")}/lm/configurations/cc3a48e2-036b-411f-8dc9-18ee16944754',
                   json=GET_CONFIGURATIONS_RESPONSE_NVIDIA_EMBED)
        mocker.get(f'{base_url.rstrip("/")}/lm/configurations/a1b2c3d4-e5f6-7890-abcd-ef1234567890',
                   json=GET_CONFIGURATIONS_RESPONSE_COHERE_COMMAND_A_REASONING)
        mocker.get(f'{base_url.rstrip("/")}/inference/deployments/d7f9c215310f5a11/completion',
                   json=GET_ORCHESTRATION_COMPLETION_RESPONSE)
        mocker.get(f'{base_url.rstrip("/")}/inference/deployments/d7f9c215310f5a11/v2/completion',
                   json=GET_ORCHESTRATION_V2_COMPLETION_RESPONSE)
        yield


def get_mocked_ai_core_client(client_id='XXX'):
    from gen_ai_hub.proxy.gen_ai_hub_proxy.client import GenAIHubProxyClient
    from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client, proxy_version_context

    with proxy_version_context('gen-ai-hub'):
        kwargs = dict(
            client_id=client_id,
            client_secret='YYY',
            auth_url='https://auth_url/oauth/token',
            base_url='https://base_url/v2',
        )
        proxy_client: GenAIHubProxyClient = get_proxy_client(**kwargs)
        with ai_core_ai_api_mocker(auth_url=kwargs['auth_url'], base_url=kwargs['base_url']):
            proxy_client.get_request_header()
            proxy_client.get_deployments()
    return proxy_client


GET_ORCHESTRATION_COMPLETION_RESPONSE = {
    "request_id": "bf846179-66ef-4af5-8263-fee5028e69b2",
    "module_results": {
        "templating": [
            {
                "role": "system",
                "content": "This is a system message."
            },
            {
                "role": "user",
                "content": "Hello, World!"
            }
        ],
        "llm": {
            "id": "",
            "object": "chat.completion",
            "created": 1738572663,
            "model": "gemini-2.0-flash",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This confirms receipt of the message: \"Hello, World!\"\n"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "completion_tokens": 13,
                "prompt_tokens": 10,
                "total_tokens": 23
            }
        }
    },
    "orchestration_result": {
        "id": "",
        "object": "chat.completion",
        "created": 1738572663,
        "model": "gemini-2.0-flash",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This confirms receipt of the message: \"Hello, World!\"\n"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "completion_tokens": 13,
            "prompt_tokens": 10,
            "total_tokens": 23
        }
    }
}


GET_ORCHESTRATION_V2_COMPLETION_RESPONSE = {
    "request_id": "bf846179-66ef-4af5-8263-fee5028e69b2",
    "intermediate_results": {
        "templating": [
            {
                "role": "system",
                "content": "This is a system message."
            },
            {
                "role": "user",
                "content": "Hello, World!"
            }
        ],
        "llm": {
            "id": "",
            "object": "chat.completion",
            "created": 1738572663,
            "model": "gemini-2.0-flash",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This confirms receipt of the message: \"Hello, World!\"\n"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "completion_tokens": 13,
                "prompt_tokens": 10,
                "total_tokens": 23,
            "prompt_tokens_details": {
                    "audio_tokens": 0,
                    "cached_tokens": 3
            },
            "completion_tokens_details": {
                    "accepted_prediction_tokens": 3,
                    "audio_tokens": 0,
                    "reasoning_tokens": 0,
                    "rejected_prediction_tokens": 0
            }
            }
        }
    },
    "final_result": {
        "id": "",
        "object": "chat.completion",
        "created": 1738572663,
        "model": "gemini-2.0-flash",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This confirms receipt of the message: \"Hello, World!\"\n"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "completion_tokens": 13,
            "prompt_tokens": 10,
            "total_tokens": 23,
            "prompt_tokens_details": {
                    "audio_tokens": 0,
                    "cached_tokens": 3
            },
            "completion_tokens_details": {
                    "accepted_prediction_tokens": 3,
                    "audio_tokens": 0,
                    "reasoning_tokens": 0,
                    "rejected_prediction_tokens": 0
            }
        }
    }
}

@contextmanager
def orchestration_completion_mocker(deployment_url):
    with respx.mock:
        respx.post(deployment_url).mock(return_value=Response(200, json=GET_ORCHESTRATION_COMPLETION_RESPONSE))
        yield

@contextmanager
def orchestration_completion_v2_mocker(deployment_url):
    with respx.mock:
        respx.post(deployment_url).mock(return_value=Response(200, json=GET_ORCHESTRATION_V2_COMPLETION_RESPONSE))
        yield

GET_ORCHESTRATION_V2_EMBEDDINGS_RESPONSE = {
    "request_id": "emb-test-123",
    "intermediate_results": None,
    "final_result": {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "embedding": [0.005, -0.016, -0.016, 0.034, 0.010] + [0.0] * 3067,  # 3072 dimensions
                "index": 0
            }
        ],
        "model": "text-embedding-3-large",
        "usage": {
            "prompt_tokens": 2,
            "total_tokens": 2
        }
    }
}

GET_ORCHESTRATION_V2_EMBEDDINGS_BATCH_RESPONSE = {
    "request_id": "emb-batch-test-456",
    "intermediate_results": None,
    "final_result": {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "embedding": [0.1, 0.2, 0.3] + [0.0] * 253,  # 256 dimensions
                "index": 0
            },
            {
                "object": "embedding",
                "embedding": [0.4, 0.5, 0.6] + [0.0] * 253,
                "index": 1
            },
            {
                "object": "embedding",
                "embedding": [0.7, 0.8, 0.9] + [0.0] * 253,
                "index": 2
            }
        ],
        "model": "text-embedding-3-large",
        "usage": {
            "prompt_tokens": 10,
            "total_tokens": 10
        }
    }
}

GET_ORCHESTRATION_V2_EMBEDDINGS_WITH_MASKING_RESPONSE = {
    "request_id": "emb-masked-789",
    "intermediate_results": {
        "input_masking": {
            "message": "Embedding input is masked successfully.",
            "data": {
                "masked_input": "Contact MASKED_PERSON at MASKED_EMAIL or call 555-123-4567."
            }
        }
    },
    "final_result": {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "embedding": [0.01, 0.02, 0.03] + [0.0] * 3069,
                "index": 0
            }
        ],
        "model": "text-embedding-3-large",
        "usage": {
            "prompt_tokens": 8,
            "total_tokens": 8
        }
    }
}


@contextmanager
def orchestration_embeddings_v2_mocker(deployment_url):
    with respx.mock:
        respx.post(deployment_url).mock(return_value=Response(200, json=GET_ORCHESTRATION_V2_EMBEDDINGS_RESPONSE))
        yield


@contextmanager
def orchestration_embeddings_v2_batch_mocker(deployment_url):
    with respx.mock:
        respx.post(deployment_url).mock(return_value=Response(200, json=GET_ORCHESTRATION_V2_EMBEDDINGS_BATCH_RESPONSE))
        yield


@contextmanager
def orchestration_embeddings_v2_with_masking_mocker(deployment_url):
    with respx.mock:
        respx.post(deployment_url).mock(return_value=Response(200, json=GET_ORCHESTRATION_V2_EMBEDDINGS_WITH_MASKING_RESPONSE))
        yield


@contextmanager
def orchestration_deployment_not_found_mocker(deployment_url):
    with respx.mock:
        respx.post(deployment_url).mock(return_value=Response(404, content=b'deployment not found'))
        yield

@contextmanager
def orchestration_too_many_requests_mocker(deployment_url):
    with respx.mock:
        respx.post(deployment_url).mock(return_value=Response(429, headers={"X-Custom-Header": "value"},
                                                              json={"error": {"message": "too many requests"}}))
        yield


def generate_events():
    # First event: templating event with system and user messages.
    first_event = {
        "request_id": "d1d50b3f-90f9-495c-b5ef-4bfeb175de02",
        "module_results": {
            "input_filtering": None,
            "output_filtering": None,
            "input_masking": None,
            "llm": None,
            "templating": [
                {"content": "This is a system message.", "role": "system"},
                {"content": "Hello, World!", "role": "user"}
            ],
            "output_unmasking": None
        },
        "orchestration_result": {
            "id": "",
            "object": "",
            "created": 0,
            "model": "",
            "choices": [
                {"index": 0, "delta": {"content": "", "role": ""}, "finish_reason": "", "logprobs": None}
            ],
            "system_fingerprint": ""
        }
    }
    # Yield the first event as a server-sent event (SSE) formatted string.
    yield ("data: {}\n\n".format(json.dumps(first_event))).encode("utf-8")

    # List of tokens that will be returned one-by-one.
    tokens = [
        "This", " con", "firm", "s re", "ceip", "t of", " the",
        " sys", "tem ", "mess", "age:", ' "He', "llo,", " Wor",
        "ld!", "\n"
    ]
    for token in tokens:
        event = {
            "request_id": "d1d50b3f-90f9-495c-b5ef-4bfeb175de02",
            "module_results": {
                "input_filtering": None,
                "output_filtering": None,
                "input_masking": None,
                "llm": {
                    "id": "",
                    "object": "chat.completion.chunk",
                    "created": 1738573708,
                    "model": "gemini-2.0-flash",
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"content": token, "role": "assistant"},
                            "finish_reason": "stop",
                            "logprobs": None
                        }
                    ],
                    "system_fingerprint": None
                },
                "templating": None,
                "output_unmasking": None
            },
            "orchestration_result": {
                "id": "",
                "object": "chat.completion.chunk",
                "created": 1738573708,
                "model": "gemini-2.0-flash",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": token, "role": "assistant"},
                        "finish_reason": "stop",
                        "logprobs": None
                    }
                ],
                "system_fingerprint": None
            }
        }
        yield ("data: {}\n\n".format(json.dumps(event))).encode("utf-8")

def generate_v2_events():
    # First event: templating event with system and user messages.
    first_event = {
        "request_id": "d1d50b3f-90f9-495c-b5ef-4bfeb175de02",
        "intermediate_results": {
            "input_filtering": None,
            "output_filtering": None,
            "input_masking": None,
            "llm": None,
            "templating": [
                {"content": "This is a system message.", "role": "system"},
                {"content": "Hello, World!", "role": "user"}
            ],
            "output_unmasking": None
        },
        "final_result": {
            "id": "",
            "object": "",
            "created": 0,
            "model": "",
            "choices": [
                {"index": 0, "delta": {"content": "", "role": ""}, "finish_reason": "", "logprobs": None}
            ],
            "system_fingerprint": ""
        }
    }
    # Yield the first event as a server-sent event (SSE) formatted string.
    yield ("data: {}\n\n".format(json.dumps(first_event))).encode("utf-8")

    # List of tokens that will be returned one-by-one.
    tokens = [
        "This", " con", "firm", "s re", "ceip", "t of", " the",
        " sys", "tem ", "mess", "age:", ' "He', "llo,", " Wor",
        "ld!", "\n"
    ]
    for token in tokens:
        event = {
            "request_id": "d1d50b3f-90f9-495c-b5ef-4bfeb175de02",
            "intermediate_results": {
                "input_filtering": None,
                "output_filtering": None,
                "input_masking": None,
                "llm": {
                    "id": "",
                    "object": "chat.completion.chunk",
                    "created": 1738573708,
                    "model": "gemini-2.0-flash",
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"content": token, "role": "assistant"},
                            "finish_reason": "stop",
                            "logprobs": None
                        }
                    ],
                    "system_fingerprint": None
                },
                "templating": None,
                "output_unmasking": None
            },
            "final_result": {
                "id": "",
                "object": "chat.completion.chunk",
                "created": 1738573708,
                "model": "gemini-2.0-flash",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": token, "role": "assistant"},
                        "finish_reason": "stop",
                        "logprobs": None
                    }
                ],
                "system_fingerprint": None
            }
        }
        yield ("data: {}\n\n".format(json.dumps(event))).encode("utf-8")

@contextmanager
def orchestration_stream_completion_mocker(deployment_url):
    with respx.mock:
        respx.post(deployment_url).mock(
            return_value=Response(200, stream=generate_events())
        )
        yield

@contextmanager
def orchestration_stream_v2_completion_mocker(deployment_url):
    with respx.mock:
        respx.post(deployment_url).mock(
            return_value=Response(200, stream=generate_v2_events())
        )
        yield

# Wrap the synchronous generator in an async generator.
async def async_generate_events():
    for event in generate_events():
        yield event
        await asyncio.sleep(0)  # yield control to the event loop

# Wrap the synchronous generator in an async generator.
async def async_generate_v2_events():
    for event in generate_v2_events():
        yield event
        await asyncio.sleep(0)  # yield control to the event loop

# A simple AsyncByteStream implementation that wraps an async iterator.
class AsyncIteratorStream(AsyncByteStream):
    def __init__(self, aiter):
        self.aiter = aiter

    async def __aiter__(self):
        async for chunk in self.aiter:
            yield chunk


@asynccontextmanager
async def orchestration_stream_completion_mocker_async(deployment_url):
    with respx.mock:
        respx.post(deployment_url).mock(
            return_value=Response(200, stream=AsyncIteratorStream(async_generate_events()))
        )
        yield

@asynccontextmanager
async def orchestration_v2_stream_completion_mocker_async(deployment_url):
    with respx.mock:
        respx.post(deployment_url).mock(
            return_value=Response(200, stream=AsyncIteratorStream(async_generate_v2_events()))
        )
        yield

OPENAI_CHAT_COMPLETION_RESPONSE = {
    'choices': [{
        'finish_reason': 'stop',
        'index': 0,
        'message': {
            'content': 'Hello! How can I assist you today?',
            'role': 'assistant'
        }
    }],
    'created':
        1703886830,
    'id':
        'chatcmpl-8bF5a0q8oyDRXcVZucIBrV25AXT7H',
    'model':
        'gpt-4o-mini',
    'object':
        'chat.completion',
    'usage': {
        'completion_tokens': 9,
        'prompt_tokens': 19,
        'total_tokens': 28
    }
}

# Cohere chat completion response with choices=None and data in model_extra
COHERE_CHAT_COMPLETION_RESPONSE = {
    'id': 'cohere-chat-completion-id',
    'object': 'chat.completion',
    'created': 1703886830,
    'model': 'cohere--command-a-reasoning',
    'choices': None,
    'finish_reason': 'COMPLETE',
    'message': {
        'content': [
            {
                'text': 'Hello! How can I assist you today?',
                'type': 'text'
            }
        ],
        'role': 'assistant'
    }
}


@contextmanager
def openai_chat_completion_mocker(deployment_url):
    with respx.mock:
        respx.post(deployment_url).mock(return_value=Response(200, json=OPENAI_CHAT_COMPLETION_RESPONSE))
        yield


@contextmanager
def cohere_chat_completion_mocker(deployment_url):
    with respx.mock:
        respx.post(deployment_url).mock(return_value=Response(200, json=COHERE_CHAT_COMPLETION_RESPONSE))
        yield


john_doe = {"first_name": "John", "last_name": "Doe"}
OPENAI_STRUCTRED_OUTPUTS_RESPONSE = {
    'id': 'chatcmpl-C3kCRY6rwFZPhwYe9dCyFayJyxxlz',
    'choices': [{
        'finish_reason': 'stop',
        'index': 0,
        'message': {
            'content': json.dumps(john_doe),
        },
    }],
    'refusal': None,
    'role': 'human',
    'parsed': {'first_name': 'John', 'last_name': 'Doe'},
    'created': 1755008611,
    'model': 'gpt-4o-mini',
    'object': 'chat.completion',
    'system_fingerprint': 'fp_efad92c60b'
}


@contextmanager
def openai_structured_outputs_mocker(deployment_url):
    with respx.mock:
        respx.post(deployment_url).mock(return_value=Response(200, json=OPENAI_STRUCTRED_OUTPUTS_RESPONSE))
        yield


random_floats = np.random.RandomState(1337).randn(1536)
normalized_floats = random_floats / np.sum(random_floats)

OPENAI_EMBEDDINGS_RESPONSE = {
    'data': [{
        'embedding': [*normalized_floats],
        'index': 0,
        'object': 'embedding'
    }],
    'model': 'ada',
    'object': 'list',
    'usage': {
        'prompt_tokens': 5,
        'total_tokens': 5
    }
}


@contextmanager
def openai_embeddings_mocker(deployment_url):
    with respx.mock:
        respx.post(deployment_url).mock(return_value=Response(200, json=OPENAI_EMBEDDINGS_RESPONSE))
        yield


OPENAI_GPT35_INSTRUCT_RESPONSE = {
    'choices': [{
        'finish_reason':
            'length',
        'index':
            0,
        'logprobs':
            None,
        'text':
            "\n\nSAP's primary business is enterprise software and services, including customer relationship management, supply chain management"
    }],
    'created':
        1703951313,
    'id':
        'cmpl-8bVrdCCCWPxyCzZUbrCZ4utqTDi8A',
    'model':
        'gpt-4-instruct',
    'object':
        'text_completion',
    'usage': {
        'completion_tokens': 20,
        'prompt_tokens': 7,
        'total_tokens': 27
    }
}


@contextmanager
def openai_completion_mocker(deployment_url):
    with respx.mock:
        respx.post(deployment_url).mock(return_value=Response(200, json=OPENAI_GPT35_INSTRUCT_RESPONSE))
        yield

RPT_RESPONSE_CODE_0 = {
    "id": "c334f854-0d70-4c79-bd73-9ac581fd8cda",
    "status": {
        "code": 0,
        "message": "ok"
    },
    "predictions": [
        {
            "COSTCENTER": [
                {
                    "prediction": "Office Furniture",
                    "confidence": 0.96
                }
            ],
            "ID": "35"
        }
    ],
    "metadata": {
        "num_columns": 5,
        "num_rows": 2,
        "num_predictions": 1,
        "num_query_rows": 1
    }
}

@contextmanager
def sap_rpt_moke_response_code_0(url: str):
    with respx.mock:
        respx.post(f"{url}/predict").mock(return_value=Response(200, json=RPT_RESPONSE_CODE_0))
        yield

RPT_RESPONSE_CODE_2 = {
    "status": {
        "code": 2,
        "message": "Invalid input"
    },
    "detail": [
        {
            "loc": [
                "prediction_config",
                "target_columns",
                0,
                "prediction_placeholder"
            ],
            "msg": "Field required",
            "type": "missing"
        }
    ]
}

@contextmanager
def sap_rpt_moke_response_code_2(url: str):
    with respx.mock:
        respx.post(f"{url}/predict").mock(return_value=Response(422, json=RPT_RESPONSE_CODE_2))
        yield

@contextmanager
def openai_stream_completion_mocker(deployment_url):
    def stream_events(*args):
        for delta, finish_reason in (
                ({"role": "assistant", "content": ""}, None),
                ({"content": "Hi"}, None),
                ({"content": "!"}, None),
                ({}, "stop"),
        ):
            yield "data: {}\n\n".format(
                json.dumps(
                    {
                        "id": "chat-1",
                        "object": "chat.completion.chunk",
                        "created": 1695096940,
                        "model": "gpt-4o-mini",
                        "choices": [
                            {"index": 0, "delta": delta, "finish_reason": finish_reason}
                        ],
                    }
                )
            )

    with respx.mock:
        respx.post(deployment_url).mock(return_value=Response(200, json=list(stream_events())))
        yield


AMAZON_TITAN_EMBED_QUERY_RESPONSE = {"embedding": [0.82421875, 0.54296875, -0.63671875], "inputTextTokenCount": 14}

AMAZON_BEDROCK_INVOKE_RESPONSE = {
    "text": "Ahoy, fellow programmer! I'm curious, what kind of programming do you enjoy the most?"
}

GOOGLE_GEMINI_GENERATE_CONTENT_RESPONSE = {
    "candidates": [
        {
            "content": {
                "parts": [
                    {
                        "text": "This is a test response from the Gemini model."
                    }
                ],
                "role": "model"
            },
            "finishReason": "STOP",
        }
    ],
    "usageMetadata": {
        "candidatesTokenCount": 402,
        "promptTokenCount": 8,
        "totalTokenCount": 410
    }
}

GOOGLE_GEMINI_INVOKE_RESPONSE = {
    'text': "Ahoy, fellow programmer! I'm curious, what kind of programming do you enjoy the most?"}

GOOGLE_GEMINI_STREAM_GENERATE_CONTENT_RESPONSE = iter(['data: {"candidates": [{"content": {"role": "model","parts": [{'
                                                       '"text": "This is a mocked response from the Gemini model'
                                                       'dust motes danced in"}]},"safetyRatings": [{"category": '
                                                       '"HARM_CATEGORY_HATE_SPEECH","probability": "NEGLIGIBLE",'
                                                       '"probabilityScore": 0.03955078,"severity": '
                                                       '"HARM_SEVERITY_NEGLIGIBLE","severityScore": 0.02722168},'
                                                       '{"category": "HARM_CATEGORY_DANGEROUS_CONTENT","probability": '
                                                       '"NEGLIGIBLE","probabilityScore": 0.07373047,"severity": '
                                                       '"HARM_SEVERITY_NEGLIGIBLE","severityScore": 0.032470703},'
                                                       '{"category": "HARM_CATEGORY_HARASSMENT","probability": '
                                                       '"NEGLIGIBLE","probabilityScore": 0.13085938,"severity": '
                                                       '"HARM_SEVERITY_NEGLIGIBLE","severityScore": 0.026367188},'
                                                       '{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","probability": '
                                                       '"NEGLIGIBLE","probabilityScore": 0.14550781,"severity": '
                                                       '"HARM_SEVERITY_NEGLIGIBLE","severityScore": 0.125}]}]}\n\n'])

GOOGLE_GEMINI_STREAM_ASYNC_RESPONSE = {
    "candidates": [
        {
            "content": {
                "text": "This is a mocked response from the Gemini model."
            },
            "safetyRatings": [
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "probability": "NEGLIGIBLE",
                    "probabilityScore": 0.03955078
                }
            ]
        }
    ]
}

AMAZON_BEDROCK_RESPONSE = [
    b'data: {"type":"message_start","message":{"id":"msg_bdrk_01Qgxvf5RHJD2PdoHeyHTV1x","type":"message",'
    b'"role":"assistant","model":"claude-3-opus-20240229","content":[],"stop_reason":null,"stop_sequence":null,'
    b'"usage":{"input_tokens":28,"output_tokens":1}}}\n\n',
    b'data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}\n\n',
    b'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"Here"}}\n\n',
    b'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" is a "}}\n\n',
    b'data: {"type":"content_block_stop","index":0}\n\n',
    b'data: {"type":"message_delta","delta":{"stop_reason":"max_tokens","stop_sequence":null},'
    b'"usage":{"output_tokens":10}}\n\n',
    b'data: {"type":"message_stop","amazon-bedrock-invocationMetrics":{"inputTokenCount":28,'
    b'"outputTokenCount":10,"invocationLatency":976,"firstByteLatency":636}}\n\n']

AMAZON_BEDROCK_STREAM_GENERATE_CONTENT_RESPONSE = iter(AMAZON_BEDROCK_RESPONSE)

AMAZON_BEDROCK_BROKEN_STREAM_RESPONSE = (
    {
        'ResponseMetadata': {
            'RequestId': 'example-request-id',
            'HTTPStatusCode': 200,
            'HTTPHeaders': {
                'content-type': 'application/vnd.amazon.eventstream',
            }
        },
        'body': iter([
            {'chunk':
                 {'bytes':
                      b'{"outputText":"\\nOnce upon a time, there was a boat that was very old. It '
                      b'had been used for many years to transport goods and people across the sea. '
                      b'The boat was made of wood and had a st","index":0,'
                      b'"totalOutputTextTokenCount":null,"completionReason":null,"inputTextTokenCount":15}'}},
            {'chunk':
                 {'bytes':
                           b'{"outputText":"urdy frame. It had a large sail that could catch the wind and help '
                           b'the boat move quickly across the water.\\n\\nOne day, the boat was being used to '
                           b'transport a group of people to a new island. '
                           b'The weather was bad, and the sea was rough. The boat was tossed around by the waves, '
                           b'and the passengers wer","index":0,"totalOutputTextTokenCount":null,'
                           b'"completionReason":null,"inputTextTokenCount":null}'}},
            {'chunk':
                # Broken byte indicator
                 {'bytes': """{"outputText":"e scared.\\n\\nThe captain of the boat was a skilled sailor,'
                                b' and he knew how to handle the boat in rough weather. He steered the boat carefully,'
                                b' and he used the sails to help him move forward.\\n\\nDespite the rough weather,'
                                b' the boat made it to the island safely. The passengers were grateful to t",'
                                b'"index":0,"totalOutputTextTokenCount":null,"completionReason":null,'
                                b'"inputTextTokenCount":null}'"""}},
            {'chunk':
                 {'bytes': b'{"outputText":"he captain for his skill and bravery.\\n\\nFrom that day on, '
                                b'the boat became known as the \\"Courageous Boat.\\" It was a symbol of bravery '
                                b'and resilience, and it was used to transport people and goods across the sea '
                                b'for many years to come.","index":0,"totalOutputTextTokenCount":229,'
                                b'"completionReason":"FINISH","inputTextTokenCount":null,'
                                b'"amazon-bedrock-invocationMetrics":{"inputTokenCount":15,"outputTokenCount":229,'
                                b'"invocationLatency":5714,"firstByteLatency":2551}}'}}
        ])
    })

# Constants for prompt registry testing
SCENARIO = 'test_scenario'
TEMPLATE_NAME = 'test_template'
TEMPLATE_ID = '123'
VERSION = '0.1.0'
TEMPLATE_GET_RESPONSE = PromptTemplateGetResponse(
    id=TEMPLATE_ID,
    name=TEMPLATE_NAME,
    version=VERSION,
    scenario=SCENARIO,
    spec=PromptTemplateSpec(
        template=[PromptTemplate(role='system', content='You are a system under test.')],
        defaults={},
        additional_fields={}
    ),
    creation_timestamp=None,
    managed_by=None,
    is_version_head=None
)
TEMPLATE_LIST_RESPONSE = PromptTemplateListResponse(
    count=1,
    resources=[TEMPLATE_GET_RESPONSE]
)
TEMPLATE_POST_RESPONSE = PromptTemplatePostResponse(
    message='Template created successfully',
    id=TEMPLATE_ID,
    scenario=SCENARIO,
    name=TEMPLATE_NAME,
    version=VERSION
)
TEMPLATE_DELETE_RESPONSE = PromptTemplateDeleteResponse(message='deleted')
TEMPLATE_SUBSTITUTION_REQUEST = PromptTemplateSubstitutionRequest(input_params={'inputExample': 'substitution test'})
TEMPLATE_SUBSTITUTION_RESPONSE = PromptTemplateSubstitutionResponse(
    parsed_prompt=[PromptTemplate(role='system', content='You are a system under test.')])
TEMPLATE_YAML = """
name: simple
version: 0.0.1
scenario: my-scenario
spec:
  template:
    - role: "system"
      content: "{{ ?instruction }}"
    - role: "user"
      content: "Some more {{ ?user_input }}"
"""

ORCHESTRATION_CONFIG_NAME = 'test_config'
ORCHESTRATION_CONFIG_ID = '123'

ORCHESTRATION_CONFIG_YAML = """
name: simple
version: 0.0.1
scenario: my-scenario
spec:
    modules:
      - prompt_templating:
          prompt:
            template:
              - role: user
                content: "First man on the moon, answer in json"
            response_format:
              type: json_object
          model:
            name: gpt-4o
"""

ORCHESTRATION_CONFIG_POST_RESPONSE = {
  "id": ORCHESTRATION_CONFIG_ID,
  "name": ORCHESTRATION_CONFIG_NAME,
  "version": VERSION,
  "scenario": SCENARIO,
  "message": "Orchestration config created successfully."
}

ORCHESTRATION_CONFIG_LIST_RESPONSE = {
  "count": 3,
  "resources": [
    {
      "id": "<orchestrationConfigId1>",
      "name": ORCHESTRATION_CONFIG_NAME,
      "version": VERSION,
      "scenario": SCENARIO,
      "creation_timestamp": "2024-08-18T14:50:17.157000",
      "managed_by": "imperative",
      "is_version_head": True
    },
    {
      "id": "<orchestrationConfigId2>",
      "name": ORCHESTRATION_CONFIG_NAME,
      "version": VERSION,
      "scenario": SCENARIO,
      "creation_timestamp": "2024-08-19T10:30:45.123000",
      "managed_by": "declarative",
      "is_version_head": True
    },
    {
      "id": "<orchestrationConfigId3>",
      "name": ORCHESTRATION_CONFIG_NAME,
      "version": VERSION,
      "scenario": SCENARIO,
      "creation_timestamp": "2024-08-19T10:30:45.123000",
      "managed_by": "imperative",
      "is_version_head": True
    }
  ]
}

ORCHESTRATION_CONFIG_LIST_RESPONSE_WITH_SPEC = {
  "count": 1,
  "resources": [
    {
      "id": "<orchestrationConfigId1>",
      "name": ORCHESTRATION_CONFIG_NAME,
      "version": VERSION,
      "scenario": SCENARIO,
      "creation_timestamp": "2024-08-18T14:50:17.157000",
      "managed_by": "imperative",
      "is_version_head": True,
      "spec": {
        "modules": {
          "prompt_templating": {
            "prompt": {
              "template_ref": {
                "id": "<promptTemplateId>"
              }
            },
            "model": {
              "name": "<model>",
              "params": {
                "temperature": 0.7,
                "max_tokens": 500
              }
            }
          }
        }
      }
    }
  ]
}

ORCHESTRATION_CONFIG_GET_RESPONSE = {
  "id": ORCHESTRATION_CONFIG_ID,
  "name": ORCHESTRATION_CONFIG_NAME,
  "version": VERSION,
  "scenario": SCENARIO,
  "creation_timestamp": "string",
  "managed_by": "string",
  "is_version_head": True,
  "resource_group_id": "string",
  "spec": {
    "modules": {
      "prompt_templating": {
        "prompt": {
          "template": [
            {
              "role": "user",
              "content": "How can the features of AI in SAP BTP specifically {{'{{?groundingOutput}}'}}, be applied to {{'{{?inputContext}}'}}"
            }
          ],
          "defaults": {
            "inputContext": "The default text that will be used in the template if inputContext is not set"
          }
        },
        "model": {
          "name": "gpt-4o-mini",
          "version": "latest",
          "params": {
            "max_completion_tokens": 300,
            "temperature": 0.1,
          },
          "timeout": 600,
          "max_retries": 2
        }
      },
      "filtering": {
        "output": {
          "filters": [
            {
              "type": "azure_content_safety",
              "config": {
                "hate": 0,
                "self_harm": 0,
                "sexual": 0,
                "violence": 0,
                "protected_material_code": False
              }
            },
            {
              "type": "llama_guard_3_8b",
              "config": {
                "violent_crimes": True,
                "non_violent_crimes": True,
                "sex_crimes": True,
                "child_exploitation": True,
                "defamation": True,
                "specialized_advice": True,
                "privacy": True,
                "intellectual_property": True,
                "indiscriminate_weapons": True,
                "hate": True,
                "self_harm": True,
                "sexual_content": True,
                "elections": True,
                "code_interpreter_abuse": True
              }
            }
          ],
          "stream_options": {
            "overlap": 0
          }
        }
      },
      "masking": {
        "providers": [
          {
            "type": "sap_data_privacy_integration",
            "method": "anonymization",
            "entities": [
              {
                "type": "profile-person",
                "replacement_strategy": {
                  "method": "constant",
                  "value": "NAME_REDACTED"
                }
              },
              {
                "regex": "string",
                "replacement_strategy": {
                  "method": "constant",
                  "value": "NAME_REDACTED"
                }
              }
            ],
            "allowlist": [
              "SAP",
              "Joule"
            ],
            "mask_grounding_input": {
              "enabled": False
            }
          }
        ]
      },
      "grounding": {
        "type": "document_grounding_service",
        "config": {
          "filters": [
            {
              "id": "string",
              "search_config": {
                "max_chunk_count": 1
              },
              "data_repositories": [
                "*"
              ],
              "data_repository_type": "vector",
              "data_repository_metadata": [
                {
                  "key": "string",
                  "value": [
                    "string"
                  ]
                }
              ],
              "document_metadata": [
                {
                  "key": "string",
                  "value": [
                    "string"
                  ],
                  "select_mode": [
                    "ignoreIfKeyAbsent"
                  ]
                }
              ],
              "chunk_metadata": [
                {
                  "key": "string",
                  "value": [
                    "string"
                  ]
                }
              ]
            }
          ],
          "placeholders": {
            "input": [
              "groundingInput"
            ],
            "output": "groundingOutput"
          },
          "metadata_params": [
            "string"
          ]
        }
      },
      "translation": {
        "input": {
          "type": "sap_document_translation",
          "translate_messages_history": True,
          "config": {
            "source_language": "de-DE",
            "apply_to": [
              {
                "category": "placeholders",
                "items": [
                  "groundingInput",
                  "inputContext"
                ],
                "source_language": "de-DE"
              }
            ],
            "target_language": "en-US"
          }
        },
        "output": {
          "type": "sap_document_translation",
          "config": {
            "source_language": "de-DE",
            "target_language": "en-US"
          }
        }
      }
    },
    "stream": {
      "enabled": False
    }
  }
}

ORCHESTRATION_CONFIG_DELETE_RESPONSE = {
  "message": "Orchestration config deleted successfully."
}


# end of prompt registry testing constants

class AsyncIteratorWrapper:
    def __init__(self, async_generator):
        self.async_generator = async_generator

    def __call__(self, *args, **kwargs):
        return self

    def __aiter__(self):
        return self.async_generator
