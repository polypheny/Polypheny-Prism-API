#!/bin/bash

# Ensure you have Python 3.8 installed
# Ensure you have the necessary permissions to run this script

set -e  # Exit immediately if a command exits with a non-zero status

# Set the version based on the current timestamp
TIMESTAMP=$(date +'%Y%m%d%H%M%S')
VERSION="1.10.${TIMESTAMP}"

# Download protobuf for Linux
echo "Downloading Protobuf..."
curl -LO https://github.com/protocolbuffers/protobuf/releases/download/v26.0/protoc-26.0-linux-x86_64.zip
if [ $? -ne 0 ]; then
    echo "Failed to download Protobuf"
    exit 1
fi

unzip protoc-26.0-linux-x86_64.zip
if [ $? -ne 0 ]; then
    echo "Failed to unzip Protobuf"
    exit 1
fi

# Build Protobuf Files
echo "Building Protobuf files..."
bin/protoc --experimental_allow_proto3_optional -I . --python_out . org/polypheny/prism/*.proto
if [ $? -ne 0 ]; then
    echo "Failed to build Protobuf files"
    exit 1
fi

# Set the version in the environment
export VERSION=$VERSION

# Build the package
echo "Building the package..."
python3 setup.py sdist
if [ $? -ne 0 ]; then
    echo "Failed to build the package"
    exit 1
fi

# Clean up the downloaded Protobuf files
rm protoc-26.0-linux-x86_64.zip
rm -rf bin

echo "Package built successfully. You can find it in the 'dist' directory."
