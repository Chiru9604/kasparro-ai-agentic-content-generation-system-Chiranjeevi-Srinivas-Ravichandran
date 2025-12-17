from typing import TypedDict, List, Optional, Annotated
from .models import Product, FAQPage, ProductPage, ComparisonPage, FeedbackReport

class AgentState(TypedDict):
    """
    The state of the agentic graph.
    This shared state is passed between nodes (agents).
    """
    product: Optional[Product]
    questions: Optional[List[str]]
    faq_page: Optional[FAQPage]
    product_page: Optional[ProductPage]
    comparison_page: Optional[ComparisonPage]
    feedback_report: Optional[FeedbackReport]
    metrics: dict
    
    # Operational flags / counters for loops
    question_retries: int
