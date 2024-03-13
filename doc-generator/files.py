import os
import re

import utils

PROTO_DIRECTORY = '../proto'
README_PATH = '../README.md'
REQUESTS_SUFFIX = '_requests.proto'
RESPONSES_SUFFIX = '_responses.proto'


def proto_files(repo_path, branch_name, directory=PROTO_DIRECTORY):
    file_names = utils.get_proto_file_names(directory)
    return generate_file_section(directory, file_names, repo_path, branch_name)


def generate_file_section(directory, file_names, repo_path, tree_ish):
    processed = []
    content = []
    short_directory = directory.replace("../", "", 1)
    for file in file_names:
        if file in processed:
            continue
        if file.endswith(REQUESTS_SUFFIX):
            responses_file = file.replace(REQUESTS_SUFFIX, RESPONSES_SUFFIX)
            if responses_file in file_names:
                category = file.replace(REQUESTS_SUFFIX, '')
                description = get_file_description(directory, file)
                file_link = utils.generate_link(repo_path, tree_ish, short_directory, file)
                responses_file_link = utils.generate_link(repo_path, tree_ish, short_directory, responses_file)
                content.append(generate_paired_file_entry(category, file, responses_file, description, file_link, responses_file_link))
                processed.append(file)
                processed.append(responses_file)
            else:
                processed.append(file)
                raise FileExistsError(f"No matching responses file found for {file}.")
        elif not file.endswith(REQUESTS_SUFFIX) and not file.endswith(RESPONSES_SUFFIX):
            category = file.replace('.proto', '')
            description = get_file_description(directory, file)
            file_link = utils.generate_link(repo_path, tree_ish, short_directory, file)
            content.append(generate_single_file_entry(category, file, description, file_link))
            processed.append(file)
    return ''.join(content)


def get_file_description(directory, file_name):
    path = os.path.join(directory, file_name)
    try:
        with open(path, 'r') as file:
            in_description_section = False
            description_lines = []
            for line in file:
                if re.match(r'/\*', line):
                    in_description_section = True
                if in_description_section:
                    description_lines.append(line)
                if in_description_section and re.match(r'.*\*/', line):
                    break
            description_text = ''.join(description_lines).strip()
            return description_text[3:-3]
    except FileNotFoundError:
        return 'NOT FOUND'


def readme():
    lines = []
    with open(README_PATH, 'r') as file:
        next(file)
        lines = file.readlines()
    return ''.join(lines)


def generate_paired_file_entry(category, request_file, response_file, description, request_link=None,
                               response_link=None):
    entry = f'### {category}\n'
    if description:
        entry += f'{description}\n\n'

    if request_link:
        entry += f'- **Request Proto File**: [`{request_file}`]({request_link})\n'
    else:
        entry += f'- **Request Proto File**: `{request_file}`\n'
    if response_link:
        entry += f'- **Response Proto File**: [`{response_file}`]({response_link})\n\n'
    else:
        entry += f'- **Response Proto File**: `{response_file}`\n\n'
    return entry


def generate_single_file_entry(category, file, description, file_link=None):
    entry = f'### {category}\n'
    if description:
        entry += f'{description}\n\n'
    if file_link:
        entry += f'- **Proto File**: [`{file}`]({file_link})\n\n'
    else:
        entry += f'- **Proto File**: `{file}`\n\n'
    return entry
