"""Verify structured errors are compatible with message-only Prism peers."""

import importlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from google.protobuf import descriptor_pb2, descriptor_pool, message_factory


class ErrorResponseContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        generated = tempfile.TemporaryDirectory()
        cls.addClassCleanup(generated.cleanup)
        root = Path(__file__).resolve().parents[1]
        subprocess.run(
            [sys.executable, "-m", "grpc_tools.protoc", f"-I{root}",
             f"--python_out={generated.name}"]
            + [str(path) for path in sorted(root.glob("org/polypheny/prism/*.proto"))],
            check=True,
        )
        sys.path.insert(0, generated.name)
        cls.addClassCleanup(sys.path.remove, generated.name)
        cls.protocol = importlib.import_module("org.polypheny.prism.protointerface_pb2")

        legacy_file = descriptor_pb2.FileDescriptorProto(name="legacy_error.proto", syntax="proto3")
        legacy_error = legacy_file.message_type.add(name="ErrorResponse")
        legacy_error.field.add(name="message", number=1, type=descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
        pool = descriptor_pool.DescriptorPool()
        pool.Add(legacy_file)
        cls.legacy_error = message_factory.GetMessageClass(pool.FindMessageTypeByName("ErrorResponse"))

    def test_new_reader_accepts_legacy_error(self):
        legacy = self.legacy_error(message="Legacy error")
        error = self.protocol.ErrorResponse.FromString(legacy.SerializeToString())
        self.assertEqual(error.message, legacy.message)
        self.assertFalse(error.HasField("details"))

    def test_legacy_reader_accepts_structured_error(self):
        response = self.protocol.Response(id=1, last=True)
        response.error_response.message = "Division by zero"
        response.error_response.details.message = response.error_response.message
        response.error_response.details.state = "22012"
        for code in (None, 0, -42):
            with self.subTest(code=code):
                if code is not None:
                    response.error_response.details.error_code = code
                parsed = self.protocol.Response.FromString(response.SerializeToString())
                self.assertEqual(parsed, response)
                details = parsed.error_response.details
                self.assertEqual(details.state, "22012")
                self.assertEqual(details.message, parsed.error_response.message)
                self.assertEqual(details.HasField("error_code"), code is not None)
                if code is not None:
                    self.assertEqual(details.error_code, code)
                legacy = self.legacy_error.FromString(parsed.error_response.SerializeToString())
                self.assertEqual(legacy.message, parsed.error_response.message)
                self.assertEqual(self.protocol.ErrorResponse.FromString(legacy.SerializeToString()),
                                 parsed.error_response)
