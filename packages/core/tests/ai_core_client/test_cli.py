import json
import pathlib
import os
import unittest
from unittest import TestCase
from unittest.mock import patch
import tempfile

from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from ai_core_sdk.helpers import get_home
from ai_core_sdk.helpers.constants import HOME_PATH_ENV_VAR

from click.testing import CliRunner


AICORE_DUMMY_KEY = {
    'serviceurls': {
        'AI_API_URL': 'https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com'
    },
    'appname': '',
    'clientid': '!!!',
    'clientsecret': '???',
    'identityzone': 'xxx',
    'identityzoneid': '',
    'url': 'https://xxx.authentication.sap.hana.ondemand.com'
}

class TestAICoreCLI(TestCase):
    pass

    def test_from_env(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {HOME_PATH_ENV_VAR: temp_dir}):
                from ai_core_sdk.cli import cli
                runner = CliRunner()
                temp_dir = pathlib.Path(temp_dir)
                aicore_key_file = temp_dir / 'aicore-key.json'
                with open(aicore_key_file, 'w') as stream:
                    json.dump(AICORE_DUMMY_KEY, stream)
                result = runner.invoke(cli, [f'configure', '-k', aicore_key_file, '-g', 'default'])
                print(result)
                if result.exception:
                    raise result.exception
                assert result.exit_code == 0, (result.output, result.exit_code)
                with (pathlib.Path(get_home()) / 'config.json').open() as stream:
                    creds = json.load(stream)
                assert creds['AICORE_AUTH_URL'] == f'{AICORE_DUMMY_KEY["url"]}/oauth/token'
                assert creds['AICORE_BASE_URL'] == f'{AICORE_DUMMY_KEY["serviceurls"]["AI_API_URL"]}/v2'
                assert creds['AICORE_CLIENT_ID'] == AICORE_DUMMY_KEY['clientid']
                assert creds['AICORE_CLIENT_SECRET'] == AICORE_DUMMY_KEY['clientsecret']
                AICoreV2Client.from_env()

    def test_from_input(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {HOME_PATH_ENV_VAR: temp_dir}):
                from ai_core_sdk.cli import cli
                runner = CliRunner()
                result = runner.invoke(cli, [f'configure', '-s', AICORE_DUMMY_KEY['clientsecret'],
                                                                '-i', AICORE_DUMMY_KEY['clientid'],
                                                                '-u', AICORE_DUMMY_KEY['url']],
                                       input='https://***.ml.hana.ondemand.com'
                                       )
                print(result)

        print('done')


if __name__ == "__main__":
    unittest.main()
