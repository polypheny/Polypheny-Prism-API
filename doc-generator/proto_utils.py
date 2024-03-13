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


def get_line_number_for_location(source_code_info, path):
    for location in source_code_info.location:
        if list(location.path) == path:
            return location.span[0]
    return None
