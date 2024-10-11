import os
from setuptools import setup

version_file = 'prism-api-version.txt'

if not os.path.exists(version_file):
    raise ValueError(f"Version file '{version_file}' not found. Please create the file with the version number.")

with open(version_file, 'r') as f:
    version = f.read().strip()

print(f"Building version: {version}")

if version == '0.0':
    raise ValueError("Version is set to '0.0'. Please set a valid version number in the version file.")

# Attempt to split the version number, default to '0' for both if it fails
try:
    major, minor = version.split('.')
except ValueError:
    raise ValueError(f"Invalid version format: {version}. Expected 'major.minor' format.")

with open('org/polypheny/prism/version.py', 'w') as f:
    f.write(f'MAJOR_VERSION = {major}\n')
    f.write(f'MINOR_VERSION = {minor}\n')

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='polypheny-prism-api',
    version=version,
    description='Polypheny Prism API files for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="The Polypheny Project",
    author_email="mail@polypheny.org",
    url="https://polypheny.com/",
    project_urls={
        "Documentation": "https://docs.polypheny.com/en/latest/query_interfaces/prism/protocol",
        "Code": "https://github.com/polypheny/Polypheny-Prism-API"
    },
    license="Apache License, Version 2.0",
    packages=['org/polypheny/prism'],
    install_requires=[
        "protobuf==5.27.2",
    ],
)
