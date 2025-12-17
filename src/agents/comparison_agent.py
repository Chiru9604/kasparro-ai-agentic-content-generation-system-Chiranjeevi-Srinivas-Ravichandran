from typing import List
from ..models import Product, ComparisonDimension, ComparisonPage
from .base_llm_agent import BaseLLMAgent
from ..prompts import get_comparison_prompts, get_competitor_gen_prompts


class ComparisonAgent(BaseLLMAgent):
    """
    Agent 5:
    Creates a fictional Product B and compares A vs B across multiple dimensions.
    """

    def run(self, product_a: Product) -> ComparisonPage:
        # Step 1: Generate Competitor (Product B) via LLM
        sys_b, user_b = get_competitor_gen_prompts(product_a)
        product_b = self._j(sys_b, user_b, schema=Product)

        # Step 2: Compare A vs B
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

        return ComparisonPage(
            product_a=product_a,
            product_b=product_b,
            comparison_dimensions=dims,
        )

