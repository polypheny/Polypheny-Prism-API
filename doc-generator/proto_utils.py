import os
import subprocess

from google.protobuf import descriptor_pb2

DESCRIPTOR_SET_OUT = 'descriptor_set.bin'
PROTO_DIRECTORY = '../proto'


def get_proto_file_names(directory):
    return [file for file in os.listdir(directory) if file.endswith(".proto")]


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


def remove_descriptor_set(descriptor_set_file=DESCRIPTOR_SET_OUT):
    if not os.path.exists(descriptor_set_file):
        return
    os.remove(descriptor_set_file)


def load_descriptor_set(descriptor_set_file=DESCRIPTOR_SET_OUT):
    with open(descriptor_set_file, 'rb') as f:
        data = f.read()
    file_descriptor_set = descriptor_pb2.FileDescriptorSet()
    file_descriptor_set.ParseFromString(data)
    return file_descriptor_set


def get_description_for_location(source_code_info, path):
    for location in source_code_info.location:
        if list(location.path) == path:
            comments = [location.leading_comments] + list(location.leading_detached_comments)
            return ' '.join(comment.strip() for comment in comments if comment.strip()).strip()
    return ''


def get_source_from_span(span, file_path):
    start_line, start_column, length_in_chars = span
    length_in_chars -= 2
    end_position = start_column + length_in_chars
    current_char_count = 0
    with open(file_path, 'r') as proto_file:
        lines = proto_file.readlines()

    segment = ''
    for i, line in enumerate(lines, start=0):
        if i < start_line:
            continue
        if i == start_line + 1:
            line = line[start_column:start_column+length_in_chars]
        if current_char_count + len(line) >= end_position:
            segment += line[:end_position - current_char_count]
            break
        else:
            segment += line
            current_char_count += len(line)
    return segment.strip()


def get_field_type(source_code_info, location_path, file_path):
    location_path.append(4)
    for location in source_code_info.location:
        if list(location.path) == location_path:
            return get_source_from_span(location.span, file_path)
    return ''


def get_line_number_for_location(source_code_info, path):
    for location in source_code_info.location:
        if list(location.path) == path:
            return location.span[0]
    return None
