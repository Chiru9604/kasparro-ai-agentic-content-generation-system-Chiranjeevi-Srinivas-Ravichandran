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
        env_limit = get_settings().faq_max_questions
        question_limit = max(max_questions or env_limit, 15)

        if len(questions) < question_limit:
            raise ValueError(
                f"FAQPageAgent requires at least {question_limit} candidate questions, "
                f"but only {len(questions)} were supplied."
            )

        # Balanced selection strategy: Group by category and round-robin select
        from collections import defaultdict
        by_category = defaultdict(list)
        for q in questions:
            by_category[q.category].append(q)
        
        selected = []
        categories = list(by_category.keys())
        while len(selected) < question_limit and categories:
            for cat in list(categories):
                if by_category[cat]:
                    selected.append(by_category[cat].pop(0))
                    if len(selected) >= question_limit:
                        break
                else:
                    categories.remove(cat)
        
        questions_payload = [q.model_dump() for q in selected]

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

