import json
from pathlib import Path

from .llm_client import LLMClient
from .agents.product_parser_agent import ProductParserAgent
from .agents.question_generator_agent import QuestionGeneratorAgent
from .agents.faq_page_agent import FAQPageAgent
from .agents.product_page_agent import ProductPageAgent
from .agents.comparison_agent import ComparisonAgent


def run_pipeline():
    input_path = "input/product_input.json"
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    llm = LLMClient()

    # 1. Parse product
    parser = ProductParserAgent(input_path)
    product = parser.run()

    # 2. Generate questions
    q_agent = QuestionGeneratorAgent(llm)
    questions = q_agent.run(product)

    # 3. FAQ page
    faq_agent = FAQPageAgent(llm)
    faq_page = faq_agent.run(product, questions)

    # 4. Product page
    product_page_agent = ProductPageAgent(llm)
    product_page = product_page_agent.run(product)

    # 5. Comparison page
    comparison_agent = ComparisonAgent(llm)
    comparison_page = comparison_agent.run(product)

    def dump(obj, path: Path):
        path.write_text(
            json.dumps(obj, default=lambda o: o.__dict__, indent=2),
            encoding="utf-8",
        )

    dump(faq_page, output_dir / "faq.json")
    dump(product_page, output_dir / "product_page.json")
    dump(comparison_page, output_dir / "comparison_page.json")


if __name__ == "__main__":
    run_pipeline()

