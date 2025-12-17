import pytest
import os
from src.models import Product
from src.agents.question_generator_agent import QuestionGeneratorAgent
from src.agents.faq_page_agent import FAQPageAgent
from src.llm_client import LLMClient

# Skip this test if no API key is present (to avoid CI failures)
@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="GROQ_API_KEY not set")
def test_real_llm_question_and_faq_flow():
    """
    Integration test using the REAL LLM.
    Verifies that prompts are effective and response schemas are valid.
    """
    print("\n[Integration] Connecting to Real LLM...")
    llm = LLMClient()
    
    # 1. Setup Input
    product = Product(
        id="test-serum",
        name="Test Glow Serum",
        concentration="5% Niacinamide",
        skin_type=["Oily", "Sensitive"],
        key_ingredients=["Niacinamide", "Zinc"],
        benefits=["Oil control", "Soothing"],
        how_to_use="Apply morning and night.",
        side_effects="None known.",
        price="$25"
    )

    # 2. Test Question Generator (Real Call)
    print("[Integration] Running QuestionGeneratorAgent...")
    q_agent = QuestionGeneratorAgent(llm)
    questions = q_agent.run(product)
    
    assert len(questions) >= 15, "LLM failed to generate requested 15 questions"
    print(f"✅ Generated {len(questions)} questions.")

    # 3. Test FAQ Page Generator (Real Call)
    print("[Integration] Running FAQPageAgent...")
    f_agent = FAQPageAgent(llm)
    faq_page = f_agent.run(product, questions)
    
    assert faq_page.title, "FAQ Page missing title"
    assert len(faq_page.questions) >= 5, "FAQ Page has too few questions"
    print(f"✅ Generated FAQ Page with title: {faq_page.title}")

    print("\nSUCCESS: Real LLM integration test passed!")
