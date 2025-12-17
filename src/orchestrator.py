"""Pipeline Orchestrator using LangGraph."""
from __future__ import annotations

import logging
import time
import json
from pathlib import Path
from typing import Any, Dict

from langgraph.graph import StateGraph, END
from pydantic import BaseModel

from .config import get_settings
from .llm_client import LLMClient
from .state import AgentState
from .agents.product_parser_agent import ProductParserAgent
from .agents.question_generator_agent import QuestionGeneratorAgent
from .agents.faq_page_agent import FAQPageAgent
from .agents.product_page_agent import ProductPageAgent
from .agents.comparison_agent import ComparisonAgent
from .agents.feedback_agent import FeedbackAgent

OUTPUT_DIR = Path("output")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def _dump_json(obj: Any, filename: str) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / filename
    def _default(o):
        if isinstance(o, BaseModel):
            return o.model_dump()
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    path.write_text(json.dumps(obj, default=_default, indent=2), encoding="utf-8")

# --- Nodes ---

def node_parse_product(state: AgentState) -> dict:
    settings = get_settings()
    parser = ProductParserAgent(settings.input_path)
    
    start = time.perf_counter()
    product = parser.run()
    duration = time.perf_counter() - start
    
    metrics = state.get("metrics", {})
    metrics["step_1_parsing_latency"] = round(duration, 4)
    
    return {"product": product, "metrics": metrics}

def node_generate_questions(state: AgentState) -> dict:
    llm = LLMClient()
    agent = QuestionGeneratorAgent(llm)
    
    start = time.perf_counter()
    questions = agent.run(state["product"])
    duration = time.perf_counter() - start
    
    metrics = state["metrics"]
    metrics["step_2_question_gen_latency"] = round(duration, 4)
    
    return {"questions": questions, "metrics": metrics}

def check_questions_quality(state: AgentState):
    """Conditional edge: Check if we have enough questions."""
    questions = state.get("questions", [])
    retry_count = state.get("metrics", {}).get("retry_count", 0)
    
    if len(questions) < 5 and retry_count < 3:
        logger.warning("Generated too few questions (%d). Routing back to generate_questions (Retry %d/3).", len(questions), retry_count + 1)
        # Update retry count in metrics
        if "metrics" not in state:
            state["metrics"] = {}
        state["metrics"]["retry_count"] = retry_count + 1
        return "retry"
        
    return "continue"

def node_generate_faq(state: AgentState) -> dict:
    llm = LLMClient()
    agent = FAQPageAgent(llm)
    
    start = time.perf_counter()
    faq_page = agent.run(state["product"], state["questions"])
    duration = time.perf_counter() - start
    
    metrics = state["metrics"]
    metrics["step_3_faq_gen_latency"] = round(duration, 4)
    
    return {"faq_page": faq_page, "metrics": metrics}

def node_generate_product_page(state: AgentState) -> dict:
    llm = LLMClient()
    agent = ProductPageAgent(llm)
    
    start = time.perf_counter()
    product_page = agent.run(state["product"])
    duration = time.perf_counter() - start
    
    metrics = state["metrics"]
    metrics["step_4_product_page_latency"] = round(duration, 4)
    
    return {"product_page": product_page, "metrics": metrics}

def node_generate_comparison(state: AgentState) -> dict:
    llm = LLMClient()
    agent = ComparisonAgent(llm)
    
    start = time.perf_counter()
    comparison_page = agent.run(state["product"])
    duration = time.perf_counter() - start
    
    metrics = state["metrics"]
    metrics["step_5_comparison_page_latency"] = round(duration, 4)
    
    return {"comparison_page": comparison_page, "metrics": metrics}

def node_feedback_audit(state: AgentState) -> dict:
    llm = LLMClient()
    agent = FeedbackAgent(llm)
    
    start = time.perf_counter()
    feedback = agent.run(
        state["product"],
        state["faq_page"],
        state["product_page"],
        state["comparison_page"]
    )
    duration = time.perf_counter() - start
    
    metrics = state["metrics"]
    metrics["step_6_feedback_agent_latency"] = round(duration, 4)
    
    return {"feedback_report": feedback, "metrics": metrics}

def node_dump_results(state: AgentState) -> dict:
    _dump_json(state["faq_page"], "faq.json")
    _dump_json(state["product_page"], "product_page.json")
    _dump_json(state["comparison_page"], "comparison_page.json")
    _dump_json(state["feedback_report"], "feedback_report.json")
    _dump_json(state["metrics"], "run_stats.json")
    return {}

# --- Graph Construction ---

def build_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("parse_product", node_parse_product)
    workflow.add_node("generate_questions", node_generate_questions)
    workflow.add_node("generate_faq", node_generate_faq)
    workflow.add_node("generate_product_page", node_generate_product_page)
    workflow.add_node("generate_comparison", node_generate_comparison)
    workflow.add_node("feedback_audit", node_feedback_audit)
    workflow.add_node("dump_results", node_dump_results)
    
    # Define edges
    workflow.set_entry_point("parse_product")
    
    workflow.add_edge("parse_product", "generate_questions")
    
    # Conditional edge for questions quality
    workflow.add_conditional_edges(
        "generate_questions",
        check_questions_quality,
        {
            "continue": "generate_faq",
            "retry": "generate_questions"
        }
    )
    
    # Parallelize Product Page and Comparison? 
    # For now, keep linear to match original flow, but Graph allows parallel.
    workflow.add_edge("generate_faq", "generate_product_page")
    workflow.add_edge("generate_product_page", "generate_comparison")
    workflow.add_edge("generate_comparison", "feedback_audit")
    workflow.add_edge("feedback_audit", "dump_results")
    workflow.add_edge("dump_results", END)
    
    return workflow.compile()

def run_pipeline() -> None:
    """Entry point for executing the pipeline with global error handling."""
    try:
        app = build_graph()
        # Initialize state
        initial_state = {"metrics": {}}
        app.invoke(initial_state)
        logger.info("Pipeline executed successfully via LangGraph")
    except Exception as exc:
        logger.error("Pipeline failed with unhandled exception: %s", exc, exc_info=True)
        raise

if __name__ == "__main__":
    run_pipeline()
