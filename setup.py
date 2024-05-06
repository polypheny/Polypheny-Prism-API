import os

from setuptools import setup

version = os.getenv('version', '0.0').split('.')
if len(version) != 2:
    raise Exception('Invalid version format')

with open('org/polypheny/prism/version.py', 'w') as f:
    f.write(f'MAJOR_VERSION = {version[0]}\n')
    f.write(f'MINOR_VERSION = {version[1]}\n')

setup(name='polyphenyprism',
      version=version,
      description='Protobuf files for Polypheny',
      packages=['org/polypheny/prism'],
      install_requires=[
          "protobuf==4.24.3",
      ],
      )
