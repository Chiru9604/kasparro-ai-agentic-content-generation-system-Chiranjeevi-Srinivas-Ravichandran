from typing import Dict
from ..models import Product, PriceComparisonResult

import re
from decimal import Decimal, InvalidOperation


def _bump_percentage(conc: str) -> str:
    """Increase numeric percentage by 2 (e.g. "10% Vitamin C" -> "12% Vitamin C")."""
    match = re.match(r"(\d+(?:\.\d+)?)%(.+)", conc.strip())
    if not match:
        return conc  # fallback – leave unchanged if format unexpected
    value, rest = match.groups()
    try:
        new_val = Decimal(value) + 2
    except InvalidOperation:
        return conc
    # Remove any trailing zeros like 12.0 -> 12
    new_val_str = (new_val.normalize() if new_val % 1 != 0 else int(new_val)).__str__()
    return f"{new_val_str}%{rest}"


def _adjust_price(price: str) -> str:
    """Add 15% to the numeric component of the price, preserving currency symbol."""
    match = re.match(r"([^\d]*)([\d,\.]+)(.*)", price.strip())
    if not match:
        return price
    prefix, num, suffix = match.groups()
    num_clean = num.replace(",", "")
    try:
        new_val = Decimal(num_clean) * Decimal("1.15")
    except InvalidOperation:
        return price
    # Format back without scientific notation, keep two decimals at most
    new_val_str = f"{new_val.quantize(Decimal('1.00'))}".rstrip("0").rstrip(".")
    return f"{prefix}{new_val_str}{suffix}"



def generate_product_b_from_product_a(product: Product) -> Product:
    """Create a fictional competitor Product B derived from Product A.

    Only deterministic transformations – no external data.
    """
    return Product(
        id=f"{product.id}-competitor",
        name=f"{product.name} Plus",
        concentration=_bump_percentage(product.concentration),
        skin_type=list({*product.skin_type, "Normal"}),  # ensure at least Normal skin type present
        key_ingredients=product.key_ingredients + ["Hyaluronic Acid"],
        benefits=list({*product.benefits, "Smooth texture"}),
        how_to_use=product.how_to_use,
        side_effects=product.side_effects or "Possible mild irritation on very sensitive skin",
        price=_adjust_price(product.price),
    )


def _parse_price(p: str) -> Decimal | None:
    match = re.search(r"([\d,\.]+)", p)
    if not match:
        return None
    try:
        return Decimal(match.group(1).replace(",", ""))
    except InvalidOperation:
        return None


def compare_price(a: Product, b: Product) -> PriceComparisonResult:
    """Return structured price comparison with numeric diff if parseable."""

    price_a_num = _parse_price(a.price)
    price_b_num = _parse_price(b.price)

    if price_a_num is not None and price_b_num is not None:
        diff = price_b_num - price_a_num
        pct = (diff / price_a_num * 100).quantize(Decimal('1.0'))
        summary = (
            f"{b.name} is {abs(pct)}% {'more' if diff > 0 else 'less'} expensive than {a.name}."
        )
    else:
        summary = f"{a.name} is listed at {a.price}, while {b.name} is listed at {b.price}."

    return PriceComparisonResult(
        product_a_price=a.price,
        product_b_price=b.price,
        summary=summary,
    )

