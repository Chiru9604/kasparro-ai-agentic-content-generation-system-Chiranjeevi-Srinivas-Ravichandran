from typing import List
from ..models import Product, Question
from .base_llm_agent import BaseLLMAgent
from ..prompts import get_question_gen_prompts


class QuestionGeneratorAgent(BaseLLMAgent):
    """
    Agent 2:
    Generates >=15 user questions about the product, with categories.
    """

    
    def run(self, product: Product) -> List[Question]:
        system_prompt, user_prompt = get_question_gen_prompts(product)

        from ..schemas import QuestionListSchema
        
        data = self._j(system_prompt, user_prompt, schema=QuestionListSchema)

        questions: List[Question] = []
        for item in data.get("questions", []):
            questions.append(
                Question(
                    question=item["question"],
                    category=item["category"],
                )
            )
        return questions

