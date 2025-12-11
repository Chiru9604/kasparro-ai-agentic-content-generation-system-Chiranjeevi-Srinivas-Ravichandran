from __future__ import annotations

import json
from pathlib import Path

from src.agents.product_parser_agent import ProductParserAgent
from src.models import Product


def test_product_parser_agent(tmp_path, sample_product_dict):
    """ProductParserAgent should read JSON and return a populated Product."""

    # Arrange – write sample product JSON to a temporary file
    input_path = tmp_path / "product_input.json"
    input_path.write_text(json.dumps(sample_product_dict, ensure_ascii=False))

    agent = ProductParserAgent(str(input_path))

    # Act
    product: Product = agent.run()

    # Assert – basic field mapping
    assert product.name == sample_product_dict["product_name"]
    assert product.concentration == "10%"
    assert "oily" in product.skin_type
    assert product.price == "$25"
    assert product.id == "brightglow-serum"
