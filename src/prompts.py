import json
from typing import Any, Dict, List
from pydantic import BaseModel
from .models import Product, UsageBlock, SafetyBlock, PricingBlock, Question, FAQPage, ProductPage, ComparisonPage

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

COMPETITOR_GEN_SYSTEM = """
You are a Product Strategist.
Create a REALISTIC competitor product profile (Product B) based on the input Product A.
Product B should be similar but slightly different to allow for interesting comparison.
For example, if Product A is expensive, make Product B cheaper but with lower concentration.
Return a valid Product JSON object.
"""

def get_competitor_gen_prompts(product_a: Product) -> tuple[str, str]:
    user_prompt = f"""
    Create a competitor for this product:
    {_to_json(product_a)}
    """
    return COMPETITOR_GEN_SYSTEM, user_prompt


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
- "price"

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


# --- Feedback / Quality Audit ---

FEEDBACK_SYSTEM = """
You are the Quality Assurance Editor (FeedbackAgent).

Your goal is to audit the generated content for quality, consistency, and safety.
Compare the generated outputs (FAQ, Product Page, Comparison) against the SOURCE Product Data.

Return JSON:
{
  "overall_score": int,    // 1-10
  "coherence_score": int,  // 1-10 (flow, tone, professionalism)
  "accuracy_score": int,   // 1-10 (adherence to source data)
  "issues": [string],      // List of specific hallucinations or errors found
  "summary": string        // 1 paragraph executive summary
}

Rules:
1. HALLUCINATION CHECK: If the output mentions ingredients or benefits NOT in the source, flag it as a major issue.
2. PRICE CHECK: Ensure prices mentioned in outputs match the source.
3. TONE CHECK: Content should be professional, helpful, and compliant (no "cure" claims).
4. Be strict but fair.

Output ONLY valid JSON.
"""

def get_feedback_prompts(
    product: Product,
    faq_page: FAQPage,
    product_page: ProductPage,
    comparison_page: ComparisonPage
) -> tuple[str, str]:
    user_prompt = f"""
SOURCE DATA (Truth):
{_to_json(product)}

GENERATED FAQ PAGE:
{_to_json(faq_page)}

GENERATED PRODUCT PAGE:
{_to_json(product_page)}

GENERATED COMPARISON PAGE:
{_to_json(comparison_page)}
"""
    return FEEDBACK_SYSTEM, user_prompt
