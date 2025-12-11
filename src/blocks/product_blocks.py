from typing import Dict
from ..models import Product, UsageBlock, SafetyBlock, PricingBlock

import re

def _derive_frequency(how_to_use: str) -> str:
    text = how_to_use.lower()
    if "morning" in text and "night" in text:
        return "Twice daily (morning and night)"
    if "morning" in text:
        return "Daily morning use"
    if "night" in text or "evening" in text:
        return "Nightly use"
    return "Daily use"


def _build_routine_tips(how_to_use: str) -> list[str]:
    tips = ["Apply on clean, dry skin."]
    if "morning" in how_to_use.lower():
        tips.append("Follow with a broad-spectrum sunscreen.")
    return tips


def build_core_summary_block(product: Product) -> Dict:
    return {
        "headline": f"{product.name} with {product.concentration}",
        "tagline": f"Brightening serum designed for {' and '.join([s.lower() for s in product.skin_type])} skin types.",
        "key_benefits": product.benefits,
    }


def build_usage_block(product: Product) -> UsageBlock:
    return UsageBlock(
        how_to_use=product.how_to_use,
        recommended_frequency=_derive_frequency(product.how_to_use),
        routine_tips=_build_routine_tips(product.how_to_use),
    )


def build_safety_block(product: Product) -> SafetyBlock:
    return SafetyBlock(
        side_effects=product.side_effects,
        patch_test_recommended=True,
        not_for=["broken or severely irritated skin"],
    )


def build_pricing_block(product: Product) -> PricingBlock:
    return PricingBlock(
        price=product.price,
        currency="INR",
        price_segment="mid-range",
    )

