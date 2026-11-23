from swarmauri_llm_falai import FalAIVisionModel

model = FalAIVisionModel(api_key="FAL_KEY")

answer = model.predict(
    image_url="https://llava-vl.github.io/static/images/monalisa.jpg",
    prompt="Who painted this artwork?",
)

print(answer)
