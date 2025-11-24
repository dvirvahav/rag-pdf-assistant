from services.embedding_service import embed_chunks

# דוגמה לצ'אנקים קצרים לבדיקה
chunks = [
    "Hello world",
    "This is another chunk of text",
    "Embedding test"
]

vectors = embed_chunks(chunks)

print("Total vectors:", len(vectors))
print("Vector length for first chunk:", len(vectors[0]))
print("First vector (first 5 numbers):", vectors[0][:5])
