import os


def get_proto_file_names(directory):
    return [file for file in os.listdir(directory) if file.endswith(".proto")]
