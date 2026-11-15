# Polypheny-Prism-API
The definition files for the Polypheny Prism API, a multi-model, multi-language query interface.

The Prism Interface uses Protocol Buffer (protobuf) messages to define it's services. To keep things clear and well-organized, the message definitions are grouped into several files. This simplifies finding specific messages, based on what they do or what part of the system they relate to. The files itself are grouped in categories. Those are expressed in the file names.
Two kinds of categories exist:

### Request Response Category

The category type contains messages that are used in communication adhering to a request, response scheme. Here the client sends a request message to the server upon which the server sends back a response message.

- **Requests File**: This file contains all messages that are sent from the client to the server. The file name adheres to the following pattern: `[category]_requests.proto`. For example, all the request messages for making or managing connections would be in `connection_requests.proto`.

- **Responses File**: This is the partner file to Requests. It contains all the messages the server sends back to the client. Following the naming pattern, these files end with `_responses.proto`. The response messages related to connections would thus be in `connection_responses.proto`.

### Other Category
The other kind of category contains messages that are not directly used as a response to a request. An example therefore would be messages representing a specific datatype supported by the DBMS.
This category always contains only one file. The filename adheres to the pattern `[category].proto`.

### Doc Generator
Detailed Documentation of the proto files their messages and enums and much more can automatically be created using the doc generator included in this repo.
For this to work, the protobuf compiler must be installed. It's current version can be downloaded [here](https://github.com/protocolbuffers/protobuf/releases/).

To run the doc generator, execute the file `generator.py` in the `doc-generator` directory.

This creates a directory called docs containing the generated documentation.

### Generate Python files

Generate the Python code:
```
python -m grpc_tools.protoc -I . --python_out . org/polypheny/prism/*.proto
```

### Use the Go bindings

Install the Go module from your project with Go 1.23 or later.

```sh
go get github.com/polypheny/Polypheny-Prism-API/go/v2@v2.2.0
```

Import `github.com/polypheny/Polypheny-Prism-API/go/v2/prism` for the generated
messages and the Prism protocol version. The Go module is published from the
`go/` directory with a prefixed Git tag such as `go/v2.2.0`. The separate
Prism release tag `2.2` provides the existing `go-api-files-2.2.tar.gz` archive.
To publish the Go module, run **Build and publish Prism Go archive** on
`main` with **Publish the Go module tag for this revision of main** selected.

To regenerate the bindings after updating the protocol definitions, put
protoc 26.0 and protoc-gen-go 1.33.0 on PATH and run from the repository root.

```sh
generated="$(mktemp -d)"
bash go/generate.sh "$(cat go/VERSION)" "$generated"
diff -ru -I '^[[:space:]]*//' go/prism "$generated/prism"
```

Replace the generated files in `go/prism/` with the updated files from
`"$generated/prism"`. Update `go/VERSION` when the protocol version changes.

### Test protocol contracts

The Python contract tests compile the checked-out definitions into a temporary directory
and check the document metadata messages, wire compatibility, and optional-field presence.

```
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```
