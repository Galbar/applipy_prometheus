from setuptools import setup, find_packages
from distutils.util import convert_path
from os import path

ns = {}
ver_path = convert_path('applipy_prometheus/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), ns)
version = ns['__version__']

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='applipy_prometheus',
    url='https://gitlab.com/applipy/applipy_prometheus',
    project_urls={
        'Source': 'https://gitlab.com/applipy/applipy_prometheus',
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description='Exposes applipy metrics in prometheus format',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='Apache 2.0',
    author='Alessio Linares',
    author_email='mail@alessio.cc',
    version=version,
    packages=find_packages(exclude=['doc', 'tests']),
    data_files=[],
    python_requires='>=3.6',
    install_requires=[
        'applipy_http~=0.13',
        'applipy_metrics~=0.11',
    ],
    scripts=[],
)
