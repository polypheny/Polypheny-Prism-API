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
                          '--proto_path=@CURRENT_SOURCE_DIR@',
                          '--cpp_out=@BUILD_DIR@',
                          '--experimental_allow_proto3_optional',
                          '@INPUT@'
                      ]
)

prism_files = files(
    'org/polypheny/prism/connection_requests.proto',
    'org/polypheny/prism/connection_responses.proto',
    'org/polypheny/prism/document_frame.proto',
    'org/polypheny/prism/error.proto',
    'org/polypheny/prism/graph_frame.proto',
    'org/polypheny/prism/meta_requests.proto',
    'org/polypheny/prism/meta_responses.proto',
    'org/polypheny/prism/namespace_meta_requests.proto',
    'org/polypheny/prism/namespace_meta_responses.proto',
    'org/polypheny/prism/protointerface.proto',
    'org/polypheny/prism/relational_frame.proto',
    'org/polypheny/prism/statement_requests.proto',
    'org/polypheny/prism/statement_responses.proto',
    'org/polypheny/prism/transaction_requests.proto',
    'org/polypheny/prism/transaction_responses.proto',
    'org/polypheny/prism/value.proto',
    'org/polypheny/prism/stream_requests.proto',
    'org/polypheny/prism/stream_responses.proto'
)

# ========================
# Library and Dependencies
# ========================

prism_src = prism_gen.process(prism_files, preserve_path_from: meson.current_source_dir())

# TODO: find a clean way to specify the include dir for the generated protobuf code
include_dirs = include_directories('libpolypheny_prism_api.a.p/')

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
