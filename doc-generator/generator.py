import os
import argparse
import files
import protobuf

OUTPUT_DIRECTORY = '../doc'


def generate_protocol_doc(repo_path, branch_name):
    file = 'protocol.md'

    text = f"""---
layout: page
title: "The Prism Protocol"
toc: true
lang: en
tags: query interface, protobuf,protocol,grpc
---
{files.readme()}
## Message Categories

Below the available categories of messages and the explicit names of their .proto files are listed below.
{files.proto_files(repo_path, branch_name)}
## Protocol Messages

This section provides a comprehensive breakdown of protocol messages used in the communication between clients and the server.
The messages are categorized by the files containing them.
Starting from connection-related messages and extending to transaction handling and beyond, the documentation delves into the purpose, structure, and usage of each message.
{protobuf.messages(repo_path, branch_name)}
## Enums
This section provides an overview of the enums and their values. Enums are categorized by the files containing them.
{protobuf.enums(repo_path, branch_name)}

"""
    return file, text


def generate_overview_doc(repo_path, branch_name):
    file = 'overview.md'
    text = """---
layout: page
title: "Prism Interface - Overview"
toc: true
lang: en
tags: query interface, protobuf, protocol, prism, api
---

The _Prism Interface_ is a query interface designed specifically for interaction with Polypheny instances. Unlike traditional HTTP-based methods, this state-of-the-art communication channel employs a binary protocol based on Google Protocol Buffers, providing a versatile and efficient method for data exchange.

To interact and use this interface, we provide drivers and connectors for various query languages and technologies:

- [JDBC](/drivers/jdbc/overview)
- Python
- Go


## Features

The "Prism" protocol, integral to Polypheny's query interface, is aptly named to reflect its capability to seamlessly process a diverse array of query languages and data models. Much like a prism dispersing light into a vibrant spectrum, the Prism protocol intricately supports complex queries, delegating them adeptly across various data paradigms. This analogy underscores Prism's role in illuminating the multifaceted nature of data, enabling a harmonious interplay between different data types, akin to the mesmerizing display of colors revealed through a prism.

### Multi-Language Statement

One of the standout features of Prism Interface is its support for multi-language queries. You're not restricted to one query language; the Prism Interface can handle all query languages supported by Polypheny, allowing for greater flexibility in your data operations.

### Results in Different Data Models

Another powerful feature is the ability to retrieve query results in multiple data models. Whether you're dealing with relational, document-based, or the relational data models, Prism Interface can deliver results in the format most suited for your application's needs.

## Why use the Prism Interface?

- **Efficiency**: The use of a binary protocol minimizes overhead, ensuring faster communication between your application and the Polypheny instance.

- **Semantics-Preserving Interaction**: Prism Interface allows for a semantics-preserving interaction with the database's native types and results, ensuring data integrity and accuracy in your operations.

- **Multi-Platform**: Built upon the robust foundations of Google Protocol Buffers, the Prism protocol and API is designed to be used in various different programming languages.


## Acknowledgments

The initial version of the PrismInterface has been developed by [Tobias Hafner](https://github.com/TobiasHafner){:target="_blank"} as part of his Bachelor's thesis at the University of Basel.
"""
    return file, text


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def write_to_file(file, text):
    with open(file, 'w') as file:
        file.write(text)


def main(repo_path, branch_name, ):
    create_directory(OUTPUT_DIRECTORY)

    tasks = [
        generate_overview_doc,
        generate_protocol_doc
    ]

    for task in tasks:
        file, text = task(repo_path, branch_name)
        path = os.path.join(OUTPUT_DIRECTORY, file)
        write_to_file(path, text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate documentation links for GitHub files.")
    parser.add_argument('repo_path', type=str, help='The full path to the GitHub repository, e.g., "https://github.com/polypheny/Polypheny-Prism-API".')
    parser.add_argument('branch_name', type=str, help='The name of the branch to document.')

    args = parser.parse_args()

    main(args.repo_path, args.branch_name)

