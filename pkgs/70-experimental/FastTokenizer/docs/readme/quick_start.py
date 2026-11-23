import fasttokenizer

# Load the text from a file
text = fasttokenizer.load_text("example.txt")

# Tokenize the text
tokens = fasttokenizer.tokenize(text)

# Get the regex pattern used for tokenization
pattern = fasttokenizer.get_pattern()

# Save the text to a file
fasttokenizer.save_text("output.txt", text)

# Read the text from a file
read_text = fasttokenizer.read_text("example.txt")

# Tokenize the text again
tokens = fasttokenizer.tokenize(read_text)

# Get the normalized text
normalized_text = fasttokenizer.normalize_unicode(read_text)

# Print the results
print("Tokens:", tokens)
print("Normalized Text:", normalized_text)
