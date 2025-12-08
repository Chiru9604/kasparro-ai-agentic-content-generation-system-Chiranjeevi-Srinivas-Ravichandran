from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Product:
    id: str
    name: str
    concentration: str
    skin_type: List[str]
    key_ingredients: List[str]
    benefits: List[str]
    how_to_use: str
    side_effects: str
    price: str


@dataclass
class Question:
    """Generated user question with a category."""
    question: str
    category: str


@dataclass
class FAQItem:
    """Question + answer for the final FAQ page."""
    question: str
    answer: str
    category: str


@dataclass
class FAQPage:
    product_id: str
    title: str
    intro: str
    questions: List[FAQItem]


@dataclass
class ProductPage:
    product_id: str
    name: str
    short_description: str
    detailed_description: str
    skin_type: List[str]
    key_ingredients: List[str]
    benefits: List[str]
    how_to_use_block: Dict[str, Any]
    safety_block: Dict[str, Any]
    pricing_block: Dict[str, Any]


@dataclass
class ComparisonDimension:
    dimension: str
    product_a: Any
    product_b: Any
    summary: str


@dataclass
class ComparisonPage:
    product_a: Dict[str, Any]
    product_b: Dict[str, Any]
    comparison_dimensions: List[ComparisonDimension]

