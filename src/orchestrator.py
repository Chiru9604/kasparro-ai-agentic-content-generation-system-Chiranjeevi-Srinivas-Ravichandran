"""Pipeline Orchestrator using LangChain Runnable pipelines."""

from __future__ import annotations

import logging

import json
from pathlib import Path
from typing import Any, Dict
from pydantic import BaseModel

from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from .config import get_settings
from .llm_client import LLMClient
from .agents.product_parser_agent import ProductParserAgent
from .agents.question_generator_agent import QuestionGeneratorAgent
from .agents.faq_page_agent import FAQPageAgent
from .agents.product_page_agent import ProductPageAgent
from .agents.comparison_agent import ComparisonAgent

OUTPUT_DIR = Path("output")


def _dump_json(obj: Any, filename: str) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / filename
    def _default(o):
        if isinstance(o, BaseModel):
            return o.model_dump()
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    path.write_text(json.dumps(obj, default=_default, indent=2), encoding="utf-8")


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def build_pipeline() -> RunnableLambda:
    """Constructs the Runnable pipeline for the end-to-end flow."""

    settings = get_settings()
    llm = LLMClient()
    parser = ProductParserAgent(settings.input_path)
    q_agent = QuestionGeneratorAgent(llm)
    faq_agent = FAQPageAgent(llm)
    product_page_agent = ProductPageAgent(llm)
    comparison_agent = ComparisonAgent(llm)

    # Step 1: parse product -> {"product": product}
    parse_step: RunnableLambda = RunnableLambda(lambda _: {"product": parser.run()})

    # Step 2: generate questions -> add to dict
    def gen_questions(data: Dict[str, Any]):
        questions = q_agent.run(data["product"])
        data["questions"] = questions
        return data

    question_step: RunnableLambda = RunnableLambda(gen_questions)

    # Step 3: FAQ page
    def gen_faq(data: Dict[str, Any]):
        faq_page = faq_agent.run(data["product"], data["questions"])
        data["faq_page"] = faq_page
        return data

    faq_step: RunnableLambda = RunnableLambda(gen_faq)

    # Step 4: Product page
    def gen_product_page(data: Dict[str, Any]):
        product_page = product_page_agent.run(data["product"])
        data["product_page"] = product_page
        return data

    product_step: RunnableLambda = RunnableLambda(gen_product_page)

    # Step 5: Comparison page
    def gen_comparison_page(data: Dict[str, Any]):
        comparison_page = comparison_agent.run(data["product"])
        data["comparison_page"] = comparison_page
        return data

    comparison_step: RunnableLambda = RunnableLambda(gen_comparison_page)

    # Step 6: dump to disk (side-effects) & final output
    def dump_results(data: Dict[str, Any]):
        _dump_json(data["faq_page"], "faq.json")
        _dump_json(data["product_page"], "product_page.json")
        _dump_json(data["comparison_page"], "comparison_page.json")
        return data

    dump_step: RunnableLambda = RunnableLambda(dump_results)

    # Compose the pipeline
    pipeline: RunnableLambda = (
        RunnablePassthrough()
        | parse_step
        | question_step
        | faq_step
        | product_step
        | comparison_step
        | dump_step
    )

    return pipeline


def run_pipeline() -> None:
    """Entry point for executing the pipeline with global error handling."""

    logger = logging.getLogger(__name__)
    try:
        pipeline = build_pipeline()
        # Trigger execution; initial input is ignored by first step
        pipeline.invoke(None)
        logger.info("Pipeline executed successfully")
    except Exception as exc:
        logger.error("Pipeline failed with unhandled exception: %s", exc, exc_info=True)
        raise


if __name__ == "__main__":
    run_pipeline()

