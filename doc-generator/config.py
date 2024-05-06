# ==================================================================================
# POLYPRISM DOCUMENTATION GENERATOR CONFIGURATION
# ==================================================================================

# ----------------------------------------------------------------------------------
# RPC FILES
# ----------------------------------------------------------------------------------

# This is the name of the .proto file where the top level request, response and error message is defined.
# This file must be inside the PROTO_DIR also specified in this config.
RPC_DEFINITION_FILE = 'protointerface.proto'

# These fields must be present in the top level request message. If on of them is missing, the documentation will not
# generate and an exception will be thrown.
REQUIRED_REQUEST_FIELDS = [
    'id',
    'dbms_version_request',
    'connection_request',
    'disconnect_request'
]

# These fields must be present in the top level response message. If on of them is missing, the documentation will not
# generate and an exception will be thrown.
REQUIRED_RESPONSE_FIELDS = [
    'id',
    'last',
    'error_response',
    'dbms_version_response',
    'connection_response',
    'disconnect_response'
]

# The common suffix of all rpc request messages in the top level request message.
REQUESTS_MESSAGE_NAME = 'Request'

# The common suffix of all rpc response messages in the top level response message.
RESPONSES_MESSAGE_NAME = 'Response'

# The common suffix of the names of all .proto files that contain response messages.
RESPONSE_FILE_SUFFIX = '_response'

# The common suffix of the names of all .proto files that contain request messages.
REQUEST_FILE_SUFFIX = '_request'

# ----------------------------------------------------------------------------------
# PROTO FILES
# ----------------------------------------------------------------------------------

# The directory containing the proto files
PROTO_DIR = '../org/polypheny/prism'

# ----------------------------------------------------------------------------------
# PROTO COMPILER
# ----------------------------------------------------------------------------------

# File name of the temporary descriptor set file generated by the proto compiler.
DESCRIPTOR_SET_OUT = 'descriptor_set.bin'

# The directory from which the imports in the .proto files are resolved.
IMPORT_BASE_DIR = '../' #../org/polypheny/prism'


# ----------------------------------------------------------------------------------
# DOCUMENTATION
# ----------------------------------------------------------------------------------

# The readme file of this repo. Its content is put at the top of the protocol.md file generated by this tool.
README_FILE = '../README.md'

# The directory in which the generated documentation should be put. The directory is created if it does not exist.
OUTPUT_DIR = '../doc'