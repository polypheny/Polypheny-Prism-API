import os
import re
import config
import utils as utils
import proto_utils as putils
import generator as gen

REQUESTS_SUFFIX = config.REQUEST_FILE_SUFFIX + '.proto'
RESPONSES_SUFFIX = config.RESPONSE_FILE_SUFFIX + '.proto'


def proto_files(repo_path, branch_name, directory=config.PROTO_DIR):
    file_names = putils.get_proto_file_names(directory)
    return _generate_file_section(directory, file_names, repo_path, branch_name)


def _generate_file_section(directory, file_names, repo_path, tree_ish):
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
                description = _get_file_description(directory, file)
                file_link = utils.generate_link(repo_path, tree_ish, file, short_directory)
                responses_file_link = utils.generate_link(repo_path, tree_ish, responses_file, short_directory)
                content.append(gen.generate_paired_file_entry(category, file, responses_file, description, file_link, responses_file_link))
                processed.append(file)
                processed.append(responses_file)
            else:
                processed.append(file)
                raise FileExistsError(f"No matching responses file found for {file}.")
        elif not file.endswith(REQUESTS_SUFFIX) and not file.endswith(RESPONSES_SUFFIX):
            category = file.replace('.proto', '')
            description = _get_file_description(directory, file)
            file_link = utils.generate_link(repo_path, tree_ish, file, short_directory)
            content.append(gen.generate_single_file_entry(category, file, description, file_link))
            processed.append(file)
    return ''.join(content)


def _get_file_description(directory, file_name):
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
    with open(config.README_FILE, 'r') as file:
        next(file)
        lines = file.readlines()
    return ''.join(lines)



