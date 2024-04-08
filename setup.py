from setuptools import setup, find_packages
import swarmauri

setup(
    name='swarmauri',
    version=swarmauri.__version__,
    author='Jacob Stewart',
    author_email='your_email@example.com',
    description='A short description of your package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='http://github.com/yourusername/your_package_name',
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
            'ampligraph',
            'pygments',
            'stanford_openie'
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
            'accelerate',
            'tensorflow',
            'scipy',
            'typing_extensions',
            'redisearch',
            'google-api-python-client',
            'google-auth-httplib2',
            'google-auth-oauthlib',
            'boto3',
            'yake',
            'torch',
            'scikit-learn',
            'gensim',
            'lightgbm',
            'rdflib',
            'ampligraph',
            'weaviate',
            'textblob',
            'spacy',
            'pygments',
            'stanford_openie'
        ]},
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.10',
    setup_requires=["wheel"]
)