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

### Test protocol contracts

The Python contract tests compile the checked-out definitions into a temporary directory
and check the document metadata messages, wire compatibility, and optional-field presence.

```
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

### Publish a Prism API release

The Polypheny GitHub organization stores the Maven Central credentials as shared
Actions secrets. Under **Organization Settings → Secrets and variables → Actions**,
check that the access policy for both secrets includes `Polypheny-Prism-API` and any
other Polypheny repositories that use them.

| Organization secret | Value from the same Sonatype user token |
| --- | --- |
| `CENTRAL_USERNAME` | Generated token username |
| `CENTRAL_TOKEN` | Generated token password |

Generate the pair in the [Central Publisher Portal](https://central.sonatype.com/usertoken)
using an account with publishing access to `org.polypheny`. When rotating the token,
update both organization secrets together and check the repositories that share them.

Before publishing, check the [Maven signing secrets](.github/workflows/publish-maven-central.yml)
and the [PyPI trusted publisher](.github/workflows/publish-pypi.yml).

Configure [NuGet Trusted Publishing](https://learn.microsoft.com/en-us/nuget/nuget-org/trusted-publishing#github-actions-setup)
under the NuGet owner of `Polypheny.Prism`. Use GitHub repository owner `polypheny`,
repository `Polypheny-Prism-API`, workflow file `publish-dotnet.yml`, and environment
`nuget`. Scope the policy to publishing new versions of `Polypheny.Prism`. In the
repository's **Settings → Environments**, create `nuget` and set its Actions
variable `NUGET_USER` to the personal NuGet profile name that created the policy.
Under **Deployment branches and tags**, select **Selected branches and tags** and
allow release tags with a tag rule such as `*.*`.
The release job exchanges its GitHub OIDC token for a temporary NuGet API key.
The package build checks on pull requests and manual runs do not upload packages.

Create a GitHub release targeting the verified commit on `main`, with a `major.minor`
tag such as `2.2`. Publishing the GitHub release starts the package uploads. Check
the runs under **Actions** and the assets on the release page. Once the Maven
deployment is **Validated**, publish it in the
[Central Publisher Portal](https://central.sonatype.com/publishing/deployments) and
check that it reaches **Published**.
