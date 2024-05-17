import os
import sys

from setuptools import setup

# Retrieve 'VERSION' environment variable, default to '0.0' if not found.
version = os.getenv('VERSION', '0.0')

print(f"Building version: {version}")

if version == '0.0':
    raise ValueError("Version not set or defaulting to '0.0'. Please set the VERSION environment variable.")

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

setup(name='polypheny-prism-api',
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
          "protobuf==4.24.3",
      ],
)
