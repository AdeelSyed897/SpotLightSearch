
from src.parser import extract_text
from src.chunker import chunk_text

text = extract_text("test_files/sample.txt")


print("Extracted text:", repr(text))
print("Type:", type(text))

chunks = chunk_text(text, chunk_size=20, overlap=5)

for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i + 1} ---")
    print(chunk)
    print(f"Word count: {len(chunk.split())}")
