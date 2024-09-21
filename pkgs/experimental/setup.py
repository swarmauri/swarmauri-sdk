from setuptools import setup, find_packages
import swarmauri_experimental

setup(
    name="swarmauri-experimental",
    version=swarmauri_experimental.__version__,
    author="Jacob Stewart",
    author_email="corporate@swarmauri.com",
    description="Experimental version of the swarmauri framework",
    long_description=swarmauri_experimental.__long_desc__,
    long_description_content_type="text/markdown",
    url="http://github.com/swarmauri/swarmauri-sdk/swarmauri-experimental",
    license="MIT",
    packages=find_packages(
        include=["swarmauri_experimental*"]
    ),  # Include packages in your_package and libs directories
    install_requires=[
        "numpy",  # Common dependencies for all distributions
        "requests",
        "pydantic",
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
