import os

from setuptools import setup

version = os.getenv('version', '0.0')
major, minor = version.split('.')

with open('org/polypheny/prism/version.py', 'w') as f:
    f.write(f'MAJOR_VERSION = {major}\n')
    f.write(f'MINOR_VERSION = {minor}\n')

setup(name='polyphenyprism',
      version=version,
      description='Protobuf files for Polypheny',
      packages=['org/polypheny/prism'],
      install_requires=[
          "protobuf==4.24.3",
      ],
      )
