"""Contract tests generated from the actual Prism protocol definitions.

Run with: python -m unittest discover -s tests -v
"""

import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from google.protobuf import descriptor_pb2, descriptor_pool, message_factory


class DocumentMetadataContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.generated.cleanup)
        root = Path(__file__).resolve().parents[1]
        proto_files = sorted(root.glob("org/polypheny/prism/*.proto"))
        subprocess.run(
            [sys.executable, "-m", "grpc_tools.protoc", f"-I{root}",
             f"--python_out={cls.generated.name}"]
            + [str(path) for path in proto_files],
            check=True,
        )
        sys.path.insert(0, cls.generated.name)
        cls.addClassCleanup(sys.path.remove, cls.generated.name)
        cls.meta = importlib.import_module(
            "org.polypheny.prism.namespace_meta_responses_pb2"
        )

    def test_field_numbers_types_and_cardinality(self):
        field = descriptor_pb2.FieldDescriptorProto
        expected = {
            "Document": [
                ("namespace_name", 1, field.TYPE_STRING, False),
                ("collection_name", 2, field.TYPE_STRING, False),
                ("fields", 3, field.TYPE_MESSAGE, True),
                ("sample_document_json", 4, field.TYPE_STRING, False),
                ("document_indexes", 5, field.TYPE_MESSAGE, True),
            ],
            "DocumentField": [
                ("field_path", 1, field.TYPE_STRING, False),
                ("type_name", 2, field.TYPE_STRING, False),
                ("is_optional", 3, field.TYPE_BOOL, False),
            ],
            "DocumentIndex": [
                ("field_path", 1, field.TYPE_STRING, False),
                ("index_type", 2, field.TYPE_STRING, False),
                ("unique", 3, field.TYPE_BOOL, False),
            ],
        }
        for name, fields in expected.items():
            with self.subTest(message=name):
                actual = getattr(self.meta, name).DESCRIPTOR.fields
                self.assertEqual(
                    [(item.name, item.number, item.type,
                      item.label == field.LABEL_REPEATED) for item in actual],
                    fields,
                )
        self.assertEqual(
            self.meta.Document.DESCRIPTOR.fields_by_name["fields"].message_type.full_name,
            "org.polypheny.prism.DocumentField",
        )
        self.assertEqual(
            self.meta.Document.DESCRIPTOR.fields_by_name["document_indexes"].message_type.full_name,
            "org.polypheny.prism.DocumentIndex",
        )

    def test_all_metadata_survives_entities_response_round_trip(self):
        sample = {"patient_id": "p1", "complications": {"renal": None}}
        response = self.meta.EntitiesResponse()
        document = response.entities.add().document
        document.namespace_name = "patients_symptoms"
        document.collection_name = "symptoms"
        document.fields.add(field_path="patient_id", type_name="string", is_optional=False)
        document.fields.add(field_path="complications", type_name="object", is_optional=True)
        document.fields.add(field_path="complications.renal", type_name="null", is_optional=True)
        document.sample_document_json = json.dumps(sample)
        document.document_indexes.add(field_path="patient_id", index_type="hash", unique=True)
        document.document_indexes.add(field_path="complications.renal", index_type="btree", unique=False)

        result = self.meta.EntitiesResponse.FromString(response.SerializeToString())
        self.assertEqual(result, response)
        self.assertEqual(result.entities[0].WhichOneof("Entity"), "document")
        actual = result.entities[0].document
        self.assertEqual(actual.namespace_name, "patients_symptoms")
        self.assertEqual(actual.collection_name, "symptoms")
        self.assertEqual(
            [(item.field_path, item.type_name, item.is_optional) for item in actual.fields],
            [("patient_id", "string", False), ("complications", "object", True),
             ("complications.renal", "null", True)],
        )
        self.assertTrue(actual.HasField("sample_document_json"))
        self.assertEqual(json.loads(actual.sample_document_json), sample)
        self.assertEqual(
            [(item.field_path, item.index_type, item.unique) for item in actual.document_indexes],
            [("patient_id", "hash", True), ("complications.renal", "btree", False)],
        )

    def test_sample_presence_and_empty_collection(self):
        document = self.meta.Document(namespace_name="ns", collection_name="empty")
        self.assertFalse(document.HasField("sample_document_json"))
        self.assertEqual(list(document.fields), [])
        self.assertEqual(list(document.document_indexes), [])
        copy = self.meta.Document.FromString(document.SerializeToString())
        self.assertFalse(copy.HasField("sample_document_json"))
        document.sample_document_json = ""
        copy = self.meta.Document.FromString(document.SerializeToString())
        self.assertTrue(copy.HasField("sample_document_json"))
        document.ClearField("sample_document_json")
        self.assertFalse(document.HasField("sample_document_json"))

    def test_document_uses_existing_entity_oneof(self):
        entity = self.meta.Entity()
        entity.document.collection_name = "symptoms"
        self.assertTrue(entity.HasField("document"))
        self.assertFalse(entity.HasField("table"))
        self.assertFalse(entity.HasField("graph"))
        self.assertEqual(entity.DESCRIPTOR.fields_by_name["document"].number, 3)
        entity.table.table_name = "patients"
        self.assertFalse(entity.HasField("document"))
        self.assertEqual(entity.WhichOneof("Entity"), "table")

    def test_old_empty_document_readers_preserve_unknown_metadata(self):
        # Model the previous empty Document definition in an isolated descriptor pool.
        legacy = descriptor_pb2.FileDescriptorProto(
            name="legacy_document.proto", package="org.polypheny.prism", syntax="proto3"
        )
        legacy.message_type.add(name="Document")
        pool = descriptor_pool.DescriptorPool()
        pool.Add(legacy)
        legacy_document = message_factory.GetMessageClass(
            pool.FindMessageTypeByName("org.polypheny.prism.Document")
        )
        document = self.meta.Document(
            namespace_name="ns", collection_name="symptoms", sample_document_json="{}"
        )
        document.fields.add(field_path="_id", type_name="string", is_optional=False)
        document.document_indexes.add(field_path="_id", index_type="hash", unique=True)
        old_reader = legacy_document.FromString(document.SerializeToString())
        self.assertEqual(
            self.meta.Document.FromString(old_reader.SerializeToString()), document
        )


if __name__ == "__main__":
    unittest.main()
