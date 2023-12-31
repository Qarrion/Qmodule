from setuptools import setup, find_packages

setup(
    name='Qupbit',
    version='0.0.1',
    packages=find_packages(include=['Qupbit']),
    package_data={
        'Qupbit':['limit.ini']
    },
    install_requires =[
        'requests',
        'websockets'
    ]
)