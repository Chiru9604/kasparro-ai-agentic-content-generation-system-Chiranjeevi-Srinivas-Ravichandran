import json
import re
from pathlib import Path
from ..models import Product


class ProductParserAgent:
    """
    Agent 1:
    Reads input/product_input.json and returns a normalized Product object.
    """

    def __init__(self, input_path: str):
        self.input_path = Path(input_path)

    def _slugify(self, name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    def run(self) -> Product:
        raw = json.loads(self.input_path.read_text(encoding="utf-8-sig"))
        product_id = self._slugify(raw["product_name"])

        return Product(
            id=product_id,
            name=raw["product_name"],
            concentration=raw["concentration"],
            skin_type=raw["skin_type"],
            key_ingredients=raw["key_ingredients"],
            benefits=raw["benefits"],
            how_to_use=raw["how_to_use"],
            side_effects=raw["side_effects"],
            price=raw["price"],
        )

