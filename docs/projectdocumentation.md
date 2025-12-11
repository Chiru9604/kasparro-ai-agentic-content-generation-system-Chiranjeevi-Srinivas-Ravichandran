# Project Documentation

## 1. Problem Statement

This project implements a **multi-agent content generation pipeline** for a skincare product as part of an Applied AI Engineer assignment.

The system:

- Starts from a **single structured product JSON** (`input/product_input.json`).
- Uses a chain of **specialized agents** powered by an LLM (via Groq API).
- Produces **three structured JSON outputs**:
  1. `faq.json` – FAQ page
  2. `product_page.json` – product detail page
  3. `comparison_page.json` – comparison page between Product A and a fictional Product B
- Uses **no external data sources**. All content is derived only from the provided product fields and a small amount of deterministic Python logic.

---

## 2. Overview

This project is an automated content generation pipeline powered by Large Language Models (LLMs) via the Groq API. It takes structured product data as input and generates:

1. **Product Pages**  
   Rich product descriptions including benefits, skin type, ingredients, usage, safety, and pricing.

2. **FAQ Pages**  
   Automatically generated user questions and answers organized by category.

3. **Comparison Pages**  
   A comparison between the input product (Product A) and a **synthetic competitor** (Product B) generated from A, including price, ingredients, benefits, skin type, and usage.

All final outputs are written as JSON files under the `output/` directory so they can be consumed by a web frontend or CMS.

---

## 3. Architecture

The project follows a **multi-agent architecture** orchestrated by a central pipeline.

### 3.1 Directory Structure

- `src/` – Core source code
  - `agents/` – Specialized agents for each step of the pipeline
  - `blocks/` – Reusable logic blocks for content structure
  - `models.py` – Pydantic models for all entities (Product, FAQ, ProductPage, Comparison, etc.)
  - `llm_client.py` – Wrapper around Groq’s LLM API
  - `orchestrator.py` – Main pipeline orchestration using LangChain Runnables
  - `config.py` – Centralized configuration via Pydantic Settings
  - `prompts.py` – Centralized prompt management
  - `schemas.py` – JSON schemas for LLM validation
- `tests/` – Unit and integration tests
- `input/` – Input files (e.g., `product_input.json`)
- `output/` – Generated JSON content (`faq.json`, `product_page.json`, `comparison_page.json`)
- `docs/` – Project documentation
- `main.py` – Entry point to run the full pipeline
- `requirements.txt` – Pinned project dependencies

---

## 4. Key Components

### 4.1 LLM Client (`src/llm_client.py`)

- Wraps the **Groq** API client.
- Uses configurable model and temperature via `src/config.py`.
- Exposes methods for chat completion and JSON parsing with error handling.
- Enforces **JSON-only responses** (via `response_format` and strict prompting).
- Uses `src/config.py` (Pydantic Settings) for robust configuration management.

---

### 4.2 Data Models (`src/models.py`)

The main Pydantic models are:

- `Product` – normalized product entity with:
  - `id` (slug from product name)
  - `name`, `concentration`, `skin_type`, `key_ingredients`
  - `benefits`, `how_to_use`, `side_effects`, `price`

- `Question` – a generated user question with a `category`.

- `FAQItem` / `FAQPage` – FAQ page structure:
  - `title`, `intro`
  - `questions: List[FAQItem]` where each item has `question`, `answer`, `category`.

- `ProductPage` – product page structure:
  - `short_description`, `detailed_description`
  - `skin_type`, `key_ingredients`, `benefits`
  - `how_to_use_block`, `safety_block`, `pricing_block` (Typed blocks)

- `ComparisonDimension` / `ComparisonPage` – comparison page between Product A and synthetic Product B.

These models are serialized to JSON via Pydantic's `model_dump()` method, ensuring type safety and correct formatting.

---

### 4.3 Reusable Logic Blocks (`src/blocks/`)

#### `product_blocks.py`

Provides pure Python functions that build reusable blocks for the product page:

- `build_core_summary_block(product)`  
  Returns headline, tagline, and key benefits.

- `build_usage_block(product)`  
  Returns how to use the serum, recommended frequency, and simple routine tips.

- `build_safety_block(product)`  
  Encodes side effects information, patch test recommendation, and basic “not for” cases.

- `build_pricing_block(product)`  
  Wraps pricing, currency, and a rough price segment label (e.g., mid-range).

These blocks are passed as context into the LLM so that the **ProductPageAgent** can generate consistent descriptions.

#### `comparison_blocks.py`

- `generate_product_b_from_product_a(product)`  
  Creates a **fictional Product B** derived from Product A (slightly different concentration, ingredients, skin type, and price). No external data or real brands are used.

- `compare_price(a, b)`  
  Adds a pure-Python price comparison dimension, summarizing the price difference between A and B.

---

## 5. Agents (`src/agents/`)

Each agent has a **single responsibility** and a `run(...)` method.

### 5.1 ProductParserAgent

**File:** `product_parser_agent.py`  
**Responsibility:** Input parsing

- Input: `input/product_input.json`
- Behavior:
  - Reads the JSON safely using `utf-8-sig` to handle BOM.
  - Normalizes keys into a `Product` dataclass.
  - Generates a slugified `id` from the product name.
- Output: `Product` instance

### 5.2 QuestionGeneratorAgent

**File:** `question_generator_agent.py`  
**Responsibility:** Question generation

- Input: `Product`
- Behavior:
  - Calls the LLM with a strict system prompt.
  - Generates **at least 15** distinct user questions.
  - Assigns each question a category from:
    - `"Usage"`, `"Safety"`, `"Benefits"`, `"Ingredients"`, `"Purchase"`.
- Output: `List[Question]`

### 5.3 FAQPageAgent

**File:** `faq_page_agent.py`  
**Responsibility:** FAQ page creation

- Inputs: `Product`, `List[Question]`
- Behavior:
  - Selects a subset of candidate questions (e.g., first 10).
  - Asks the LLM to generate:
    - A `title` and `intro` for the FAQ page.
    - An answer and category for each selected question.
  - Ensures answers only use:
    - `name`, `concentration`, `skin_type`, `key_ingredients`, `benefits`, `how_to_use`, `side_effects`, `price`.
- Output: `FAQPage` → serialized to `output/faq.json`

### 5.4 ProductPageAgent

**File:** `product_page_agent.py`  
**Responsibility:** Product page generation

- Input: `Product` + blocks from `product_blocks.py`
- Behavior:
  - Combines:
    - Core summary block
    - Usage block
    - Safety block
    - Pricing block
  - Asks the LLM to produce:
    - `short_description` (1–2 sentences)
    - `detailed_description` (3–6 sentences)
  - Restricts the LLM from inventing clinical claims beyond what the input says.
- Output: `ProductPage` → serialized to `output/product_page.json`

### 5.5 ComparisonAgent

**File:** `comparison_agent.py`  
**Responsibility:** Comparison page generation

- Input: Product A (`Product`)
- Behavior:
  - Uses `generate_product_b_from_product_a` to create a synthetic Product B.
  - Calls the LLM to compare A vs B across dimensions:
    - `"ingredients"`, `"benefits"`, `"skin_type"`, `"usage"`.
  - Adds a `"price"` comparison dimension using pure Python `compare_price`.
- Output: `ComparisonPage` → serialized to `output/comparison_page.json`

---

## 6. Orchestration (`src/orchestrator.py`)

The orchestrator coordinates the full pipeline:

1. Load product from `input/product_input.json` via `ProductParserAgent`.
2. Generate questions with `QuestionGeneratorAgent`.
3. Build FAQ page with `FAQPageAgent`.
4. Build product page with `ProductPageAgent`.
5. Build comparison page with `ComparisonAgent`.
6. Dump all dataclasses to JSON files in `output/`.

Entry point `main.py` simply calls:

```python
from src.orchestrator import run_pipeline

if __name__ == "__main__":
    run_pipeline()
