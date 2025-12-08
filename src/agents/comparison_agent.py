import json
from dataclasses import asdict
from typing import List
from ..models import Product, ComparisonDimension, ComparisonPage
from ..blocks.comparison_blocks import (
    generate_product_b_from_product_a,
    compare_price,
)
from ..llm_client import LLMClient


class ComparisonAgent:
    """
    Agent 5:
    Creates a fictional Product B and compares A vs B across multiple dimensions.
    """

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(self, product_a: Product) -> ComparisonPage:
        product_b = generate_product_b_from_product_a(product_a)

        system_prompt = """
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

        user_prompt = f"""
Product A (JSON):
{json.dumps(asdict(product_a), ensure_ascii=False, indent=2)}

Product B (JSON):
{json.dumps(asdict(product_b), ensure_ascii=False, indent=2)}
"""

        data = self.llm.call_and_parse_json(system_prompt, user_prompt)

        dims: List[ComparisonDimension] = []
        for item in data["comparison_dimensions"]:
            dims.append(
                ComparisonDimension(
                    dimension=item["dimension"],
                    product_a=item["product_a"],
                    product_b=item["product_b"],
                    summary=item["summary"],
                )
            )

        # Add price comparison dimension from pure Python logic
        price_data = compare_price(product_a, product_b)
        dims.append(
            ComparisonDimension(
                dimension="price",
                product_a=price_data["product_a_price"],
                product_b=price_data["product_b_price"],
                summary=price_data["summary"],
            )
        )

        return ComparisonPage(
            product_a={
                "id": product_a.id,
                "name": product_a.name,
                "price": product_a.price,
            },
            product_b={
                "id": product_b.id,
                "name": product_b.name,
                "price": product_b.price,
            },
            comparison_dimensions=dims,
        )

