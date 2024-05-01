from google.protobuf import descriptor_pb2

import generator as gen
import proto_utils as putils
import utils as utils

RPC_DEFINITION_FILE_PATH = '../proto/polyprism/protointerface.proto'
RPC_DEFINITION_FILE_NAME = 'protointerface.proto'

REQUESTS_MESSAGE_NAME = 'Request'
RESPONSES_MESSAGE_NAME = 'Response'
RESPONSE_MESSAGE_SUFFIX = '_response'
REQUEST_MESSAGE_SUFFIX = '_request'

REQUIRED_RESPONSE_FIELDS = [
    'id',
    'last',
    'error_response',
    'dbms_version_response',
    'connection_response',
    'disconnect_response'
]

REQUIRED_REQUEST_FIELDS = [
    'id',
    'dbms_version_request',
    'connection_request',
    'disconnect_request'
]


def get_rpcs_from_sets(descriptor, matches, single_responses, single_requests, repo_path, tree_ish, request_path,
                       response_path):
    content = []
    short_directory = putils.PROTO_DIRECTORY.replace("../", "", 1) + "polyprism"
    for rpc in matches:
        request, response = rpc
        title = request[1].name.replace(REQUESTS_MESSAGE_NAME, '')
        message_path = [4, request_path, 2, request[0]]
        description = putils.get_description_for_location(descriptor.source_code_info, message_path)
        content.append(gen.generate_subtitle(title, description))

        request_type = request[1].type_name.split('.')[-1]
        line = putils.get_line_number_for_location(descriptor.source_code_info, message_path)
        request_link = utils.generate_link(repo_path, tree_ish, RPC_DEFINITION_FILE_NAME, short_directory, line)
        content.append(gen.generate_rpc_message(request_type, request[1].name, True, request_link))

        response_type = response[1].type_name.split('.')[-1]
        message_path = [4, response_path, 2, response[0]]
        line = putils.get_line_number_for_location(descriptor.source_code_info, message_path)
        response_link = utils.generate_link(repo_path, tree_ish, RPC_DEFINITION_FILE_NAME, short_directory, line)
        content.append(gen.generate_rpc_message(response_type, response[1].name, False, response_link))

    for single_request in single_requests:
        title = single_request[1].name.replace(REQUESTS_MESSAGE_NAME, '')
        message_path = [4, request_path, 2, single_request[0]]
        description = putils.get_line_number_for_location(descriptor.source_code_info, message_path[0])
        content.append(gen.generate_subtitle(title, description))

        request_type = single_request[1].type_name.split('.')[-1]
        line = putils.get_line_number_for_location(descriptor.source_code_info, message_path)
        request_link = utils.generate_link(repo_path, tree_ish, RPC_DEFINITION_FILE_NAME, short_directory, line)
        content.append(gen.generate_rpc_message(request_type, single_request[1].name, False, request_link))

    for single_response in single_responses:
        title = single_response[1].name.replace(REQUESTS_MESSAGE_NAME, '')
        message_path = [4, request_path, 2, single_response[0]]
        description = putils.get_line_number_for_location(descriptor.source_code_info, message_path[0])
        content.append(gen.generate_subtitle(title, description))

        request_type = single_response[1].type_name.split('.')[-1]
        line = putils.get_line_number_for_location(descriptor.source_code_info, message_path)
        request_link = utils.generate_link(repo_path, tree_ish, RPC_DEFINITION_FILE_NAME, short_directory, line)
        content.append(gen.generate_rpc_message(request_type, single_response[1].name, True, request_link))

    return content


def rpc(repo_path, tree_ish):
    content = []
    putils.compile_file(RPC_DEFINITION_FILE_PATH)
    descriptor_set = putils.load_descriptor_set()
    for descriptor in descriptor_set.file:
        check_required_fields(descriptor)
        matches, single_responses, single_requests = get_rpc_sets_from_file_descriptor(descriptor)
        requests_path, _ = get_message_descriptor(descriptor, REQUESTS_MESSAGE_NAME)
        responses_path, _ = get_message_descriptor(descriptor, RESPONSES_MESSAGE_NAME)
        content.extend(get_rpcs_from_sets(descriptor, matches, single_responses, single_requests, repo_path, tree_ish,
                                          requests_path, responses_path))
    return ''.join(content)


def get_message_field_descriptors(file_descriptor, message_name):
    message_descriptors = []
    _, message_descriptor = get_message_descriptor(file_descriptor, message_name)
    if not message_descriptor:
        raise Exception(f'No message with name "{message_name}" found.')
    for field_id, field in enumerate(message_descriptor.field):
        if not field.type == descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE:
            continue
        message_descriptors.append((field_id, field))
    return message_descriptors


def get_message_descriptor(file_descriptor, message_name):
    for message_index, message in enumerate(file_descriptor.message_type):
        if message.name == message_name:
            return message_index, message
    return None


def is_request_present(file_descriptor):
    return get_message_descriptor(file_descriptor, REQUESTS_MESSAGE_NAME) is not None


def is_response_resent(file_descriptor):
    return get_message_descriptor(file_descriptor, RESPONSES_MESSAGE_NAME) is not None


def get_rpc_sets_from_file_descriptor(file_descriptor):
    if not is_request_present(file_descriptor):
        raise Exception('Request message not present.')
    if not is_response_resent(file_descriptor):
        raise Exception('Response message not present.')
    request_messages = get_message_field_descriptors(file_descriptor, REQUESTS_MESSAGE_NAME)
    response_messages = get_message_field_descriptors(file_descriptor, RESPONSES_MESSAGE_NAME)
    matches, leftover_requests, leftover_responses = get_matches(request_messages, response_messages)
    for left_request in leftover_requests:
        if left_request[1].name.endswith(REQUESTS_MESSAGE_NAME):
            raise Exception(f'No matching response for {left_request.name}')
    for left_response in leftover_responses:
        if left_response[1].name.endswith(RESPONSES_MESSAGE_NAME):
            raise Exception(f'No matching request for {left_response.name}')
    return matches, leftover_requests, leftover_responses


def get_matches(requests, responses):
    matches = []
    leftover_requests = []
    leftover_responses = responses.copy()
    for request in requests:
        match = None
        for response in responses:
            request_name = request[1].name.replace(REQUEST_MESSAGE_SUFFIX, '')
            response_name = response[1].name.replace(RESPONSE_MESSAGE_SUFFIX, '')
            if request_name == response_name:
                match = (request, response)
        if match is not None:
            matches.append(match)
            leftover_responses.remove(match[1])
        else:
            leftover_requests.append(request)
    return matches, leftover_requests, leftover_responses


def check_required_fields(file_descriptor):
    _, request_descriptor = get_message_descriptor(file_descriptor, REQUESTS_MESSAGE_NAME)
    request_fields = [field.name for field in request_descriptor.field]
    for required_field in REQUIRED_REQUEST_FIELDS:
        if required_field in request_fields:
            continue
        raise Exception(f'Required field "{required_field}" not present in request message.')

    _, response_descriptor = get_message_descriptor(file_descriptor, RESPONSES_MESSAGE_NAME)
    response_fields = [field.name for field in response_descriptor.field]
    for required_field in REQUIRED_RESPONSE_FIELDS:
        if required_field in response_fields:
            continue
        raise Exception(f'Required field "{required_field}" not present in response message.')
