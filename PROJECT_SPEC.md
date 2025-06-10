# Bidding Estimator Chatbot – Technical Specification

## 1. Purpose
Build a conversational assistant that produces accurate, auditable cost estimates and professional proposals for Network, Electrical, Mixed, and Plumbing projects. The assistant must separate "fuzzy" natural-language understanding from deterministic business math.

## 2. Guiding Principles
1. Deterministic pricing formulas live **only** in code.
2. LLM handles **extraction & dialogue**, not arithmetic.
3. All I/O is strongly typed via Pydantic models.
4. Every module is small, documented, and unit-testable.
5. Validation → retry loop guarantees perfect JSON before pricing.

## 3. High-Level Workflow
```text
User NL → LLM (extract) → JSON → pricing_engine (math) → formatter (MD/PDF) → Chat
```

## 4. Core Modules
| Module | Responsibility | Key Tech |
| ------ | -------------- | -------- |
| `schema.py` | Typed data models (`BidInput`, `LineItem`) | Pydantic |
| `extract.py` | Prompt construction + OpenAI call + retry-until-valid | OpenAI SDK |
| `pricing_engine.py` | Implements all labor & material formulas | Pure Python |
| `formatter.py` | Render Markdown & PDF | Jinja2, WeasyPrint |
| `driver.py` | State machine for CLI / future API | Typer, Rich |

## 5. Data Models (`schema.py`)
```python
class LineItem(BaseModel):
    name: str
    quantity: PositiveInt
    mto_cost_unit: NonNegativeFloat
    minutes_per_unit: PositiveInt
    mto_mu: float = Field(1.2, gt=0)

class BidInput(BaseModel):
    bid_type: Literal["Regular", "Communication", "Electrical", "Plumbing"]
    tax_percent: float = Field(..., ge=0)
    items: List[LineItem]
```

## 6. Rates Table (`pricing_engine.py`)
| Bid Type | burden_incl | fringe | total_mhr_sale |
| -------- | ----------- | ------ | -------------- |
| Regular | 40.00 | 0.00 | 57.47 |
| Communication | 77.15 | 32.00 | 110.44 |
| Electrical | 89.13 | 36.00 | 127.53 |
| Plumbing | 93.84 | 36.00 | 134.25 |

## 7. Formulas
*Labor*
- `labor_unit_hr = minutes_per_unit / 60`
- `labor_unit_sale = labor_unit_hr × total_mhr_sale`
- `labor_total_sale = quantity × labor_unit_sale`
- `man_hours = quantity × labor_unit_hr`

*Material*
- `material_cost = quantity × mto_cost_unit`
- `material_sale_unit = mto_cost_unit × mto_mu`
- `material_sale = quantity × material_sale_unit`

*Totals*
- `labor = Σ labor_total_sale`
- `material = Σ material_sale`
- `tax = material × tax_percent`
- `total = labor + material + tax`

## 8. Conversation Flow
1. Greeting & project-type selection.
2. Collect basic project info.
3. Collect line items (loop until user says "done").
4. Validate & price.
5. Present breakdown & ask next action (PDF, revise, new project).

## 9. LLM Extraction Prompt (system role)
```
You are a data-extraction engine. Return ONLY valid JSON that matches the BidInput schema. ...
```
(See `extract.py` for full template.)

## 10. CLI Entry (`driver.py`)
```bash
pip install -r requirements.txt
python driver.py  # launches interactive prompt
```

## 11. Testing
- `pytest tests/` must pass (unit tests for extraction, pricing, formatter).
- Provide golden-file tests for sample paragraph in README.

## 12. Deployment Targets
| Env | Notes |
| ----|-------|
| CLI (MVP) | Typer / Rich for local use |
| Slack bot | Replace `driver.py` state machine with Slack events |
| Web API | FastAPI wrapper around extraction + pricing |

## 13. Open Questions for Client
1. **LLM provider & model?** (OpenAI GPT-4o assumed)
2. **Authentication?** Should the bot require login or API keys for PDF generation?
3. **Live material pricing API?** Do we integrate with a distributor now or later?
4. **PDF branding assets?** Logo, color palette, legal terms.
5. **Deployment preference?** Docker container, serverless, or on-prem?

---
Please review the open questions and confirm or amend any details so we can proceed without ambiguity. 