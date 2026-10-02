"""Streamlit interface for PDF search and sample HR analytics."""

import os

import streamlit as st
from groq import GroqError
from pypdf.errors import PdfReadError

from assistant import (
    answer_from_evidence,
    extract_pdf_pages,
    find_relevant_pages,
    get_hr_results,
    load_employees,
)


st.set_page_config(page_title="Multimodal RAG Assistant", page_icon="📚")
st.title("📚 Multimodal RAG Assistant")
st.write("Search PDF documents and explore structured HR data in one place.")

employees = load_employees()

mode = st.radio(
    "What should I search?",
    ["Documents", "HR data", "Both"],
    horizontal=True,
)

uploaded_files = st.file_uploader(
    "Upload text-based PDF documents",
    type=["pdf"],
    accept_multiple_files=True,
)

analysis = st.selectbox(
    "Choose an HR summary",
    [
        "Employees by department",
        "Attrition counts",
        "Average monthly income by department",
        "Overtime counts",
    ],
    disabled=mode == "Documents",
)

question = st.text_input("Ask a question")

if question:
    evidence = []
    hr_results = None

    if mode in {"Documents", "Both"}:
        if uploaded_files:
            try:
                pages = extract_pdf_pages(uploaded_files)
                matches = find_relevant_pages(pages, question)
            except (PdfReadError, ValueError) as error:
                st.error(f"Could not read a PDF: {error}")
                matches = []

            if matches:
                st.subheader("Relevant document pages")
                for page, score in matches:
                    st.markdown(f"**{page['source']} — page {page['page']}**")
                    st.caption(f"Text similarity: {score:.2f}")
                    st.write(page["text"])
                    evidence.append(
                        f"Source: {page['source']}, page {page['page']}\n"
                        f"{page['text']}"
                    )
            else:
                st.info("No matching PDF text was found.")
        else:
            st.info("Upload a PDF to search documents.")

    if mode in {"HR data", "Both"}:
        hr_results, chart_x, chart_y = get_hr_results(employees, analysis)
        st.subheader(analysis)
        st.dataframe(hr_results, hide_index=True, width="stretch")
        st.bar_chart(hr_results, x=chart_x, y=chart_y)
        evidence.append(f"HR data summary ({analysis}):\n{hr_results.to_string(index=False)}")

    if evidence:
        st.subheader("Answer")
        try:
            api_key = st.secrets.get("GROQ_API_KEY", "")
            model = st.secrets.get("GROQ_MODEL", "")
        except FileNotFoundError:
            api_key = ""
            model = ""

        api_key = api_key or os.getenv("GROQ_API_KEY", "")
        model = model or os.getenv("GROQ_MODEL", "")
        try:
            st.write(answer_from_evidence(question, evidence, api_key, model))
        except GroqError as error:
            st.error(f"AI answer failed: {error}")

st.caption(
    "The included employee data is synthetic. Uploaded PDFs are processed "
    "in memory and are not saved by this app."
)
