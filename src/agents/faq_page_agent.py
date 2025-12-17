from ..config import get_settings
from typing import List
from ..models import Product, Question, FAQItem, FAQPage
from .base_llm_agent import BaseLLMAgent
from ..prompts import get_faq_page_prompts


class FAQPageAgent(BaseLLMAgent):
    """
    Agent 3:
    Builds an FAQ page from the product data and generated questions.
    """

    def run(
        self,
        product: Product,
        questions: List[Question],
        max_questions: int | None = None,
    ) -> FAQPage:
        # Instead of manually filtering in Python, we pass all questions (or a reasonable subset)
        # to the LLM and ask it to select the most relevant ones.
        
        # We still cap the input to avoid context window explosion if there are hundreds of questions,
        # but we don't do complex logic.
        
        questions_payload = [q.model_dump() for q in questions]

        system_prompt, user_prompt = get_faq_page_prompts(product, questions_payload)

        from ..schemas import FAQPageSchema
        
        data = self._j(system_prompt, user_prompt, schema=FAQPageSchema)

        faq_items: List[FAQItem] = []
        for q in data["questions"]:
            faq_items.append(
                FAQItem(
                    question=q["question"],
                    answer=q["answer"],
                    category=q["category"],
                )
            )

        return FAQPage(
            product_id=product.id,
            title=data["title"],
            intro=data["intro"],
            questions=faq_items,
        )

