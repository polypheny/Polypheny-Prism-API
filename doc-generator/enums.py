import os
import generator as gen
import utils as utils
import proto_utils as putils

def get_enums_from_file_descriptor(file_descriptor, repo_path, tree_ish):
    content = []
    if not hasattr(file_descriptor, 'source_code_info'):
        print('ERROR: No source code info!')
        return content
    short_directory = putils.PROTO_DIRECTORY.replace("../", "", 1)
    for enum_index, enum in enumerate(file_descriptor.enum_type):
        enum_path = [5, enum_index]
        line = putils.get_line_number_for_location(file_descriptor.source_code_info, enum_path)
        file_link = utils.generate_link(repo_path, tree_ish, file_descriptor.name, short_directory, line)
        enum_description = putils.get_description_for_location(file_descriptor.source_code_info, enum_path)
        content.append(gen.generate_subtitle(enum.name, enum_description, file_link))
        if enum.value:
            content.append('\n')
        for value_index, value in enumerate(enum.value):
            value_path = [5, enum_index, 2, value_index]
            value_description = putils.get_description_for_location(file_descriptor.source_code_info, value_path)
            content.append(gen.generate_value_entry(value.name, value.number, value_description))
    for message_index, message in enumerate(file_descriptor.message_type):
        for enum_index, enum in enumerate(message.enum_type):
            enum_path = [4, message_index, 4, enum_index]
            line = putils.get_line_number_for_location(file_descriptor.source_code_info, enum_path)
            file_link = utils.generate_link(repo_path, tree_ish, file_descriptor.name, short_directory, line)
            enum_description = putils.get_description_for_location(file_descriptor.source_code_info, enum_path)
            content.append(gen.generate_subtitle(enum.name, enum_description, file_link))
            if enum.value:
                content.append('\n')
            for value_index, value in enumerate(enum.value):
                value_path = [4, message_index, 4, enum_index, 2, value_index]
                value_description = putils.get_description_for_location(file_descriptor.source_code_info, value_path)
                content.append(gen.generate_value_entry(value.name, value.number, value_description))
    if content:
        content.insert(0, gen.generate_title(file_descriptor.name))
    return content


def enums(repo_path, tree_ish):
    content = []
    files = putils.get_proto_file_names(putils.PROTO_DIRECTORY)
    for file in files:
        file_path = os.path.join(putils.PROTO_DIRECTORY, file)
        putils.compile_file(file_path)
        descriptor_set = putils.load_descriptor_set()
        for descriptor in descriptor_set.file:
            content.extend(get_enums_from_file_descriptor(descriptor, repo_path, tree_ish))
    putils.remove_descriptor_set()
    return ''.join(content)
