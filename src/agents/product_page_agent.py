from ..models import Product, ProductPage
from ..blocks.product_blocks import (
    build_core_summary_block,
    build_usage_block,
    build_safety_block,
    build_pricing_block,
)
from .base_llm_agent import BaseLLMAgent
from ..prompts import get_product_page_prompts


class ProductPageAgent(BaseLLMAgent):
    """
    Agent 4:
    Builds a structured product page using logic blocks and LLM-generated descriptions.
    """

    def run(self, product: Product) -> ProductPage:
        core = build_core_summary_block(product)
        usage = build_usage_block(product)
        safety = build_safety_block(product)
        pricing = build_pricing_block(product)

        system_prompt, user_prompt = get_product_page_prompts(product, core, usage, safety, pricing)

        from ..schemas import ProductPageSchema
        
        data = self._j(system_prompt, user_prompt, schema=ProductPageSchema)

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

