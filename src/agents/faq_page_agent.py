import json
from typing import List
from ..models import Product, Question, FAQItem, FAQPage
from ..llm_client import LLMClient


class FAQPageAgent:
    """
    Agent 3:
    Builds an FAQ page from the product data and generated questions.
    """

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(self, product: Product, questions: List[Question]) -> FAQPage:
        # Use first 10 questions (at least 5 are required)
        selected = questions[:10]

        system_prompt = """
You are FAQPageAgent.

You create an FAQ page for a skincare product.
Use ONLY the provided product data and questions.
Do not invent new ingredients or medical/clinical claims.

Return JSON with this shape:
{
  "title": string,
  "intro": string,
  "questions": [
    { "question": string, "answer": string, "category": string }
  ]
}

Rules:
- Use AT LEAST 5 questions from the provided list.
- Answers must rely ONLY on:
  name, concentration, skin_type, key_ingredients, benefits, how_to_use, side_effects, price.
- You can rephrase and clarify, but do not add new scientific claims.

Output ONLY valid JSON.
"""

        questions_payload = [
            {"question": q.question, "category": q.category} for q in selected
        ]

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

Candidate questions (JSON):
{json.dumps(questions_payload, ensure_ascii=False, indent=2)}
"""

        data = self.llm.call_and_parse_json(system_prompt, user_prompt)

        faq_items: List[FAQItem] = []
        for q in data["questions"]:
            faq_items.append(
                FAQItem(
                    question=q["question"],
                    answer=q["answer"],
                    category=q["category"],
                )
            )

        return FAQPage(
            product_id=product.id,
            title=data["title"],
            intro=data["intro"],
            questions=faq_items,
        )

