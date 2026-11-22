"""Verify generated-key selection, results, and identity metadata on the wire."""

import importlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from google.protobuf import descriptor_pb2, descriptor_pool, message_factory


class GeneratedKeysContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        generated = tempfile.TemporaryDirectory()
        cls.addClassCleanup(generated.cleanup)
        root = Path(__file__).resolve().parents[1]
        proto_files = sorted(root.glob("org/polypheny/prism/*.proto"))
        subprocess.run(
            [sys.executable, "-m", "grpc_tools.protoc", f"-I{root}",
             f"--python_out={generated.name}"]
            + [str(path) for path in proto_files],
            check=True,
        )
        sys.path.insert(0, generated.name)
        cls.addClassCleanup(sys.path.remove, generated.name)
        cls.connections = importlib.import_module("org.polypheny.prism.connection_responses_pb2")
        cls.meta = importlib.import_module("org.polypheny.prism.namespace_meta_responses_pb2")
        cls.relational = importlib.import_module("org.polypheny.prism.relational_frame_pb2")
        cls.requests = importlib.import_module("org.polypheny.prism.statement_requests_pb2")
        cls.responses = importlib.import_module("org.polypheny.prism.statement_responses_pb2")
        cls.value = importlib.import_module("org.polypheny.prism.value_pb2")

    def test_requests_preserve_selection_and_order(self):
        selectors = self.requests.GeneratedKeysRequest
        request_types = (
            self.requests.ExecuteUnparameterizedStatementRequest,
            self.requests.PrepareStatementRequest,
        )
        selections = (
            ("all", selectors(all=True), True),
            ("column_names", selectors(column_names=selectors.ColumnNames(names=["key_b", "key_a"])), ["key_b", "key_a"]),
            ("column_indexes", selectors(column_indexes=selectors.ColumnIndexes(indexes=[2, 1])), [2, 1]),
        )
        for request_type in request_types:
            with self.subTest(request=request_type.__name__):
                request = request_type(language_name="sql", statement="INSERT INTO t DEFAULT VALUES")
                self.assertFalse(request.HasField("generated_keys"))
                for name, selector, expected in selections:
                    request.generated_keys.CopyFrom(selector)
                    decoded = request_type.FromString(request.SerializeToString())
                    self.assertEqual(decoded.generated_keys.WhichOneof("selection"), name)
                    self.assertEqual(decoded.generated_keys, selector)
                    if name == "all":
                        actual = decoded.generated_keys.all
                    elif name == "column_names":
                        actual = list(decoded.generated_keys.column_names.names)
                    else:
                        actual = list(decoded.generated_keys.column_indexes.indexes)
                    self.assertEqual(actual, expected)

    def test_batch_keys_identify_the_input_entry(self):
        result = self.responses.StatementBatchResponse(batch_id=41, scalars=[1, 0, 2])
        self.add_key(result.generated_keys.add(statement_index=0).keys, "id", 101)
        keys = result.generated_keys.add(statement_index=2).keys
        self.add_key(keys, "external_id", 9007199254740993)
        keys.relational_frame.rows.add().values.add().long.long = 9007199254740994

        decoded = self.responses.StatementBatchResponse.FromString(result.SerializeToString())
        self.assertEqual(list(decoded.scalars), [1, 0, 2])
        self.assertEqual([entry.statement_index for entry in decoded.generated_keys], [0, 2])
        first, last = (entry.keys.relational_frame for entry in decoded.generated_keys)
        self.assertEqual(first.column_meta[0].column_name, "id")
        self.assertEqual(last.column_meta[0].column_name, "external_id")
        self.assertEqual([row.values[0].long.long for row in last.rows],
                         [9007199254740993, 9007199254740994])

    def test_update_count_remains_compatible_with_legacy_readers(self):
        result = self.responses.StatementResult(scalar=1)
        self.add_key(result.generated_keys, "id", 9007199254740993)
        decoded = self.responses.StatementResult.FromString(result.SerializeToString())
        self.assertEqual(decoded.scalar, 1)
        self.assertFalse(decoded.HasField("frame"))
        self.assertTrue(decoded.generated_keys.is_last)
        self.assertEqual(decoded.generated_keys.relational_frame.rows[0].values[0].long.long,
                         9007199254740993)

        old = self.legacy_statement_result().FromString(result.SerializeToString())
        self.assertEqual(old.scalar, 1)
        self.assertFalse(old.HasField("frame"))
        self.assertEqual(self.responses.StatementResult.FromString(old.SerializeToString()), result)

    def test_metadata_distinguishes_explicit_false_from_an_older_server(self):
        for message_type, field in (
            (self.connections.ConnectionResponse, "supports_generated_keys"),
            (self.meta.Column, "is_auto_increment"),
            (self.relational.ColumnMeta, "is_auto_increment"),
        ):
            with self.subTest(message=message_type.__name__):
                message = message_type()
                self.assertFalse(message.HasField(field))
                for value in (True, False):
                    setattr(message, field, value)
                    decoded = message_type.FromString(message.SerializeToString())
                    self.assertTrue(decoded.HasField(field))
                    self.assertEqual(getattr(decoded, field), value)

    def add_key(self, keys, name, value):
        keys.is_last = True
        column = keys.relational_frame.column_meta.add(column_name=name, is_auto_increment=True)
        column.type_meta.proto_value_type = self.value.BIGINT
        keys.relational_frame.rows.add().values.add().long.long = value

    @staticmethod
    def legacy_statement_result():
        # The old schema uses fields 1 and 2 and interprets only field 2 as a regular result frame.
        file = descriptor_pb2.FileDescriptorProto(name="legacy_statement_result.proto", syntax="proto2")
        fields = descriptor_pb2.FieldDescriptorProto
        result = file.message_type.add(name="StatementResult")
        result.field.add(name="scalar", number=1, type=fields.TYPE_INT64)
        result.field.add(name="frame", number=2, type=fields.TYPE_BYTES)
        pool = descriptor_pool.DescriptorPool()
        pool.Add(file)
        return message_factory.GetMessageClass(pool.FindMessageTypeByName("StatementResult"))
