from typing import Dict
from ..models import Product


def generate_product_b_from_product_a(product: Product) -> Product:
    """
    Create a fictional competitor product B based on product A.
    No external data, just small variations.
    """
    return Product(
        id="radiantshield-vitamin-c-niacinamide-serum",
        name="RadiantShield Vitamin C + Niacinamide Serum",
        concentration="12% Vitamin C",
        skin_type=["Normal", "Combination"],
        key_ingredients=["Vitamin C", "Niacinamide", "Hyaluronic Acid"],
        benefits=["Brightening", "Smooth texture"],
        how_to_use=product.how_to_use,
        side_effects="Possible mild irritation on very sensitive skin",
        price="₹799",
    )


def compare_price(a: Product, b: Product) -> Dict:
    return {
        "product_a_price": a.price,
        "product_b_price": b.price,
        "summary": f"{a.name} is listed at {a.price}, while {b.name} is listed at {b.price}.",
    }

