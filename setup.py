import os
import sys

from setuptools import setup

# Retrieve 'VERSION' environment variable, default to '0.0' if not found.
version = os.getenv('VERSION', '0.0')

# Attempt to split the version number, default to '0' for both if it fails
try:
    major, minor = version.split('.')
except ValueError:
    major, minor = '0', '0'  # Default to '0.0' if the version isn't in a 'major.minor' format


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
      packages=['org/polypheny/prism'],
      install_requires=[
          "protobuf==4.24.3",
      ],
      )
