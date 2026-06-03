import json
import sqlite3
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from io import BytesIO

import gen_ai_hub.evaluations.helpers.s3_file_client as module
from gen_ai_hub.evaluations.helpers.collector import ValidationCollector
from gen_ai_hub.evaluations.exceptions.error_codes import ErrorCode
from gen_ai_hub.evaluations.helpers.s3_file_client import S3FileClient


class TestS3FileClient(unittest.TestCase):

    def setUp(self):
        self.collector = ValidationCollector()

    def _mock_boto_session(self, mock_s3=None):
        if mock_s3 is None:
            mock_s3 = MagicMock()

        patcher = patch("boto3.Session")
        self.addCleanup(patcher.stop)
        mock_session = patcher.start()

        session_obj = MagicMock()
        session_obj.client.return_value = mock_s3
        session_obj.region_name = "us-east-1"
        mock_session.return_value = session_obj

        return mock_s3

    def test_init_valid_bucket(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.head_bucket.return_value = True

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertIsInstance(c, S3FileClient)
        self.assertFalse(self.collector.has_errors())

    def test_init_bucket_not_found(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.head_bucket.side_effect = module.ClientError(
            {"Error": {"Code": "404"}}, "HeadBucket"
        )

        S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.INVALID_S3_CLIENT_ERROR,
        )

    def test_init_bucket_forbidden(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.head_bucket.side_effect = module.ClientError(
            {"Error": {"Code": "403"}}, "HeadBucket"
        )

        S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.INVALID_S3_CLIENT_ERROR,
        )

    def test_init_no_credentials(self):
        with patch("boto3.Session", side_effect=module.NoCredentialsError()):
            S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.INVALID_S3_CLIENT_ERROR,
        )

    def test_init_generic_error(self):
        with patch("boto3.Session", side_effect=Exception("boom")):
            S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.INVALID_S3_CLIENT_ERROR,
        )

    def test_read_json_success(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.get_object.return_value = {
            "Body": BytesIO(json.dumps({"a": 1}).encode())
        }

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(c.read_json("x.json"), {"a": 1})

    def test_read_json_empty(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.get_object.return_value = {"Body": BytesIO(b"")}

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(c.read_json("x.json"), [])

    def test_read_json_invalid(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.get_object.return_value = {"Body": BytesIO(b"{bad json")}

        c = S3FileClient("bucket", error_collector=self.collector)
        c.read_json("x.json")

        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.READ_FILE_DATA_FROM_ARTIFACT_ERROR,
        )

    def test_read_json_boto_error(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.get_object.side_effect = module.ClientError(
            {"Error": {"Code": "NoSuchKey"}}, "GetObject"
        )

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(c.read_json("x.json"), [])
        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.READ_FILE_DATA_FROM_ARTIFACT_ERROR,
        )

    def test_read_json_generic_error(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.get_object.side_effect = RuntimeError("boom")

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(c.read_json("x.json"), [])
        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.READ_FILE_DATA_FROM_ARTIFACT_ERROR,
        )

    def test_read_jsonl_success(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.get_object.return_value = {
            "Body": BytesIO(b'{"x":1}\n{"y":2}')
        }

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(
            c.read_jsonl("x.jsonl"),
            [{"x": 1}, {"y": 2}],
        )

    def test_read_csv_success(self):
        mock_s3 = self._mock_boto_session()
        csv_data = "a,b\n1,2\n3,4"
        mock_s3.get_object.return_value = {
            "Body": BytesIO(csv_data.encode())
        }

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(
            c.read_csv("x.csv"),
            [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}],
        )

    def test_upload_json_success(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.put_object.return_value = True

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertTrue(c.upload_json({"a": 1}, "x.json"))

    def test_upload_json_failure(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.put_object.side_effect = Exception("boom")

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertFalse(c.upload_json({"a": 1}, "x.json"))
        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.FILE_UPLOAD_ERROR,
        )

    def test_get_sqlitedb_tables_data_from_s3(self):
        mock_s3 = self._mock_boto_session()

        tmp = tempfile.NamedTemporaryFile(delete=False)
        conn = sqlite3.connect(tmp.name)
        conn.execute("CREATE TABLE t (id INTEGER, val TEXT)")
        conn.execute("INSERT INTO t VALUES (1,'A')")
        conn.commit()
        conn.close()

        with open(tmp.name, "rb") as f:
            db_bytes = f.read()

        mock_s3.download_fileobj.side_effect = (
            lambda b, k, fd: fd.write(db_bytes)
        )

        c = S3FileClient("bucket", error_collector=self.collector)

        out = c.get_sqlitedb_tables_data_from_s3("db.sqlite", ["t"])

        self.assertEqual(
            out["t"],
            [{"id": 1, "val": "A"}],
        )


import json
import sqlite3
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from io import BytesIO

import gen_ai_hub.evaluations.helpers.s3_file_client as module
from gen_ai_hub.evaluations.helpers.collector import ValidationCollector
from gen_ai_hub.evaluations.exceptions.error_codes import ErrorCode
from gen_ai_hub.evaluations.helpers.s3_file_client import S3FileClient



class TestS3FileClient(unittest.TestCase):

    def setUp(self):
        self.collector = ValidationCollector()

    def _mock_boto_session(self):
        mock_s3 = MagicMock()

        patcher = patch("boto3.Session")
        self.addCleanup(patcher.stop)
        mock_session = patcher.start()

        session_obj = MagicMock()
        session_obj.client.return_value = mock_s3
        session_obj.region_name = "us-east-1"
        mock_session.return_value = session_obj

        return mock_s3

    def test_init_valid_bucket(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.head_bucket.return_value = True

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertIsInstance(c, S3FileClient)
        self.assertFalse(self.collector.has_errors())

    def test_init_bucket_not_found(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.head_bucket.side_effect = module.ClientError(
            {"Error": {"Code": "404"}}, "HeadBucket"
        )

        S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.INVALID_S3_CLIENT_ERROR,
        )

    def test_init_bucket_forbidden(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.head_bucket.side_effect = module.ClientError(
            {"Error": {"Code": "403"}}, "HeadBucket"
        )

        S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.INVALID_S3_CLIENT_ERROR,
        )

    def test_init_no_credentials(self):
        with patch("boto3.Session", side_effect=module.NoCredentialsError()):
            S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.INVALID_S3_CLIENT_ERROR,
        )

    def test_init_generic_error(self):
        with patch("boto3.Session", side_effect=Exception("boom")):
            S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.INVALID_S3_CLIENT_ERROR,
        )

    def test_read_json_success(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.get_object.return_value = {
            "Body": BytesIO(json.dumps({"a": 1}).encode())
        }

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(c.read_json("x.json"), {"a": 1})

    def test_read_json_empty(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.get_object.return_value = {"Body": BytesIO(b"")}

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(c.read_json("x.json"), [])

    def test_read_json_invalid(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.get_object.return_value = {"Body": BytesIO(b"{bad json")}

        c = S3FileClient("bucket", error_collector=self.collector)
        c.read_json("x.json")

        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.READ_FILE_DATA_FROM_ARTIFACT_ERROR,
        )

    def test_read_json_boto_error(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.get_object.side_effect = module.ClientError(
            {"Error": {"Code": "NoSuchKey"}}, "GetObject"
        )

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(c.read_json("x.json"), [])
        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.READ_FILE_DATA_FROM_ARTIFACT_ERROR,
        )

    def test_read_json_generic_error(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.get_object.side_effect = RuntimeError("boom")

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(c.read_json("x.json"), [])
        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.READ_FILE_DATA_FROM_ARTIFACT_ERROR,
        )

    def test_read_jsonl_success(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.get_object.return_value = {
            "Body": BytesIO(b'{"x":1}\n{"y":2}')
        }

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(
            c.read_jsonl("x.jsonl"),
            [{"x": 1}, {"y": 2}],
        )

    def test_read_jsonl_invalid_lines(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.get_object.return_value = {
            "Body": BytesIO(b'{"x":1}\nbad\n{"y":2}')
        }

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(
            c.read_jsonl("x.jsonl"),
            [{"x": 1}, {"y": 2}],
        )

    def test_read_csv_success(self):
        mock_s3 = self._mock_boto_session()
        csv_data = "a,b\n1,2\n3,4"
        mock_s3.get_object.return_value = {
            "Body": BytesIO(csv_data.encode())
        }

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertEqual(
            c.read_csv("x.csv"),
            [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}],
        )

    def test_read_csv_parsing_error(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.get_object.return_value = {"Body": BytesIO(b"bad,data")}

        with patch("pandas.read_csv", side_effect=module.csv.Error("bad csv")):
            c = S3FileClient("bucket", error_collector=self.collector)

            self.assertEqual(c.read_csv("x.csv"), [])
            self.assertEqual(
                self.collector.errors[0][0],
                ErrorCode.READ_FILE_DATA_FROM_ARTIFACT_ERROR,
            )

    def test_upload_json_success(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.put_object.return_value = True

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertTrue(c.upload_json({"a": 1}, "x.json"))

    def test_upload_json_failure(self):
        mock_s3 = self._mock_boto_session()
        mock_s3.put_object.side_effect = Exception("boom")

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertFalse(c.upload_json({"a": 1}, "x.json"))
        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.FILE_UPLOAD_ERROR,
        )

    def test_upload_csv_empty_data(self):
        mock_s3 = self._mock_boto_session()

        c = S3FileClient("bucket", error_collector=self.collector)

        self.assertFalse(c.upload_csv([], "x.csv"))
        self.assertEqual(
            self.collector.errors[0][0],
            ErrorCode.FILE_UPLOAD_ERROR,
        )

    def test_get_sqlitedb_tables_data_from_s3(self):
        mock_s3 = self._mock_boto_session()

        tmp = tempfile.NamedTemporaryFile(delete=False)
        conn = sqlite3.connect(tmp.name)
        conn.execute("CREATE TABLE t (id INTEGER, val TEXT)")
        conn.execute("INSERT INTO t VALUES (1,'A')")
        conn.commit()
        conn.close()

        with open(tmp.name, "rb") as f:
            db_bytes = f.read()

        mock_s3.download_fileobj.side_effect = (
            lambda b, k, fd: fd.write(db_bytes)
        )

        c = S3FileClient("bucket", error_collector=self.collector)

        out = c.get_sqlitedb_tables_data_from_s3("db.sqlite", ["t"])

        self.assertEqual(
            out["t"],
            [{"id": 1, "val": "A"}],
        )
