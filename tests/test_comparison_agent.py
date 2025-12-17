from src.agents.comparison_agent import ComparisonAgent
from src.models import Product, ComparisonPage
from tests.conftest import MockLLM
import json

class SequentialMockLLM(MockLLM):
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0

    def call_and_parse_json(self, system_prompt: str, user_prompt: str, schema=None):
        resp = self.responses[self.call_count]
        self.call_count += 1
        return resp

def test_comparison_agent_run(sample_product_dict):
    # Setup
    data = sample_product_dict.copy()
    name = data.pop("product_name")
    product_a = Product(id="prod-a", name=name, **data)
    
    # Response 1: Generated Competitor Product
    competitor_response = {
        "id": "comp-b",
        "name": "Competitor B",
        "concentration": "10%",
        "skin_type": ["dry"],
        "key_ingredients": ["water"],
        "benefits": ["hydration"],
        "how_to_use": "Apply daily.",
        "side_effects": "None",
        "price": "$30"
    }

    # Response 2: Comparison Page
    comparison_response = {
        "comparison_dimensions": [
            {
                "dimension": "ingredients",
                "product_a": "Ing A",
                "product_b": "Ing B",
                "summary": "A is better"
            },
            {
                "dimension": "skin_type",
                "product_a": "Oily",
                "product_b": "Dry",
                "summary": "Different"
            },
            {
                "dimension": "usage",
                "product_a": "Daily",
                "product_b": "Weekly",
                "summary": "Usage differs"
            },
            {
                "dimension": "price",
                "product_a": "$25",
                "product_b": "$30",
                "summary": "B is cheaper"
            }
        ]
    }
    
    llm = SequentialMockLLM([competitor_response, comparison_response])
    agent = ComparisonAgent(llm)
    
    # Execute
    result = agent.run(product_a)
    
    # Verify
    assert isinstance(result, ComparisonPage)
    assert len(result.comparison_dimensions) == 4
    
    # Check Price dimension
    price_dim = result.comparison_dimensions[3]
    assert price_dim.dimension == "price"
    assert price_dim.product_b == "$30"
    
    assert result.product_a == product_a
    assert result.product_b is not None
    assert result.product_b.name == "Competitor B"

