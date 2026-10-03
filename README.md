# Multimodal RAG Assistant

A Streamlit app that brings together searchable PDF documents and structured
HR sample data. Upload policy or report PDFs, find relevant pages, and explore
HR summaries with tables and charts. Groq AI can optionally write a short
answer using the retrieved evidence.

> **Demo data:** `data/demo_employees.csv` contains fictional records. Do not
> use this project or its sample statistics to make employment decisions.

## Features

- Upload one or more text-based PDF files.
- Search PDF page text with TF-IDF and display matching page numbers.
- View employee counts, attrition counts, average monthly income, and overtime
  counts from the included CSV.
- Display HR summaries as a table and chart.
- Optionally generate an answer from the question and displayed evidence with
  Groq.
- Run the document search and HR summaries locally without an AI key or
  database server.

## How it works

1. The app extracts text from each uploaded PDF page.
2. TF-IDF converts page text and the question into word-weight vectors.
3. Cosine similarity ranks PDF pages by how closely their words match the
   question. The app displays the best matching pages as evidence.
4. Pandas reads the sample employee CSV and groups it for the selected HR
   summary.
5. If Groq is configured, the question and evidence are sent to the AI service
   to produce a written answer. Otherwise, the app displays the evidence
   without generating an answer.

This is a small learning/demo RAG flow. TF-IDF is a word-matching technique,
not a large language model embedding, and matching a passage does not guarantee
that it answers the question.

## Technology

- Python
- Streamlit
- Pandas
- pypdf
- scikit-learn (TF-IDF and cosine similarity)
- Plotly/Streamlit charts
- Groq API (optional)

## Project structure

```text
app.py                    Streamlit user interface
assistant.py              PDF retrieval, HR summaries, optional AI answer
data/
  demo_employees.csv      Fictional HR data for summaries and charts
tests/
  test_assistant.py       Tests for the core helper functions
.env.example              Template for optional Groq configuration
.gitignore                Excludes local secrets and generated files
requirements.txt          Python dependencies
README.md                 Project guide
```

## Setup and run on Windows

1. Install Python 3.12 and open this project folder in VS Code.
2. Select **Terminal → New Terminal**.
3. Create a virtual environment and install dependencies:

   ```powershell
   py -3.12 -m venv .venv
   & ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
   ```

   If `.venv` already exists, skip the first command.
4. Start the app:

   ```powershell
   & ".\.venv\Scripts\python.exe" -m streamlit run app.py
   ```

5. Open the local URL printed in the terminal, usually
   `http://localhost:8501`. Keep the terminal running while you use the app;
   press **Ctrl+C** there to stop it.

If Streamlit asks for an email on first launch, leave it blank and press Enter.

## Use the app

1. Choose **Documents**, **HR data**, or **Both**.
2. In document mode, upload a PDF with selectable text. Scanned image-only
   PDFs need OCR first.
3. In HR mode, choose one of the listed summaries.
4. Enter a question. The app displays matching PDF passages and/or the chosen
   HR table and chart.
5. Without Groq configured, those results are shown as evidence. Groq is
   optional and is only used to write the answer.

## Optional AI answers with Groq

The app works locally without Groq. To enable AI-written answers:

1. Create an account at [console.groq.com](https://console.groq.com/) and
   create an API key.
2. Copy `.env.example` to `.env`:

   ```powershell
   Copy-Item .env.example .env
   ```
3. Open `.env` and set `GROQ_API_KEY` to your key. You can also set
   `GROQ_MODEL` to a model available to your account.
4. Restart Streamlit.

When enabled, the question and retrieved evidence are sent to Groq. Do not
send sensitive HR documents unless your organization's policies permit it.
Never commit `.env` or share your API key. Groq model availability, quotas,
and pricing can change; check your account's current terms and limits.

## Database

MySQL is **not required or integrated** in this version. HR summaries use the
included CSV through Pandas, so no database setup is needed.

## Tests

Run the helper-function tests from the project folder:

```powershell
& ".\.venv\Scripts\python.exe" -m pytest
```

## Privacy and limitations

- The bundled employee data is fictional.
- PDF search requires selectable text; scanned pages without OCR are not
  searchable.
- PDF matching is based on word similarity and may return irrelevant passages.
- Uploaded files are processed in memory by the app and are not intentionally
  saved to disk.
- If Groq is enabled, the question and retrieved evidence are sent to that
  external service.
- Do not use this demo to make employment decisions.
