from setuptools import setup, find_packages

setup(
    name='multithreaded',
    version='0.0.4',
    packages=find_packages(),
    install_requires=['cloudpickle', 'logzero', 'stop-thread'],
    author='Noah018',
    author_email='noahc018@pm.me',
    description='advanced threading made beginner... threading library that expands upon stdlib "threading."',
    long_description=open('README.md', 'r').read(), 
    long_description_content_type='text/markdown',
    url='https://github.com/Noah018dev/multithreaded',
    classifiers=[
        'Programming Language :: Python :: 3'
    ],
    license=open('UNLICENSE').read()
)