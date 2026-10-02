"""PDF retrieval, HR summaries, and optional AI answers."""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


PROJECT_FOLDER = Path(__file__).parent
load_dotenv(PROJECT_FOLDER / ".env")


def load_employees():
    """Read the example employee records from the CSV file."""
    return pd.read_csv(PROJECT_FOLDER / "data" / "demo_employees.csv")


def extract_pdf_pages(uploaded_files):
    """Return the text and page number for every non-empty PDF page."""
    pages = []
    for uploaded_file in uploaded_files:
        uploaded_file.seek(0)
        reader = PdfReader(uploaded_file)
        for page_number, pdf_page in enumerate(reader.pages, start=1):
            text = (pdf_page.extract_text() or "").strip()
            if text:
                pages.append(
                    {
                        "source": uploaded_file.name,
                        "page": page_number,
                        "text": text,
                    }
                )
    return pages


def find_relevant_pages(pages, question, result_limit=3):
    """Find the PDF pages whose words best match the question."""
    if not pages or not question.strip():
        return []

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        page_vectors = vectorizer.fit_transform([page["text"] for page in pages])
        question_vector = vectorizer.transform([question])
    except ValueError:
        return []

    scores = cosine_similarity(question_vector, page_vectors).flatten()
    best_pages = scores.argsort()[::-1][:result_limit]
    return [
        (pages[index], float(scores[index]))
        for index in best_pages
        if scores[index] > 0
    ]


def get_hr_results(employees, analysis):
    """Create a small, understandable summary from the employee table."""
    if analysis == "Employees by department":
        results = employees.groupby("department").size().reset_index(name="employees")
        return results, "department", "employees"

    if analysis == "Attrition counts":
        results = employees.groupby("attrition").size().reset_index(name="employees")
        return results, "attrition", "employees"

    if analysis == "Average monthly income by department":
        results = (
            employees.groupby("department", as_index=False)["monthly_income"]
            .mean()
            .rename(columns={"monthly_income": "average_monthly_income"})
        )
        results["average_monthly_income"] = results[
            "average_monthly_income"
        ].round(2)
        return results, "department", "average_monthly_income"

    if analysis == "Overtime counts":
        results = employees.groupby("overtime").size().reset_index(name="employees")
        return results, "overtime", "employees"

    raise ValueError(f"Unknown HR summary: {analysis}")


def answer_from_evidence(question, evidence, api_key="", model=""):
    """Use Groq when configured; otherwise show a clear evidence-based reply."""
    api_key = (api_key or os.getenv("GROQ_API_KEY", "")).strip()
    if not api_key:
        return (
            "No AI key is configured. Review the matching PDF pages and HR "
            "summary above; these are the evidence for your question."
        )

    from groq import Groq

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer using only the evidence provided. Cite PDF source "
                    "and page when available. If evidence does not answer the "
                    "question, say so. Do not infer causation from HR statistics."
                ),
            },
            {
                "role": "user",
                "content": f"Question:\n{question}\n\nEvidence:\n"
                + "\n\n".join(evidence),
            },
        ],
        temperature=0.2,
    )
    answer = response.choices[0].message.content
    if not answer:
        raise RuntimeError("The AI service returned an empty answer.")
    return answer
