from setuptools import setup

setup(
    name='minkyo',
    version='1.1',
    description='Tool to assign rides',
    author='dhong',
    author_email='dhong12@ucsc.edu',
    packages=['minkyo'],
    install_requires=[
        'python-dotenv',
        'googlemaps',
        'requests',
    ],
)
