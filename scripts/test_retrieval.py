from services.rag.retriever import retrieve

results = retrieve(
    query="کلمه هایی که حروف مشابه دارند و باید درست نوشته شوند",
    grade="اول",
    subject="فارسی",
    top_k=5,
    candidate_k=100,
)

print()
print("=" * 80)
print("RETRIEVAL TEST")
print("results:", len(results))
print("=" * 80)

for i, result in enumerate(results, start=1):
    print()
    print(f"RESULT {i}")
    print("score:", result["score"])
    print("grade:", result["grade"])
    print("subject:", result["subject"])
    print("page:", result["page"])
    print("source:", result["source"])
    print("text:")
    print(result["text"])
    print("-" * 80)
