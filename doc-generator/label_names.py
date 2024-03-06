from google.protobuf.descriptor_pb2 import FieldDescriptorProto

LABEL_TO_STRING = {
    FieldDescriptorProto.LABEL_OPTIONAL: "optional",
    FieldDescriptorProto.LABEL_REQUIRED: "required",
    FieldDescriptorProto.LABEL_REPEATED: "repeated"
}


def get_display_name(field_label):
    return LABEL_TO_STRING.get(field_label, 'unknown')
