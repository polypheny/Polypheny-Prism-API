project('polypheny_prism_api', 'cpp', default_options : ['cpp_std=c++17'])

# ========================
# Dependencies
# ========================

protobuf_subproject = subproject('protobuf')
protobuf_dep = protobuf_subproject.get_variable('protobuf_dep')
protoc = protobuf_subproject.get_variable('protoc')

# ========================
# Protobuf Code Generation
# ========================
gen_dir = meson.current_build_dir() / 'libpolypheny_prism_api.a.p'
run_command('mkdir', '-p', gen_dir)

prism_gen = generator(protoc,
                      output : ['@BASENAME@.pb.cc', '@BASENAME@.pb.h'],
                      arguments : [
                          '--proto_path=@CURRENT_SOURCE_DIR@/prism',
                          '--cpp_out=@BUILD_DIR@',
                          '--experimental_allow_proto3_optional',
                          '@INPUT@'
                      ]
)

prism_files = files(
    'prism/connection_requests.proto',
    'prism/connection_responses.proto',
    'prism/document_frame.proto',
    'prism/error.proto',
    'prism/graph_frame.proto',
    'prism/meta_requests.proto',
    'prism/meta_responses.proto',
    'prism/namespace_meta_requests.proto',
    'prism/namespace_meta_responses.proto',
    'prism/protointerface.proto',
    'prism/relational_frame.proto',
    'prism/statement_requests.proto',
    'prism/statement_responses.proto',
    'prism/transaction_requests.proto',
    'prism/transaction_responses.proto',
    'prism/value.proto'
)

# ========================
# Library and Dependencies
# ========================

prism_src = prism_gen.process(prism_files)

# TODO: find a clean way to specify the include dir for the generated protobuf code
include_dirs = include_directories('libpolypheny_prism_api.a.p')

polypheny_prism_api_lib = static_library('polypheny_prism_api',
                                         prism_src,
                                         dependencies : [protobuf_dep],
                                         include_directories : include_dirs
)

polypheny_prism_api_dep = declare_dependency(
    link_with: polypheny_prism_api_lib,
    include_directories: include_dirs,
    dependencies: [protobuf_dep],
)
