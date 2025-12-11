import json
from typing import Any, Dict, List
from pydantic import BaseModel
from .models import Product, UsageBlock, SafetyBlock, PricingBlock, Question

def _to_json(obj: Any) -> str:
    if isinstance(obj, BaseModel):
        return obj.model_dump_json(indent=2)
    return json.dumps(obj, ensure_ascii=False, indent=2)


# --- Question Generator ---

QUESTION_GEN_SYSTEM = """
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

def get_question_gen_prompts(product: Product) -> tuple[str, str]:
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
    return QUESTION_GEN_SYSTEM, user_prompt


# --- FAQ Page ---

FAQ_PAGE_SYSTEM = """
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
- Use AT LEAST 15 questions from the provided list.
- Answers must rely ONLY on:
  name, concentration, skin_type, key_ingredients, benefits, how_to_use, side_effects, price.
- You can rephrase and clarify, but do not add new scientific claims.

Output ONLY valid JSON. No markdown, no commentary.
"""

def get_faq_page_prompts(product: Product, questions: List[Dict[str, Any]]) -> tuple[str, str]:
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
{_to_json(questions)}
"""
    return FAQ_PAGE_SYSTEM, user_prompt


# --- Product Page ---

PRODUCT_PAGE_SYSTEM = """
You are ProductPageAgent.

You create product page copy from structured blocks.
Use ONLY the provided product and block data.

Return JSON with this shape:
{
  "short_description": string,
  "detailed_description": string
}

Rules:
- short_description: 1–2 concise sentences summarizing what the serum is and who it is for.
- detailed_description: 3–6 sentences elaborating on concentration, skin type,
  key ingredients, benefits, and how to use.
- Do NOT add new medical or clinical claims beyond "brightening" and "fades dark spots".

Output ONLY valid JSON.
"""

def get_product_page_prompts(
    product: Product, 
    core: Dict, 
    usage: UsageBlock, 
    safety: SafetyBlock, 
    pricing: PricingBlock
) -> tuple[str, str]:
    user_prompt = f"""
Product (JSON):
{_to_json(product)}

Core summary block:
{_to_json(core)}

Usage block:
{_to_json(usage)}

Safety block:
{_to_json(safety)}

Pricing block:
{_to_json(pricing)}
"""
    return PRODUCT_PAGE_SYSTEM, user_prompt


# --- Comparison ---

COMPARISON_SYSTEM = """
You are ComparisonAgent.

You compare two skincare serums, Product A and Product B.
Use ONLY the provided product objects.

Return JSON:
{
  "comparison_dimensions": [
    {
      "dimension": string,
      "product_a": any,
      "product_b": any,
      "summary": string
    }
  ]
}

Use these dimensions:
- "ingredients"
- "benefits"
- "skin_type"
- "usage"

For each dimension:
- product_a field: relevant data from Product A
- product_b field: relevant data from Product B
- summary: 1–3 sentences comparing them plainly and fairly.

Do NOT add clinical claims or external research.

Output ONLY valid JSON.
"""

def get_comparison_prompts(product_a: Product, product_b: Product) -> tuple[str, str]:
    user_prompt = f"""
Product A (JSON):
{_to_json(product_a)}

Product B (JSON):
{_to_json(product_b)}
"""
    return COMPARISON_SYSTEM, user_prompt
