from setuptools import setup, find_packages

setup(
    name='aweber_api',
    version='1.0.3',
    packages=find_packages(exclude=['tests']),
    url='https://github.com/aweber/AWeber-API-Python-Library',
    install_requires = ['oauth2 >= 1.2'],
    include_package_data=True
)

