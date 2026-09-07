from resume_cli.mock import extract_with_mock, score_with_mock


RESUME = """Name: Alex Chen
Phone: +1 415 555 0123
Email: alex@example.com
City: Hangzhou
4 years of experience with TypeScript, React, Node.js, SQL and Docker.
2015 - 2019 | Example University | B.S. Computer Science"""


def test_mock_extracts_contact_and_skills() -> None:
    result = extract_with_mock(RESUME)
    assert result["email"] == "alex@example.com"
    assert {"TypeScript", "React", "Node.js"}.issubset(result["skills"])


def test_mock_score_is_bounded_and_deterministic() -> None:
    result = score_with_mock(
        RESUME, "Need TypeScript, React, Node.js, Docker and AWS experience."
    )
    assert 0 <= result["overall_score"] <= 100
    assert "Mock 评分" in result["comment"]


def test_mock_does_not_treat_dates_or_lowercase_go_as_skills() -> None:
    result = extract_with_mock(
        "2015 - 2019 | Example University | B.S. Computer Science\nI go to meet users."
    )
    assert result["phone"] == ""
    assert "Go" not in result["skills"]
