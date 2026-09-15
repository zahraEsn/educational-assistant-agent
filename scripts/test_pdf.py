from services.rag.pdf_loader import load_pdf_pages

pages = load_pdf_pages("data/books/اول/ریاضی.pdf")

print("pages:", len(pages))

for page in pages[:3]:
    print("=" * 50)
    print("PAGE:", page["page"])
    print(page["text"][:1000])
