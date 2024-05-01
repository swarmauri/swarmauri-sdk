from setuptools import setup, find_packages
import swarmauri

setup(
    name='swarmauri',
    version=swarmauri.__version__,
    author='Jacob Stewart',
    author_email='corporate@swarmauri.com',
    description='This repository includes core interfaces, standard ABCs and concrete references, third party plugins, and experimental modules for the swarmaURI framework.',
    long_description=swarmauri.__long_desc__,
    long_description_content_type='text/markdown',
    url='http://github.com/swarmauri/swarmauri-sdk',
    license='MIT',
    packages=find_packages(include=['swarmauri*']),  # Include packages in your_package and libs directories
    install_requires=[
        'numpy',  # Common dependencies for all distributions
        'requests'
    ],
    extras_require={
        'standard': [
            'openai',
            'transformers',
            'accelerate',
            'tensorflow',
            'scipy',
            'typing_extensions',
            'scikit-learn',
            'gensim',
            'rdflib',
            'pygments',
            'stanford_openie',
            'sentencepiece',
            'gradio',
            'websockets'
        ],
        'community': [
            'openai',
            'transformers',
            'accelerate',
            'tensorflow',
            'scipy',
            'typing_extensions',
            'redisearch',
            'google-api-python-client',
            'google-auth-httplib2',
            'google-auth-oauthlib',
            'boto3'
        ],
        'experimental': [
            'openai',
            'transformers',
            'accelerate',
            'tensorflow',
            'scipy',
            'typing_extensions',
            'google-api-python-client',
            'google-auth-httplib2',
            'google-auth-oauthlib',
            'boto3',
            'lightgbm'
        ],
        'full': [
            'openai',
            'transformers',
            #'accelerate',
            'tensorflow',
            'scipy',
            'typing_extensions',
            'redisearch',
            'google-api-python-client',
            'google-auth-httplib2',
            'google-auth-oauthlib',
            'boto3',
            #'yake',
            'torch',
            'scikit-learn',
            'gensim',
            #'lightgbm',
            #'rdflib',
            'textblob',
            'spacy==3.7.4',
            'pygments',
            #'stanford_openie',
            #'sentencepiece',
            'gradio',
            'websockets',
            'groq',
            'mistralai',
            'cohere',
            'google-generativeai',
            'anthropic'

        ]},
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10'
    ],
    python_requires='>=3.10',
    setup_requires=["wheel"]
)