from typing import List
from ..models import Product, ComparisonDimension, ComparisonPage
from ..blocks.comparison_blocks import (
    generate_product_b_from_product_a,
    compare_price,
)
from .base_llm_agent import BaseLLMAgent
from ..prompts import get_comparison_prompts


class ComparisonAgent(BaseLLMAgent):
    """
    Agent 5:
    Creates a fictional Product B and compares A vs B across multiple dimensions.
    """

    def run(self, product_a: Product) -> ComparisonPage:
        product_b = generate_product_b_from_product_a(product_a)

        system_prompt, user_prompt = get_comparison_prompts(product_a, product_b)

        from ..schemas import ComparisonPageSchema
        
        data = self._j(system_prompt, user_prompt, schema=ComparisonPageSchema)

        dims: List[ComparisonDimension] = []
        for item in data["comparison_dimensions"]:
            dims.append(
                ComparisonDimension(
                    dimension=item["dimension"],
                    product_a=str(item["product_a"]),
                    product_b=str(item["product_b"]),
                    summary=item["summary"],
                )
            )

        # Add price comparison dimension from pure Python logic
        price_data = compare_price(product_a, product_b)
        dims.append(
            ComparisonDimension(
                dimension="price",
                product_a=price_data.product_a_price,
                product_b=price_data.product_b_price,
                summary=price_data.summary,
            )
        )

        return ComparisonPage(
            product_a=product_a,
            product_b=product_b,
            comparison_dimensions=dims,
        )

