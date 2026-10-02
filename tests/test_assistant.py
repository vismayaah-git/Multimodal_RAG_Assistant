import pandas as pd

from assistant import (
    answer_from_evidence,
    find_relevant_pages,
    get_hr_results,
    load_employees,
)


def test_search_finds_page_about_salary():
    pages = [
        {"source": "policy.pdf", "page": 1, "text": "Annual salary review process"},
        {"source": "guide.pdf", "page": 2, "text": "Office parking and access"},
    ]

    matches = find_relevant_pages(pages, "salary review")

    assert matches[0][0]["source"] == "policy.pdf"


def test_search_returns_no_matches_for_unrelated_words():
    pages = [{"source": "policy.pdf", "page": 1, "text": "Annual salary review"}]

    assert find_relevant_pages(pages, "volcano eruption") == []


def test_sample_csv_and_department_summary():
    employees = load_employees()
    results, chart_x, chart_y = get_hr_results(
        employees, "Employees by department"
    )

    assert isinstance(results, pd.DataFrame)
    assert results[chart_y].sum() == 24
    assert chart_x == "department"


def test_offline_answer_explains_it_uses_evidence(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    answer = answer_from_evidence("How many employees?", ["There are 24 examples."])

    assert "No AI key is configured" in answer
