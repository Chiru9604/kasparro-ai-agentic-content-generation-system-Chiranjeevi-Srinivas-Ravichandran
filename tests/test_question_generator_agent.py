from __future__ import annotations

from typing import List

from src.agents.question_generator_agent import QuestionGeneratorAgent
from src.models import Question, Product
from tests.conftest import MockLLM


MOCK_RESPONSE = {
    "questions": [
        {"question": f"Question {i}", "category": "Benefits"} for i in range(1, 18)
    ]
}


def make_product() -> Product:
    return Product(
        id="sample",
        name="BrightGlow Serum",
        concentration="10%",
        skin_type=["oily"],
        key_ingredients=["niacinamide"],
        benefits=["brightening"],
        how_to_use="Apply nightly.",
        side_effects="None",
        price="$25",
    )


def test_question_generator_agent_returns_minimum_questions():
    # Arrange
    mock_llm = MockLLM(MOCK_RESPONSE)
    agent = QuestionGeneratorAgent(mock_llm)

    # Act
    questions: List[Question] = agent.run(make_product())

    # Assert
    assert len(questions) >= 15
    for q in questions:
        assert q.category in {"Usage", "Safety", "Benefits", "Ingredients", "Purchase", "Benefits"}
