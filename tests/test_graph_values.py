"""Verify that Prism can carry graph values alongside scalars in a row."""

import importlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from google.protobuf import descriptor_pb2, descriptor_pool, message_factory


class GraphValueContractTest(unittest.TestCase):
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
        cls.value = importlib.import_module("org.polypheny.prism.value_pb2")
        cls.frames = importlib.import_module("org.polypheny.prism.relational_frame_pb2")

    def test_graph_cells_preserve_rows_and_path_traversal(self):
        value = self.value
        a = value.ProtoNode(id="a", labels=["Person"])
        a.properties["name"].string.string = "Alice"
        b = value.ProtoNode(id="b", labels=["Person"])
        isolated = value.ProtoNode(id="c")
        edge = value.ProtoEdge(id="e", left="a", right="b", direction=value.ProtoEdge.LEFT_TO_RIGHT)
        edge.properties["since"].integer.integer = 2024
        second_edge = value.ProtoEdge(id="f", left="a", right="b", direction=value.ProtoEdge.LEFT_TO_RIGHT)

        frame = self.frames.RelationalFrame()
        column_types = [value.INTEGER, value.NODE, value.EDGE, value.PATH, value.GRAPH]
        for index, column_type in enumerate(column_types):
            frame.column_meta.add(column_index=index).type_meta.proto_value_type = column_type
        row = frame.rows.add()
        row.values.add().integer.integer = 42
        row.values.add().node.CopyFrom(a)
        row.values.add().edge.CopyFrom(edge)
        row.values.add().path.CopyFrom(value.ProtoPath(nodes=[b, a, b], edges=[edge, second_edge]))
        row.values.add().graph.CopyFrom(value.ProtoGraph(nodes=[a, b, isolated], edges=[edge, second_edge]))
        row = frame.rows.add()
        row.values.add().integer.integer = 43
        for _ in column_types[1:]:
            row.values.add().null.SetInParent()

        decoded = self.frames.RelationalFrame.FromString(frame.SerializeToString())
        self.assertEqual(decoded, frame)
        self.assertEqual([column.type_meta.proto_value_type for column in decoded.column_meta], column_types)
        first, second = decoded.rows
        self.assertEqual([item.WhichOneof("value") for item in first.values],
                         ["integer", "node", "edge", "path", "graph"])
        self.assertEqual([node.id for node in first.values[3].path.nodes], ["b", "a", "b"])
        self.assertEqual([item.id for item in first.values[3].path.edges], ["e", "f"])
        first_edge = first.values[3].path.edges[0]
        self.assertEqual((first_edge.left, first_edge.right, first_edge.direction),
                         ("a", "b", value.ProtoEdge.LEFT_TO_RIGHT))
        self.assertEqual({node.id for node in first.values[4].graph.nodes}, {"a", "b", "c"})
        self.assertEqual([item.WhichOneof("value") for item in second.values],
                         ["integer", "null", "null", "null", "null"])

    def test_legacy_value_readers_keep_existing_fields_and_preserve_new_unknown_fields(self):
        graph_cases = {"node": 20, "edge": 21, "path": 22, "graph": 23}
        descriptor = descriptor_pb2.FileDescriptorProto.FromString(self.value.DESCRIPTOR.serialized_pb)
        value_descriptor = next(message for message in descriptor.message_type if message.name == "ProtoValue")
        removed = {}
        for index in reversed(range(len(value_descriptor.field))):
            field = value_descriptor.field[index]
            if field.name in graph_cases:
                removed[field.name] = field.number
                del value_descriptor.field[index]
        self.assertEqual(removed, graph_cases)
        for index in reversed(range(len(descriptor.message_type))):
            if descriptor.message_type[index].name in {"ProtoPath", "ProtoGraph"}:
                del descriptor.message_type[index]
        pool = descriptor_pool.DescriptorPool()
        pool.Add(descriptor)
        legacy_value = message_factory.GetMessageClass(pool.FindMessageTypeByName("org.polypheny.prism.ProtoValue"))

        scalar = self.value.ProtoValue()
        scalar.integer.integer = 42
        self.assertEqual(legacy_value.FromString(scalar.SerializeToString()).integer.integer, 42)
        for graph_case in graph_cases:
            with self.subTest(case=graph_case):
                extended = self.value.ProtoValue()
                getattr(extended, graph_case).SetInParent()
                old = legacy_value.FromString(extended.SerializeToString())
                self.assertIsNone(old.WhichOneof("value"))
                self.assertEqual(self.value.ProtoValue.FromString(old.SerializeToString()), extended)
