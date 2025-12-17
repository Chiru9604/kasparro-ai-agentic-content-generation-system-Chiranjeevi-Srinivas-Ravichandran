from ..models import Product, FAQPage, ProductPage, ComparisonPage, FeedbackReport
from .base_llm_agent import BaseLLMAgent
from ..prompts import get_feedback_prompts


class FeedbackAgent(BaseLLMAgent):
    """
    Agent 6 (Optional):
    Audits the generated content against the source product to ensure quality and safety.
    """

    def run(
        self,
        product: Product,
        faq_page: FAQPage,
        product_page: ProductPage,
        comparison_page: ComparisonPage,
    ) -> FeedbackReport:
        system_prompt, user_prompt = get_feedback_prompts(
            product, faq_page, product_page, comparison_page
        )

        from ..schemas import FeedbackReportSchema
        
        data = self._j(system_prompt, user_prompt, schema=FeedbackReportSchema)

        return FeedbackReport(
            overall_score=data["overall_score"],
            coherence_score=data["coherence_score"],
            accuracy_score=data["accuracy_score"],
            issues=data["issues"],
            summary=data["summary"],
        )
