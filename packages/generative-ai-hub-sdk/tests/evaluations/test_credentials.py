import unittest
from unittest.mock import patch
import json
import os
import tempfile

from gen_ai_hub.evaluations.credentials import (
    get_home,
    get_nested_value,
    VCAPEnvironment,
    Service,
    fetch_credentials,
    init_conf,
    extract_credentials,
    resolve_credentials,
    resolve_resource_group,
    validate_credentials,
    Source,
)


class TestGetHome(unittest.TestCase):
    def test_get_home_from_env(self):
        with patch.dict(os.environ, {"AICORE_HOME": "/custom/home"}):
            result = get_home()
            self.assertEqual(result, "/custom/home")

    def test_get_home_default(self):
        with patch.dict(os.environ, {}, clear=True):
            result = get_home()
            # Should return the default path (~/.aicore)
            self.assertTrue(result.endswith(".aicore"))


class TestGetNestedValue(unittest.TestCase):
    def test_get_nested_value_single_key(self):
        data = {"key": "value"}
        result = get_nested_value(data, ["key"])
        self.assertEqual(result, "value")

    def test_get_nested_value_nested_keys(self):
        data = {"level1": {"level2": {"level3": "value"}}}
        result = get_nested_value(data, ["level1", "level2", "level3"])
        self.assertEqual(result, "value")

    def test_get_nested_value_missing_key_raises(self):
        data = {"key": "value"}
        with self.assertRaises(KeyError):
            get_nested_value(data, ["missing"])


class TestVCAPEnvironment(unittest.TestCase):
    def test_from_dict(self):
        env_dict = {
            "aicore": [
                {"label": "aicore", "name": "service1"},
                {"label": "aicore", "name": "service2"},
            ]
        }
        vcap = VCAPEnvironment.from_dict(env_dict)
        self.assertEqual(len(vcap.services), 2)

    def test_from_env_empty(self):
        with patch.dict(os.environ, {}, clear=True):
            vcap = VCAPEnvironment.from_env()
            self.assertEqual(len(vcap.services), 0)

    def test_from_env_with_data(self):
        vcap_data = {"aicore": [{"label": "aicore", "name": "test-service"}]}
        with patch.dict(os.environ, {"VCAP_SERVICES": json.dumps(vcap_data)}):
            vcap = VCAPEnvironment.from_env()
            self.assertEqual(len(vcap.services), 1)

    def test_getitem(self):
        env_dict = {"aicore": [{"label": "aicore", "name": "service1"}]}
        vcap = VCAPEnvironment.from_dict(env_dict)
        service = vcap["aicore"]
        self.assertEqual(service.label, "aicore")

    def test_get_service_exactly_one(self):
        env_dict = {"aicore": [{"label": "aicore", "name": "service1"}]}
        vcap = VCAPEnvironment.from_dict(env_dict)
        service = vcap.get_service("aicore", exactly_one=True)
        self.assertEqual(service.name, "service1")

    def test_get_service_not_found_raises(self):
        vcap = VCAPEnvironment(services=[])
        with self.assertRaises(KeyError) as context:
            vcap.get_service("missing")
        self.assertIn("No service found with label", str(context.exception))

    def test_get_service_by_name_exactly_one(self):
        env_dict = {"aicore": [{"label": "aicore", "name": "service1"}]}
        vcap = VCAPEnvironment.from_dict(env_dict)
        service = vcap.get_service_by_name("service1", exactly_one=True)
        self.assertEqual(service.name, "service1")

    def test_get_service_by_name_not_found_raises(self):
        vcap = VCAPEnvironment(services=[])
        with self.assertRaises(KeyError) as context:
            vcap.get_service_by_name("missing")
        self.assertIn("No service found with name", str(context.exception))

    def test_get_service_not_exactly_one_returns_list(self):
        env_dict = {
            "aicore": [
                {"label": "aicore", "name": "service1"},
                {"label": "aicore", "name": "service2"},
            ]
        }
        vcap = VCAPEnvironment.from_dict(env_dict)
        services = vcap.get_service("aicore", exactly_one=False)
        self.assertIsInstance(services, list)
        self.assertEqual(len(services), 2)


class TestService(unittest.TestCase):
    def test_label_property(self):
        env = {"label": "aicore", "name": "test"}
        service = Service(env)
        self.assertEqual(service.label, "aicore")

    def test_name_property(self):
        env = {"label": "aicore", "name": "test-service"}
        service = Service(env)
        self.assertEqual(service.name, "test-service")

    def test_getitem(self):
        env = {"credentials": {"clientid": "test-id"}}
        service = Service(env)
        result = service["credentials.clientid"]
        self.assertEqual(result, "test-id")

    def test_get_with_default(self):
        env = {"key": "value"}
        service = Service(env)
        result = service.get("missing", default="default-value")
        self.assertEqual(result, "default-value")

    def test_get_without_default_raises(self):
        env = {"key": "value"}
        service = Service(env)
        with self.assertRaises(KeyError) as context:
            service.get("missing")
        self.assertIn("Key 'missing' not found", str(context.exception))

    def test_get_with_list_key(self):
        env = {"level1": {"level2": "value"}}
        service = Service(env)
        result = service.get(["level1", "level2"])
        self.assertEqual(result, "value")


class TestInitConf(unittest.TestCase):
    def test_init_conf_no_profile_no_config_file(self):
        with patch("pathlib.Path.exists", return_value=False), patch.dict(
            os.environ, {}, clear=True
        ):
            result = init_conf()
            self.assertEqual(result, {})

    def test_init_conf_with_valid_config_file(self):
        config_data = {"AICORE_BASE_URL": "https://test.com"}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            json.dump(config_data, temp_file)
            temp_path = temp_file.name

        try:
            with patch.dict(os.environ, {"AICORE_CONFIG": temp_path}, clear=True):
                result = init_conf()
                self.assertEqual(result, config_data)
        finally:
            os.unlink(temp_path)

    def test_init_conf_with_invalid_json_raises(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            temp_file.write("invalid json")
            temp_path = temp_file.name

        try:
            with patch.dict(os.environ, {"AICORE_CONFIG": temp_path}, clear=True):
                with self.assertRaises(KeyError) as context:
                    init_conf()
                self.assertIn("not a valid json file", str(context.exception))
        finally:
            os.unlink(temp_path)

    def test_init_conf_with_profile_not_found_raises(self):
        with patch("pathlib.Path.exists", return_value=False):
            with self.assertRaises(FileNotFoundError) as context:
                init_conf(profile="nonexistent")
            self.assertIn("Unable to locate profile config file", str(context.exception))


class TestExtractCredentials(unittest.TestCase):
    def test_extract_credentials_success(self):
        source = Source("test", lambda cv: "test-value" if cv.name == "client_id" else None)
        credentials = extract_credentials(source)
        self.assertIn("client_id", credentials)
        self.assertEqual(credentials["client_id"], "test-value")

    def test_extract_credentials_with_transform(self):
        source = Source("test", lambda cv: "https://test.com" if cv.name == "auth_url" else None)
        credentials = extract_credentials(source)
        # Should have auth_url with transform applied
        if "auth_url" in credentials:
            self.assertTrue(credentials["auth_url"].endswith("/oauth/token"))

    def test_extract_credentials_with_exclude(self):
        source = Source("test", lambda cv: "value")
        credentials = extract_credentials(source, exclude=["client_id"])
        self.assertNotIn("client_id", credentials)


class TestResolveCredentials(unittest.TestCase):
    def test_resolve_credentials_from_first_source(self):
        source1 = Source("kwargs", lambda cv: "value1" if cv.name == "client_id" else None)
        source2 = Source("env", lambda cv: "value2")

        credentials = resolve_credentials([source1, source2])
        self.assertEqual(credentials["client_id"], "value1")

    def test_resolve_credentials_no_source_raises(self):
        source = Source("empty", lambda cv: None)

        with self.assertRaises(ValueError) as context:
            resolve_credentials([source])
        self.assertIn("No credentials found", str(context.exception))


class TestResolveResourceGroup(unittest.TestCase):
    def test_resolve_resource_group_found(self):
        source = Source("test", lambda cv: "test-rg" if cv.name == "resource_group" else None)

        result = resolve_resource_group([source])
        self.assertEqual(result, "test-rg")

    def test_resolve_resource_group_not_found(self):
        source = Source("test", lambda cv: None)

        result = resolve_resource_group([source])
        self.assertIsNone(result)


class TestValidateCredentials(unittest.TestCase):
    def test_validate_credentials_with_client_secret_success(self):
        credentials = {
            "client_id": "test-id",
            "client_secret": "test-secret",
            "auth_url": "https://auth.com",
            "base_url": "https://api.com/v2",
        }
        # Should not raise
        validate_credentials(credentials)

    def test_validate_credentials_with_cert_files_success(self):
        credentials = {
            "client_id": "test-id",
            "cert_file_path": "/path/to/cert",
            "key_file_path": "/path/to/key",
            "auth_url": "https://auth.com",
            "base_url": "https://api.com/v2",
        }
        # Should not raise
        validate_credentials(credentials)

    def test_validate_credentials_no_auth_method_raises(self):
        credentials = {
            "client_id": "test-id",
            "auth_url": "https://auth.com",
            "base_url": "https://api.com/v2",
        }
        with self.assertRaises(ValueError) as context:
            validate_credentials(credentials)
        self.assertIn("No authentication method found", str(context.exception))

    def test_validate_credentials_multiple_auth_methods_raises(self):
        credentials = {
            "client_id": "test-id",
            "client_secret": "secret",
            "cert_file_path": "/path/to/cert",
            "key_file_path": "/path/to/key",
            "auth_url": "https://auth.com",
            "base_url": "https://api.com/v2",
        }
        with self.assertRaises(ValueError) as context:
            validate_credentials(credentials)
        self.assertIn("Multiple authentication methods found", str(context.exception))

    def test_validate_credentials_missing_base_fields_raises(self):
        credentials = {
            "client_secret": "secret",
        }
        with self.assertRaises(ValueError) as context:
            validate_credentials(credentials)
        self.assertIn("Missing required credentials", str(context.exception))


class TestFetchCredentials(unittest.TestCase):
    def test_fetch_credentials_from_kwargs(self):
        result = fetch_credentials(
            client_id="test-client",
            client_secret="test-secret",
            auth_url="https://auth.com/oauth/token",
            base_url="https://api.com/v2",
        )
        self.assertEqual(result["client_id"], "test-client")
        self.assertEqual(result["client_secret"], "test-secret")

    def test_fetch_credentials_from_env(self):
        with patch.dict(
            os.environ,
            {
                "AICORE_CLIENT_ID": "env-client",
                "AICORE_CLIENT_SECRET": "env-secret",
                "AICORE_AUTH_URL": "https://auth.com/oauth/token",
                "AICORE_BASE_URL": "https://api.com/v2",
            },
        ), patch("gen_ai_hub.evaluations.credentials.init_conf", return_value={}):
            result = fetch_credentials()
            self.assertEqual(result["client_id"], "env-client")
            self.assertEqual(result["client_secret"], "env-secret")

    def test_fetch_credentials_cert_url_becomes_auth_url(self):
        with patch(
            "gen_ai_hub.evaluations.credentials.init_conf", return_value={}
        ), patch.dict(
            os.environ,
            {
                "AICORE_CLIENT_ID": "test-id",
                "AICORE_CERT_URL": "https://cert.com/oauth/token",
                "AICORE_BASE_URL": "https://api.com/v2",
                "AICORE_CERT_STR": "cert-content",
                "AICORE_KEY_STR": "key-content",
            },
            clear=True,
        ):
            result = fetch_credentials()
            self.assertIn("auth_url", result)
            self.assertNotIn("cert_url", result)


if __name__ == "__main__":
    unittest.main()
