
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_llm_leptonai/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_llm_leptonai" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_leptonai/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_leptonai.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_leptonai/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_llm_leptonai" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_leptonai/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_leptonai" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_leptonai/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_leptonai?label=swarmauri_llm_leptonai&color=green" alt="PyPI - swarmauri_llm_leptonai"/></a>
</p>

---

# Swarmauri LLM LeptonAI

This package provides integration with Lepton AI's text and image generation models.

## Installation

```bash
pip install swarmauri_llm_leptonai
```

## Usage
Basic usage examples with code snippets

#### Text Generation
```python
from swarmauri.llms.LeptonAIModel import LeptonAIModel

# Initialize the model
model = LeptonAIModel(api_key="your_api_key")

# Generate text
conversation = Conversation()
conversation.add_message(HumanMessage(content="Hello, how are you?"))
response = model.predict(conversation=conversation)
print(response.get_last().content)
```


#### Image Generation
```python
from swarmauri.image_gens.LeptonAIImgGenModel import LeptonAIImgGenModel

# Initialize the model
img_model = LeptonAIImgGenModel(api_key="your_api_key")

# Generate an image
prompt = "A cute cat playing with a ball of yarn"
image_bytes = img_model.generate_image(prompt=prompt)

# Save the image
with open("generated_image.png", "wb") as img_file:
    img_file.write(image_bytes)
```
## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
