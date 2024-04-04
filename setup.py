from distutils.core import setup

setup(name='polyphenyprism',
      version='0.1',
      description='Protobuf files for Polypheny',
      packages=['polyprism'],
      install_requires=[
          "protobuf==4.24.3",
      ],
      )
