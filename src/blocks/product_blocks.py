from typing import Dict
from ..models import Product


def build_core_summary_block(product: Product) -> Dict:
    return {
        "headline": f"{product.name} with {product.concentration}",
        "tagline": "Brightening serum designed for oily and combination skin.",
        "key_benefits": product.benefits,
    }


def build_usage_block(product: Product) -> Dict:
    return {
        "how_to_use": product.how_to_use,
        "recommended_frequency": "Daily morning use",
        "routine_tips": [
            "Apply on clean, dry skin.",
            "Follow with a broad-spectrum sunscreen.",
        ],
    }


def build_safety_block(product: Product) -> Dict:
    return {
        "side_effects": product.side_effects,
        "patch_test_recommended": True,
        "not_for": ["broken or severely irritated skin"],
    }


def build_pricing_block(product: Product) -> Dict:
    return {
        "price": product.price,
        "currency": "INR",
        "price_segment": "mid-range",
    }

