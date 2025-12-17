"""Pydantic models describing LLM response payloads."""
from __future__ import annotations

from typing import List, Literal
from pydantic import BaseModel, Field


class FAQItemSchema(BaseModel):
    question: str
    answer: str
    category: str


class QuestionSchema(BaseModel):
    question: str
    category: Literal["Usage", "Safety", "Benefits", "Ingredients", "Purchase"]


class QuestionListSchema(BaseModel):
    questions: List[QuestionSchema] = Field(..., min_length=15)


class ComparisonDimensionSchema(BaseModel):
    dimension: Literal["ingredients", "benefits", "skin_type", "usage", "price"]
    product_a: object
    product_b: object
    summary: str


class ComparisonPageSchema(BaseModel):
    comparison_dimensions: List[ComparisonDimensionSchema] = Field(..., min_length=4)


class ProductPageSchema(BaseModel):
    short_description: str
    detailed_description: str


class FAQPageSchema(BaseModel):
    title: str
    intro: str
    questions: List[FAQItemSchema] = Field(..., min_length=15)


class FeedbackReportSchema(BaseModel):
    overall_score: int = Field(..., description="Score from 1-10")
    coherence_score: int = Field(..., description="Score from 1-10 on flow and tone")
    accuracy_score: int = Field(..., description="Score from 1-10 on factual consistency with input")
    issues: List[str] = Field(..., description="List of specific inconsistencies or quality issues found")
    summary: str = Field(..., description="Executive summary of the content quality")
