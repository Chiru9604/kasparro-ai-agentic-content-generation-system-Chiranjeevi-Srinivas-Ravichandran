from pydantic import ValidationError

from src.schemas import FAQPageSchema, QuestionSchema, QuestionListSchema


def _generate_questions(n: int):
    return [
        {
            "question": f"Q{i}?",
            "category": "Usage",
        }
        for i in range(n)
    ]


def test_faq_page_schema_min_items_pass():
    data = {
        "title": "FAQ",
        "intro": "intro",
        "questions": [
            {
                "question": f"Question {i}",
                "answer": "Answer",
                "category": "General",
            }
            for i in range(15)
        ],
    }
    page = FAQPageSchema(**data)
    assert len(page.questions) == 15


def test_faq_page_schema_min_items_fail():
    data = {
        "title": "FAQ",
        "intro": "intro",
        "questions": [
            {
                "question": "Q1",
                "answer": "A1",
                "category": "General",
            }
        ],
    }
    try:
        FAQPageSchema(**data)  # should raise
    except ValidationError:
        return
    assert False, "ValidationError not raised for <15 FAQs"


def test_question_list_schema():
    data = {"questions": _generate_questions(15)}
    ql = QuestionListSchema(**data)
    assert len(ql.questions) == 15