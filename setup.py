from setuptools import setup

setup(
    name='minkyo',
    version='0.1',
    description='Tool to assign rides',
    author='dhong',
    author_email='ddanielhongg@gmail.com',
    packages=['minkyo'],
    install_requires=[
        'python-dotenv',
        'googlemaps',
        'requests',
    ],
)
