from typing import List
from ..models import Product, Question
from ..llm_client import LLMClient


class QuestionGeneratorAgent:
    """
    Agent 2:
    Generates >=15 user questions about the product, with categories.
    """

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(self, product: Product) -> List[Question]:
        system_prompt = """
You are QuestionGeneratorAgent.

You generate customer questions about a skincare product.
Use ONLY the provided fields. Do not invent new medical or scientific facts.

Return a JSON object with this shape:
{
  "questions": [
    { "question": string, "category": string }
  ]
}

Rules:
- Generate AT LEAST 15 distinct questions.
- Categories must be one of:
  "Usage", "Safety", "Benefits", "Ingredients", "Purchase".
- Questions must clearly relate to the product fields:
  name, concentration, skin_type, key_ingredients, benefits, how_to_use, side_effects, price.

Output ONLY valid JSON. No explanation, no markdown.
"""

        user_prompt = f"""
Product data:
- Name: {product.name}
- Concentration: {product.concentration}
- Skin type: {product.skin_type}
- Key ingredients: {product.key_ingredients}
- Benefits: {product.benefits}
- How to use: {product.how_to_use}
- Side effects: {product.side_effects}
- Price: {product.price}
"""

        data = self.llm.call_and_parse_json(system_prompt, user_prompt)

        questions: List[Question] = []
        for item in data.get("questions", []):
            questions.append(
                Question(
                    question=item["question"],
                    category=item["category"],
                )
            )
        return questions

