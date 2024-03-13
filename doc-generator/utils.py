import os


def get_proto_file_names(directory):
    return [file for file in os.listdir(directory) if file.endswith(".proto")]


def generate_link(repo_path, tree_ish, file_name, directory_path=None, line=None):
    base_url = "https://github.com"
    path = f"{base_url}/{repo_path}/blob/{tree_ish}/"
    if directory_path:
        path += f"{directory_path}/"
    path += f"{file_name}"
    if line:
        path += f"#L{line}"
    return path
