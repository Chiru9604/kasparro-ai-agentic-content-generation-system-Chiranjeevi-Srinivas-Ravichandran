import json
from ..models import Product, ProductPage
from ..blocks.product_blocks import (
    build_core_summary_block,
    build_usage_block,
    build_safety_block,
    build_pricing_block,
)
from ..llm_client import LLMClient


class ProductPageAgent:
    """
    Agent 4:
    Builds a structured product page using logic blocks and LLM-generated descriptions.
    """

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(self, product: Product) -> ProductPage:
        core = build_core_summary_block(product)
        usage = build_usage_block(product)
        safety = build_safety_block(product)
        pricing = build_pricing_block(product)

        system_prompt = """
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

        user_prompt = f"""
Product (JSON):
{json.dumps(product.__dict__, ensure_ascii=False, indent=2)}

Core summary block:
{json.dumps(core, ensure_ascii=False, indent=2)}

Usage block:
{json.dumps(usage, ensure_ascii=False, indent=2)}

Safety block:
{json.dumps(safety, ensure_ascii=False, indent=2)}

Pricing block:
{json.dumps(pricing, ensure_ascii=False, indent=2)}
"""

        data = self.llm.call_and_parse_json(system_prompt, user_prompt)

        return ProductPage(
            product_id=product.id,
            name=product.name,
            short_description=data["short_description"],
            detailed_description=data["detailed_description"],
            skin_type=product.skin_type,
            key_ingredients=product.key_ingredients,
            benefits=product.benefits,
            how_to_use_block=usage,
            safety_block=safety,
            pricing_block=pricing,
        )

