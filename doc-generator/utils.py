import os


def get_proto_file_names(directory):
    return [file for file in os.listdir(directory) if file.endswith(".proto")]


def generate_link(repo_path, branch_name, file_name, directory_path=None, line=None):
    path = f'{repo_path}/blob/{branch_name}/'
    if directory_path:
        path += f'{directory_path}/'
    path += f'{file_name}'
    if line:
        path += f'#L{line}'
    return path
