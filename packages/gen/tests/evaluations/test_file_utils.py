import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from gen_ai_hub.evaluations.utils.file_utils import (
    load_config_file,
    read_local_csv_file,
)
from gen_ai_hub.evaluations.utils.aicore_utils import generate_random_id
from gen_ai_hub.evaluations.helpers.collector import ValidationCollector


class TestFileUtils(unittest.TestCase):

    def write_file(self, tmp_path: Path, name: str, content: str):
        file = tmp_path / name
        file.write_text(content, encoding="utf-8")
        return file

    def test_load_config_file_file_not_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            collector = ValidationCollector()

            result = load_config_file(tmp_path / "missing.json", collector)

            self.assertEqual(result, [])
            with self.assertRaisesRegex(RuntimeError, "Config file not found"):
                collector.raise_if_errors()

    def test_load_config_file_path_is_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            collector = ValidationCollector()

            result = load_config_file(tmp_path, collector)

            self.assertEqual(result, [])
            with self.assertRaisesRegex(RuntimeError, "is not an actual file"):
                collector.raise_if_errors()

    def test_load_config_file_unsupported_file_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            collector = ValidationCollector()
            file = self.write_file(tmp_path, "config.txt", "abc")

            result = load_config_file(file, collector)

            self.assertEqual(result, [])
            with self.assertRaisesRegex(RuntimeError, "not supported"):
                collector.raise_if_errors()

    def test_load_config_file_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            collector = ValidationCollector()
            data = {"key": "value"}
            file = self.write_file(tmp_path, "config.json", json.dumps(data))

            result = load_config_file(file, collector)

            self.assertEqual(result, data)

    def test_load_config_file_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            collector = ValidationCollector()
            file = self.write_file(tmp_path, "config.json", "{invalid json}")

            result = load_config_file(file, collector)

            self.assertEqual(result, [])
            with self.assertRaisesRegex(RuntimeError, "Failed to parse config file"):
                collector.raise_if_errors()

    def test_load_config_file_valid_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            collector = ValidationCollector()
            content = '{"a": 1}\n{"b": 2}\n'
            file = self.write_file(tmp_path, "config.jsonl", content)

            result = load_config_file(file, collector)

            self.assertEqual(result, [{"a": 1}, {"b": 2}])

    def test_load_config_file_valid_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            collector = ValidationCollector()
            file = self.write_file(tmp_path, "config.csv", "col1,col2\n1,2\n3,4\n")

            result = load_config_file(file, collector)

            self.assertEqual(
                result,
                [
                    {"col1": "1", "col2": "2"},
                    {"col1": "3", "col2": "4"},
                ],
            )

    def test_generate_random_id_format(self):
        value = generate_random_id()

        self.assertIsInstance(value, str)
        self.assertEqual(len(value), 32)
        int(value, 16)  # should not raise

    def test_generate_random_id_uniqueness(self):
        ids = {generate_random_id() for _ in range(100)}
        self.assertEqual(len(ids), 100)

    def test_load_config_file_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            collector = ValidationCollector()
            file = self.write_file(tmp_path, "config.json", "{}")

            with patch("json.load", side_effect=ValueError("forced value error")):
                result = load_config_file(file, collector)

            self.assertEqual(result, [])
            with self.assertRaisesRegex(RuntimeError, "Value error reading config file"):
                collector.raise_if_errors()

    def test_load_config_file_generic_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            collector = ValidationCollector()
            file = self.write_file(tmp_path, "config.json", "{}")

            with patch("json.load", side_effect=RuntimeError("boom")):
                result = load_config_file(file, collector)

            self.assertEqual(result, [])
            with self.assertRaisesRegex(RuntimeError, "Reading config file .* failed with"):
                collector.raise_if_errors()

    def test_read_local_csv_file_generic_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            collector = ValidationCollector()
            file = self.write_file(tmp_path, "config.csv", "a,b\n1,2")

            with patch("pandas.read_csv", side_effect=RuntimeError("unexpected error")):
                result = read_local_csv_file(file, collector)

            self.assertEqual(result, [])
            with self.assertRaisesRegex(RuntimeError, "Reading config file .* failed with"):
                collector.raise_if_errors()
