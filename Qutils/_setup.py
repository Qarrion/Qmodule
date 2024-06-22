
from setuptools import setup, find_packages
"""
location file :
    project
        - my_module (import name)
        - my_util

    <setup.py>    
"""

# ---------------------------------- simple ---------------------------------- #

setup(
    name='my_package (pip name)',
    version='0.0.1',
    packages=find_packages(include=['project']),
    package_data={
        'my_package':['data.ini']
    },
    install_requires=[
        'requests>=2.25.1',
        'numpy==1.19.4',
        'pandas'
    ]
)

# --------------------------------- with libs -------------------------------- #
setup(
    name='my_package (pip name)',
    version='0.0.1',
    packages=find_packages(include=['project']),
    package_data={
        'my_package':['data.ini']
    },
    install_requires=[
        'requests>=2.25.1',
        'numpy==1.19.4',
        'pandas'
    ]
)

# --------------------------------- with file -------------------------------- #
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='my_package (pip name)',
    version='0.0.1',
    packages=find_packages(include=['project']),
    package_data={
        'my_package':['data.ini']
    },
    install_requires=required
)