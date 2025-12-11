from typing import List
from pydantic import BaseModel

class Product(BaseModel):
    id: str
    name: str
    concentration: str
    skin_type: List[str]
    key_ingredients: List[str]
    benefits: List[str]
    how_to_use: str
    side_effects: str
    price: str

class Question(BaseModel):
    """Generated user question with a category."""
    question: str
    category: str

class FAQItem(BaseModel):
    """Question + answer for the final FAQ page."""
    question: str
    answer: str
    category: str

class FAQPage(BaseModel):
    product_id: str
    title: str
    intro: str
    questions: List[FAQItem]

class UsageBlock(BaseModel):
    how_to_use: str
    recommended_frequency: str
    routine_tips: List[str]

class SafetyBlock(BaseModel):
    side_effects: str
    patch_test_recommended: bool
    not_for: List[str]

class PricingBlock(BaseModel):
    price: str
    currency: str
    price_segment: str

class ProductPage(BaseModel):
    product_id: str
    name: str
    short_description: str
    detailed_description: str
    skin_type: List[str]
    key_ingredients: List[str]
    benefits: List[str]
    how_to_use_block: UsageBlock
    safety_block: SafetyBlock
    pricing_block: PricingBlock

class ComparisonDimension(BaseModel):
    dimension: str
    product_a: str
    product_b: str
    summary: str

class PriceComparisonResult(BaseModel):
    product_a_price: str
    product_b_price: str
    summary: str

class ComparisonPage(BaseModel):
    product_a: Product
    product_b: Product
    comparison_dimensions: List[ComparisonDimension]
