from swarmauri_parser_entityrecognition import EntityRecognitionParser

text = "Barack Obama was born in Hawaii and served as President of the United States."
parser = EntityRecognitionParser()
entities = parser.parse(text)

for entity in entities:
    print(entity.content, entity.metadata["entity_type"])
