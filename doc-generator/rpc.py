from google.protobuf import descriptor_pb2

import generator as gen
import proto_utils as putils
import utils as utils
import os
import config

RPC_DEFINITION_FILE = os.path.join(config.PROTO_DIR, config.RPC_DEFINITION_FILE)


def get_rpcs_from_sets(descriptor, matches, single_responses, single_requests, repo_path, tree_ish, request_path,
                       response_path):
    content = []
    short_directory = config.PROTO_DIR.replace("../", "", 1)
    for rpc in matches:
        request, response = rpc
        title = request[1].name.replace(config.REQUESTS_MESSAGE_NAME, '')
        message_path = [4, request_path, 2, request[0]]
        description = putils.get_description_for_location(descriptor.source_code_info, message_path)
        content.append(gen.generate_subtitle(title, description))

        request_type = request[1].type_name.split('.')[-1]
        line = putils.get_line_number_for_location(descriptor.source_code_info, message_path)
        request_link = utils.generate_link(repo_path, tree_ish, os.path.basename(RPC_DEFINITION_FILE), short_directory,
                                           line)
        content.append(gen.generate_rpc_message(request_type, request[1].name, True, request_link))

        response_type = response[1].type_name.split('.')[-1]
        message_path = [4, response_path, 2, response[0]]
        line = putils.get_line_number_for_location(descriptor.source_code_info, message_path)
        response_link = utils.generate_link(repo_path, tree_ish, os.path.basename(RPC_DEFINITION_FILE), short_directory,
                                            line)
        content.append(gen.generate_rpc_message(response_type, response[1].name, False, response_link))

    for single_request in single_requests:
        title = single_request[1].name.replace(config.REQUESTS_MESSAGE_NAME, '')
        message_path = [4, request_path, 2, single_request[0]]
        description = putils.get_line_number_for_location(descriptor.source_code_info, message_path[0])
        content.append(gen.generate_subtitle(title, description))

        request_type = single_request[1].type_name.split('.')[-1]
        line = putils.get_line_number_for_location(descriptor.source_code_info, message_path)
        request_link = utils.generate_link(repo_path, tree_ish, os.path.basename(RPC_DEFINITION_FILE), short_directory,
                                           line)
        content.append(gen.generate_rpc_message(request_type, single_request[1].name, False, request_link))

    for single_response in single_responses:
        title = single_response[1].name.replace(config.REQUESTS_MESSAGE_NAME, '')
        message_path = [4, request_path, 2, single_response[0]]
        description = putils.get_line_number_for_location(descriptor.source_code_info, message_path[0])
        content.append(gen.generate_subtitle(title, description))

        request_type = single_response[1].type_name.split('.')[-1]
        line = putils.get_line_number_for_location(descriptor.source_code_info, message_path)
        request_link = utils.generate_link(repo_path, tree_ish, os.path.basename(RPC_DEFINITION_FILE), short_directory,
                                           line)
        content.append(gen.generate_rpc_message(request_type, single_response[1].name, True, request_link))

    return content


def rpc(repo_path, tree_ish):
    content = []
    putils.compile_file(RPC_DEFINITION_FILE)
    descriptor_set = putils.load_descriptor_set()
    for descriptor in descriptor_set.file:
        check_required_fields(descriptor)
        matches, single_responses, single_requests = _get_rpc_sets_from_file_descriptor(descriptor)
        requests_path, _ = _get_message_descriptor(descriptor, config.REQUESTS_MESSAGE_NAME)
        responses_path, _ = _get_message_descriptor(descriptor, config.RESPONSES_MESSAGE_NAME)
        content.extend(get_rpcs_from_sets(descriptor, matches, single_responses, single_requests, repo_path, tree_ish,
                                          requests_path, responses_path))
    return ''.join(content)


def _get_message_field_descriptors(file_descriptor, message_name):
    message_descriptors = []
    _, message_descriptor = _get_message_descriptor(file_descriptor, message_name)
    if not message_descriptor:
        raise Exception(f'No message with name "{message_name}" found.')
    for field_id, field in enumerate(message_descriptor.field):
        if not field.type == descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE:
            continue
        message_descriptors.append((field_id, field))
    return message_descriptors


def _get_message_descriptor(file_descriptor, message_name):
    for message_index, message in enumerate(file_descriptor.message_type):
        if message.name == message_name:
            return message_index, message
    return None


def _is_request_present(file_descriptor):
    return _get_message_descriptor(file_descriptor, config.REQUESTS_MESSAGE_NAME) is not None


def _is_response_resent(file_descriptor):
    return _get_message_descriptor(file_descriptor, config.RESPONSES_MESSAGE_NAME) is not None


def _get_rpc_sets_from_file_descriptor(file_descriptor):
    if not _is_request_present(file_descriptor):
        raise Exception('Request message not present.')
    if not _is_response_resent(file_descriptor):
        raise Exception('Response message not present.')
    request_messages = _get_message_field_descriptors(file_descriptor, config.REQUESTS_MESSAGE_NAME)
    response_messages = _get_message_field_descriptors(file_descriptor, config.RESPONSES_MESSAGE_NAME)
    matches, leftover_requests, leftover_responses = _get_matches(request_messages, response_messages)
    for left_request in leftover_requests:
        if left_request[1].name.endswith(config.REQUESTS_MESSAGE_NAME):
            raise Exception(f'No matching response for {left_request.name}')
    for left_response in leftover_responses:
        if left_response[1].name.endswith(config.RESPONSES_MESSAGE_NAME):
            raise Exception(f'No matching request for {left_response.name}')
    return matches, leftover_requests, leftover_responses


def _get_matches(requests, responses):
    matches = []
    leftover_requests = []
    leftover_responses = responses.copy()
    for request in requests:
        match = None
        for response in responses:
            request_name = request[1].name.replace(config.REQUEST_FILE_SUFFIX, '')
            response_name = response[1].name.replace(config.RESPONSE_FILE_SUFFIX, '')
            if request_name == response_name:
                match = (request, response)
        if match is not None:
            matches.append(match)
            leftover_responses.remove(match[1])
        else:
            leftover_requests.append(request)
    return matches, leftover_requests, leftover_responses


def check_required_fields(file_descriptor):
    _, request_descriptor = _get_message_descriptor(file_descriptor, config.REQUESTS_MESSAGE_NAME)
    request_fields = {field.name: field.number for field in request_descriptor.field}
    _check_for_missing_fields(request_fields, config.REQUIRED_REQUEST_FIELDS)

    _, response_descriptor = _get_message_descriptor(file_descriptor, config.RESPONSES_MESSAGE_NAME)
    response_fields = {field.name: field.number for field in response_descriptor.field}
    _check_for_missing_fields(response_fields, config.REQUIRED_RESPONSE_FIELDS)


def _check_for_missing_fields(existing_fields, required_fields):
    for required_field_name, required_field_number in required_fields:
        if required_field_name not in existing_fields:
            raise Exception(f'Required field "{required_field_name}" not present in response message.')
        if existing_fields[required_field_name] != required_field_number:
            raise Exception(f'Required field "{required_field_name}" in response message has incorrect number. Expected {required_field_number}, got {existing_fields[required_field_name]}.')