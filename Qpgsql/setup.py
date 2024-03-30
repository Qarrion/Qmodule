from setuptools import setup, find_packages

setup(
    name='Qpgsql',
    version='0.0.1',
    packages=find_packages(include=['Qpgsql']),
    package_data={},
    install_requires=[
        'psycopg',
        'psycopg-binary'
    ],
)