from setuptools import setup, find_packages
import swarmauri_core

setup(
    name='swarmauri-core',
    version=swarmauri_core.__version__,
    author='Jacob Stewart',
    author_email='corporate@swarmauri.com',
    description='This repository includes core interfaces, standard ABCs and concrete references, third party plugins, and experimental modules for the swarmaURI framework.',
    long_description=swarmauri_core.__long_desc__,
    long_description_content_type='text/markdown',
    url='http://github.com/swarmauri/swarmauri-sdk',
    license='Apache Software License',
    packages=find_packages(include=['swarmauri_core*']),  # Include packages in your_package and libs directories
    install_requires=[
        'numpy==1.26.4',
        'requests',
        'pydantic',
        'pandas>2.2'
    ],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ],
    python_requires='>=3.10',
    setup_requires=["wheel"]
)
