from src.agents.product_page_agent import ProductPageAgent
from src.models import Product, ProductPage
from tests.conftest import MockLLM

def test_product_page_agent_run(sample_product_dict):
    # Setup
    data = sample_product_dict.copy()
    name = data.pop("product_name")
    product = Product(id="test-id", name=name, **data)
    
    mock_response = {
        "short_description": "A great product.",
        "detailed_description": "This product is amazing for...",
    }
    
    llm = MockLLM(mock_response)
    agent = ProductPageAgent(llm)
    
    # Execute
    result = agent.run(product)
    
    # Verify
    assert isinstance(result, ProductPage)
    assert result.short_description == "A great product."
    assert result.detailed_description == "This product is amazing for..."
    assert result.product_id == product.id
    # Verify blocks are populated
    assert result.how_to_use_block is not None
    assert result.safety_block is not None
    assert result.pricing_block is not None
