from setuptools import setup, find_packages
import swarmauri_community

setup(
    name="swarmauri-community",
    version=swarmauri_community.__version__,
    author="Jacob Stewart",
    author_email="corporate@swarmauri.com",
    description="Community version of the swarmauri framework",
    long_description=swarmauri_community.__long_desc__,
    long_description_content_type="text/markdown",
    url="http://github.com/swarmauri/swarmauri-sdk",
    license='Apache Software License',
    packages=find_packages(
        include=["swarmauri_community*"]
    ),  # Include packages in your_package and libs directories
    install_requires=[
        "numpy",  # Common dependencies for all distributions
        "requests",
        "pydantic",
        "pymupdf",
        "swarmauri-core==0.5.0.dev8",
        "swarmauri==0.5.0.dev8"
    ],
    extras_require={
        "full": [
            "ai21>=2.2.0",
            "shuttleai",
            "transformers",
            "tensorflow",
            "typing_extensions",
            "google-api-python-client",
            "google-auth-httplib2",
            "google-auth-oauthlib",
            "boto3",
            "yake",
            "torch",
            "scikit-learn",
            "gensim",
            "textblob",
            "spacy",
            "pygments",
            "gradio",
            "websockets",
            "openai",
            "groq",
            "mistralai",
            "cohere",
            "google-generativeai",
            "anthropic",
            "scipy",
            "qdrant-client",
            "chromadb",
            "textstat",
            "nltk",
            "psutil",
            "qrcode",
            "folium",
            "captcha",
            "bs4",
            "pygithub",
            "pacmap",
            "tf-keras",
        ]
    },
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    setup_requires=["wheel"],
)
