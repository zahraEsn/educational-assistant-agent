# Educational Assistant Agent

An AI-powered educational assistant for Iranian elementary school students.

The system combines a **local LLM**, **textbook-based RAG**, and **teacher-guided personalization** to help students learn their school subjects and practice the skills they need to improve.

![AI Tutor Demo](/image1.png)
![AI Tutor Demo](/image2.png)
![AI Tutor Demo](/image3.png)
![AI Tutor Demo](/image4.png)


## Features

### Student Panel

* Supports grades **1 to 6** of elementary school.
* Shows subjects based on the selected grade.
* Two learning modes:

  * **Explain:** simple, step-by-step explanations adapted to the student's grade.
  * **Quiz:** generates educational questions based on the selected subject and textbook content.
* Maintains conversation context during the session.
* Uses retrieved textbook content as the main source for educational responses.
* Shows retrieved textbook sources, including grade, subject, page, and file.

### Teacher Panel

* Enter the student's name, grade, and subject.
* Record the student's **weak skills** and additional **teacher notes**.
* Generate a personalized worksheet with **5 to 10 questions**.
* Questions are designed around the student's specific weaknesses rather than as a generic test.
* Supports different question types such as:

  * Multiple choice
  * True/false
  * Fill in the blank
  * Short answer
  * Problem solving
* Questions include a difficulty level and a non-revealing hint.
* Teachers can edit questions and hints before generating the final worksheet.
* Generates a printable **A4 PDF worksheet** with Persian RTL layout.

### Textbook RAG

The application uses the Iranian elementary-school textbooks as a knowledge source.

The RAG pipeline:

```text
Textbook PDFs
     |
     v
PDF text extraction
     |
     v
Chunking
(1000 chars / 150 overlap)
     |
     v
BAAI/bge-m3 embeddings
     |
     v
FAISS vector index
     |
     v
Semantic retrieval
     |
     v
Grade + subject filtering
     |
     v
Relevant textbook context
     |
     v
Local Ollama model
```

Textbook PDFs are extracted with **PyMuPDF**, split into overlapping chunks, embedded with **`BAAI/bge-m3`**, and stored in a **FAISS inner-product index** together with metadata such as grade, subject, page, and source file.

For each request, retrieval is restricted to the selected grade and subject before the retrieved context is passed to the language model.

## Tech Stack

* **Python**
* **Streamlit** — web interface
* **Ollama** — local LLM inference
* **Sentence Transformers** — embeddings
* **BAAI/bge-m3** — embedding model
* **FAISS** — vector search
* **PyMuPDF** — PDF text extraction
* **WeasyPrint** — worksheet PDF generation
* **Yekan Bakh** — Persian RTL UI and PDF typography

The current dependency set is defined in `requirements.txt`.

## Project Structure

```text
educational-assistant-agent/
├── app.py
├── pages/
│   ├── پنل_دانش‌آموز.py
│   └── پنل_معلم.py
├── services/
│   ├── ai.py
│   ├── worksheet_pdf.py
│   └── rag/
│       ├── chunker.py
│       ├── embedder.py
│       ├── pdf_loader.py
│       ├── retriever.py
│       └── vector_store.py
├── prompts/
│   └── quiz_prompts.py
├── scripts/
│   ├── index_books.py
│   └── test_embedding.py
├── utils/
├── config/
├── docs/
├── fonts/
├── assets/
├── tests/
├── requirements.txt
└── requirements-dev.txt
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/zahraEsn/educational-assistant-agent.git
cd educational-assistant-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and run Ollama

Install Ollama and make sure it is running.

For example, install a model such as:

```bash
ollama pull gemma3
```

The application automatically detects installed Ollama models and presents them in the UI.

## Preparing the Textbook Knowledge Base

Place the textbook PDFs inside:

```text
data/books/
```

Organize them by grade:

```text
data/
└── books/
    ├── اول/
    │   ├── ریاضی.pdf
    │   ├── فارسی.pdf
    │   └── ...
    ├── دوم/
    │   ├── ریاضی.pdf
    │   └── ...
    └── ششم/
        ├── ریاضی.pdf
        └── ...
```

Then build the vector index:

```bash
python scripts/index_books.py
```

The indexing script:

1. Finds all textbook PDFs under `data/books`.
2. Extracts text page by page.
3. Splits pages into overlapping chunks.
4. Creates `bge-m3` embeddings.
5. Builds the FAISS index.
6. Saves the index and metadata under:

```text
data/vector_store/
├── index.faiss
└── metadata.json
```

This workflow is implemented in `scripts/index_books.py`.

## Run the Application

Start Streamlit with:

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

The main dashboard provides access to:

* Student Panel
* Teacher Panel

## How Personalization Works

The teacher provides:

```text
Grade
Subject
Student weaknesses
Teacher notes
Number of questions
```

The system first retrieves relevant textbook chunks for that grade and subject. These retrieved materials are then included in the worksheet-generation prompt along with the student's weaknesses and teacher notes.

The quiz-generation prompt explicitly requires:

* questions to target the student's weaknesses,
* difficulty progression from easy to hard,
* varied question types,
* short and age-appropriate wording,
* meaningful hints,
* no answer or solution fields,
* valid JSON output.

## Persian and RTL Support

The application is designed for Persian-speaking students and teachers.

It includes:

* Persian UI text
* Right-to-left layout
* Persian typography using Yekan Bakh
* RTL PDF worksheets
* Persian page numbering
* Grade-specific Persian school subjects

The global UI styles explicitly configure RTL direction and Yekan Bakh for Streamlit inputs, labels, sidebar, buttons, and other components.

## Design Goals

The project is built around four main ideas:

**Personalized learning**
Practice should target what the student actually struggles with.

**Textbook-grounded answers**
The system should prefer the relevant school textbook instead of relying only on the model's general knowledge.

**Teacher in the loop**
Teachers define the student's weaknesses and can review and edit generated worksheets before using them.

**Local AI**
The language model runs through Ollama locally, keeping the main tutoring and worksheet-generation workflow on the user's machine.

## Current Status

This project is an active development project. The current implementation focuses on:

* Persian elementary education
* Student tutoring
* Teacher-generated personalized worksheets
* Textbook RAG
* Local Ollama models
* PDF worksheet generation

## Future Improvements

Planned areas for improvement include:

* Better evaluation of generated questions
* Improved retrieval quality
* More robust structured-output validation
* Student progress tracking
* Learning history and performance analytics
* More educational content and textbook coverage
* Better worksheet generation and customization
