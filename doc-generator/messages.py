import os

from google.protobuf.descriptor_pb2 import FieldDescriptorProto

import label_names as label_names
import type_names as type_names
import utils as utils
import generator as gen
import proto_utils as putils


def get_messages_from_file_descriptor(file_descriptor, repo_path, tree_ish):
    content = []
    if not hasattr(file_descriptor, 'source_code_info'):
        print('ERROR: No source code info!')
        return content
    short_directory = putils.PROTO_DIRECTORY.replace("../", "", 1)
    file_link = utils.generate_link(repo_path, tree_ish, file_descriptor.name, short_directory)
    content.append(gen.generate_title(file_descriptor.name, file_link))

    for message_index, message in enumerate(file_descriptor.message_type):
        message_path = [4, message_index]
        message_description = putils.get_description_for_location(file_descriptor.source_code_info, message_path)
        line = putils.get_line_number_for_location(file_descriptor.source_code_info, message_path)
        file_link = utils.generate_link(repo_path, tree_ish, file_descriptor.name, short_directory, line)
        content.append(gen.generate_subtitle(message.name, message_description, file_link))
        if message.field:
            content.append('\n')
        for field_index, field in enumerate(message.field):
            field_path = [4, message_index, 2, field_index]
            field_description = putils.get_description_for_location(file_descriptor.source_code_info, field_path)
            if field.type in (FieldDescriptorProto.TYPE_MESSAGE, FieldDescriptorProto.TYPE_ENUM):
                field_type_name = field.type_name.split('.')[-1]
            else:
                field_type_name = type_names.get_display_name(field.type)
            label = label_names.get_display_name(field.label)
            content.append(gen.generate_field_entry(field_type_name, field.name, field_description, label))
    return content


def messages(repo_path, branch_name):
    content = []
    files = putils.get_proto_file_names(putils.PROTO_DIRECTORY)
    for file in files:
        file_path = os.path.join(putils.PROTO_DIRECTORY, file)
        putils.compile_file(file_path)
        descriptor_set = putils.load_descriptor_set()
        for descriptor in descriptor_set.file:
            content.extend(get_messages_from_file_descriptor(descriptor, repo_path, branch_name))
    putils.remove_descriptor_set()
    return ''.join(content)
