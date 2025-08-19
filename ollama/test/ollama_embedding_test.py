import ollama

result = ollama.embeddings(model='nomic-embed-text', prompt="This is a sentence I want to embed")
print(result.get('embedding', 'No embedding found'))