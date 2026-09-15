from services.rag.embedder import embed_texts

texts = [
    "عددهای طبیعی شامل اعداد ۰، ۱، ۲، ۳ و ... هستند.",
    "گیاهان برای رشد به نور و آب نیاز دارند.",
]

embeddings = embed_texts(texts)

print("shape:", embeddings.shape)
print("dtype:", embeddings.dtype)
print("first vector length:", len(embeddings[0]))
