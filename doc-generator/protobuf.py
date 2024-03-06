import os
import subprocess

from google.protobuf import descriptor_pb2
from google.protobuf.descriptor_pb2 import FieldDescriptorProto

import type_names
import label_names
import utils

DESCRIPTOR_SET_OUT = 'descriptor_set.bin'
PROTO_DIRECTORY = '../proto'


def compile_file(proto_file, proto_path=PROTO_DIRECTORY, descriptor_set_out=DESCRIPTOR_SET_OUT):
    try:
        command = [
            'protoc',
            f'--proto_path={proto_path}',
            f'--descriptor_set_out={descriptor_set_out}',
            '--include_source_info',
            proto_file
        ]
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f'Error compiling {proto_file}: {e}')
        return False


def get_messages_from_file_descriptor(file_descriptor):
    content = []
    if not hasattr(file_descriptor, 'source_code_info'):
        print('ERROR: No source code info!')
        return content

    content.append(generate_title(file_descriptor.name))

    for message_index, message in enumerate(file_descriptor.message_type):
        message_path = [4, message_index]
        message_description = get_description_for_location(file_descriptor.source_code_info, message_path)
        content.append(generate_subtitle(message.name, message_description))
        if message.field:
            content.append('\n')
        for field_index, field in enumerate(message.field):
            field_path = [4, message_index, 2, field_index]
            field_description = get_description_for_location(file_descriptor.source_code_info, field_path)
            if field.type in (FieldDescriptorProto.TYPE_MESSAGE, FieldDescriptorProto.TYPE_ENUM):
                field_type_name = field.type_name.split('.')[-1]
            else:
                field_type_name = type_names.get_display_name(field.type)
            label = label_names.get_display_name(field.label)
            content.append(generate_field_entry(field_type_name, field.name, field_description, label))
    return content


def get_enums_from_file_descriptor(file_descriptor):
    content = []
    if not hasattr(file_descriptor, 'source_code_info'):
        print('ERROR: No source code info!')
        return content
    for enum_index, enum in enumerate(file_descriptor.enum_type):
        enum_path = [5, enum_index]
        enum_description = get_description_for_location(file_descriptor.source_code_info, enum_path)
        content.append(generate_subtitle(enum.name, enum_description))
        if enum.value:
            content.append('\n')
        for value_index, value in enumerate(enum.value):
            value_path = [5, enum_index, 2, value_index]
            value_description = get_description_for_location(file_descriptor.source_code_info, value_path)
            content.append(generate_value_entry(value.name, value.number, value_description))
    for message_index, message in enumerate(file_descriptor.message_type):
        for enum_index, enum in enumerate(message.enum_type):
            enum_path = [4, message_index, 4, enum_index]
            enum_description = get_description_for_location(file_descriptor.source_code_info, enum_path)
            content.append(generate_subtitle(enum.name, enum_description))
            if enum.value:
                content.append('\n')
            for value_index, value in enumerate(enum.value):
                value_path = [4, message_index, 4, enum_index, 2, value_index]
                value_description = get_description_for_location(file_descriptor.source_code_info, value_path)
                content.append(generate_value_entry(value.name, value.number, value_description))
    if content:
        content.insert(0, generate_title(file_descriptor.name))
    return content


def get_description_for_location(source_code_info, path):
    for location in source_code_info.location:
        if list(location.path) == path:
            comments = [location.leading_comments] + list(location.leading_detached_comments)
            return ' '.join(comment.strip() for comment in comments if comment.strip()).strip()
    return ''


def load_descriptor_set(descriptor_set_file=DESCRIPTOR_SET_OUT):
    with open(descriptor_set_file, 'rb') as f:
        data = f.read()
    file_descriptor_set = descriptor_pb2.FileDescriptorSet()
    file_descriptor_set.ParseFromString(data)
    return file_descriptor_set


def remove_descriptor_set(descriptor_set_file=DESCRIPTOR_SET_OUT):
    if not os.path.exists(descriptor_set_file):
        return
    os.remove(descriptor_set_file)


def messages():
    content = []
    files = utils.get_proto_file_names(PROTO_DIRECTORY)
    for file in files:
        file_path = os.path.join(PROTO_DIRECTORY, file)
        compile_file(file_path)
        descriptor_set = load_descriptor_set()
        for descriptor in descriptor_set.file:
            content.extend(get_messages_from_file_descriptor(descriptor))
    remove_descriptor_set()
    return ''.join(content)


def enums():
    content = []
    files = utils.get_proto_file_names(PROTO_DIRECTORY)
    for file in files:
        file_path = os.path.join(PROTO_DIRECTORY, file)
        compile_file(file_path)
        descriptor_set = load_descriptor_set()
        for descriptor in descriptor_set.file:
            content.extend(get_enums_from_file_descriptor(descriptor))
    remove_descriptor_set()
    return ''.join(content)


def generate_title(name):
    content = f'\n### {name}\n'
    return content


def generate_field_entry(type, name, description=None, label=None):
    content = f'- '
    if label:
        content += f'`{label}` '
    content += f'`{type}` **{name}'
    if description:
        content += f':** {description}\n'
    else:
        content += '**\n'
    return content


def generate_subtitle(name, description=None):
    content = f'\n**{name}**\n'
    if description:
        content += f'\n{description}\n'
    return content


def generate_value_entry(name, value, description=None):
    content = f'- `{name}` = {value}'
    if description:
        content += f': {description}\n'
    else:
        content += '\n'
    return content
