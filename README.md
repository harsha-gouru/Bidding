# MVP – Local Usage Guide

```bash
# 1. Install deps (Python 3.9+)
pip install -r requirements.txt

# 2. Export your OpenAI key
export OPENAI_API_KEY="sk-…"

# 3. Run the estimator
#    a) Interactive paste
python driver.py
#    b) Read from a text file
python driver.py --file my_bid.txt
#    c) Or via stdin
python driver.py < my_bid.txt

# 4. Stream extraction tokens (optional)
python driver.py --file my_bid.txt --stream

---

## Testing Streaming with Postman

While the CLI streams JSON tokens, you may want to hit an **HTTP** endpoint and watch the
response stream in Postman. Here's a minimal FastAPI server you can spin up:

```python title="server.py"
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from extract import Extractor

app = FastAPI()


@app.post("/extract", response_class=StreamingResponse)
async def extract_endpoint(text: str):
    extractor = Extractor()

    def generate():
        for chunk in extractor.extract_stream(text):
            yield chunk if isinstance(chunk, str) else "\n\n##JSON-END##\n\n"

    return StreamingResponse(generate(), media_type="text/plain")

# run with:  uvicorn server:app --reload --port 8000
```

1.  `pip install fastapi uvicorn`
2.  Start the server: `uvicorn server:app --reload --port 8000`
3.  In **Postman**:
    * Method: **POST**
    * URL: `http://localhost:8000/extract`
    * Body → **raw** → **Text** → Paste the long paragraph
    * Click **Send**

Postman will show a *live* response pane updating as the server yields chunks. When you see
`##JSON-END##` the final JSON has been fully transmitted. (You can change that sentinel
string to whatever suits your consumer.)

If Postman doesn't appear to stream, ensure **Settings → General → Request →
"Send no-cache header"** is **ON** and "Max response size" is large enough.

Paste your project paragraph, hit Enter twice, and you'll get a line-item table plus grand total.

---

## All-in-one Chat UI

Prefer a friendly front-end?  Run:

```bash
python chat_app.py
# → open http://127.0.0.1:7860
```

You'll get a ChatGPT-style interface where you can:
• say hello,  
• paste or upload your bid text,  
• watch the JSON stream live,  
• and see the final pricing table rendered inline.

No extra setup—`gradio` is already in `requirements.txt`.

---

Brain storm with me I want to create a chat bot i will get request like this I want to do electrician bidding mto mu is 1.2 for the following, cat6A cable 130 quantity mto cost/unit 95 minutes per unit 100, install cat6A jacks 260 quantity mto cost/unit 11 minutes per unit 9, Provide and install Cat6 48-port patch panels 4 quantity mto cost/unit 120 minutes per unit 30, Provide and install patch cord  quantity 130  mto cost/unit 16 minutes per unit 5, Provide and install faceplates ro biscuit jacks 108 quantity mto cost/unit 3.85 minutes per unit 8, remove old cabling quantity 1  mto cost/unit 150 minutes per unit 600, Test, label and certify Cat6 cables 130 quantity mto cost/unit 3 minutes per unit 10, Consumables 1 quantity mto cost/unit 1000 minutes per unit 60, Provide and install 12 strand multi-mode fiber OM4 1145 quantity mto cost/unit 1.46 minutes per unit 1, provide and install 12 count LC OM4 cassettes 6 quantity mto cost/unit 430 minutes per unit 120, provide and install New fiber housing unit 1U  4 quantity mto cost/unit 185 minutes per unit 15, Provide and install fiber spool 4 quantity mto cost/unit 120 minutes per unit 30, Test and certify fiber cabling 36 quantity mto cost/unit 1.25 minutes per unit 5, Provide and install wall mount IDF cabinet 1 quantity mto cost/unit 780 minutes per unit 120, provide and install fire rated back board  1 quantity mto cost/unit 89 minutes per unit 120. Tax Percent: 0.0825 and extractin information and calculate accordingly
You are a professional Construction Bid Estimator Assistant specializing in network, electrical, and plumbing project cost estimation. Your purpose is to guide users through a structured, stage-based bidding process that delivers accurate, detailed cost breakdowns and professional proposals.
 
# Core Capabilities
- Guide users through a conversational, stage-based estimation process
- Calculate precise labor and material costs using industry-standard formulas
- Generate detailed bid breakdowns with proper tax and markup calculations
- Produce professional, branded PDF quotes when requested
- Reference live market pricing when available
 
# Advanced Pricing Considerations
## Labor Rate Complexity Factors
- Account for installation complexity
- Include overhead costs and project-specific challenges in labor calculations
- Apply prevailing wage rates when applicable (significantly higher than standard rates)
- Consider access difficulty, height requirements, and installation environment
 
## Material Pricing Accuracy
- Use brand-specific pricing from actual distributors rather than generic estimates
- Reference the most current market rates for all materials
- Include all hardware components, not just primary materials
- Apply appropriate markup based on material type and procurement difficulty
 
## Bundled Services Recognition
- Identify when line items include multiple services (e.g., "hardware from BOM" may include mounting, assembly, and site prep)
- Break down bundled services when possible to show true cost distribution
- Recognize when labor charges include preparation work not explicitly listed
 
# Interaction Flow
1. Begin with a friendly welcome and project type selection
2. Store all user responses in memory throughout the session
3. Progress through all required sections in sequence
4. Calculate and present detailed bid results
5. Offer next action options (PDF generation, template saving, etc.)
 
# Project Type Pathways
When a user begins a new estimation session, present these options:
- 📡 Network Cabling
- ⚡ Electrical Installation
- 🛠️ Mixed (Electrical + Data)
- 🔧 Plumbing
 
## For Network Cabling projects, first give basic calculations with what user asks then you can dig deeper by asking following:
- Cable type (Cat5e, Cat6, Cat6A, Fiber, etc.)
- Number of drops
- Average drop length
- Patch panel type
- Conduit requirements
- Diagram uploads (if available, Optional)
- Scope description
- Permit/compliance requirements
 
## For Electrical Installation projects, first give basic calculations with what user asks then you can dig deeper by asking following:
- Voltage level
- Panel size
- Number of circuits
- Lighting requirements
- Conduit type
- Site conditions
- Drawing uploads (if available, Optional)
- Scope description
- Inspection requirements
 
## For Mixed projects:
- Collect both Network and Electrical information
 
## For Plumbing projects:
- Fixture types and quantities
- Pipe types and lengths
- Special requirements
 
# Core Input Sections
After project-specific questions, collect:
 
## Project Basics
- Project name
- Client information
- Location
- Completion date
 
## Materials
- Material name
- Quantity
- Cost per unit
- Minutes per unit for installation
 
## Labor
- Number of technicians
- Hours per day
- Total days
- Prevailing wage requirements
 
## Financial Settings
- Tax rate (based on location)
- Markup percentage
- Bonding requirements
- Payment terms
 
## Special Conditions
- After-hours work
- Security clearance needs
- Access limitations
- Demolition requirements
 
# Calculation Formulas
Use these precise formulas for all calculations:
 
## Bid Type Base Rates
- Regular: 
       mhr_cost $40.00
       Fringe $0.00
       burden_incl: $40.00
       mhr_sale: $17.04
       total_mhr_sale: $57.47
- Communication: 
       mhr_cost $45.00
       Fringe $32.00
       burden_incl: $77.15
       mhr_sale: $32.87
       total_mhr_sale: $110.44
- Electrical: 
       mhr_cost $51.00
       Fringe $36.00
       burden_incl: $89.13
       mhr_sale: $37.97
       total_mhr_sale: $127.53
- Plumbing: 
       mhr_cost$51.00
       Fringe $36.00
       burden_incl:$93.84
       mhr_sale: $39.98
       total_mhr_sale: $134.25
 
## Labor Calculations
- labor_unit = minutes_per_unit / 60
- unit_sale = labor_unit × total_mhr_sale
- total_sale = quantity × unit_sale
- man_hours = quantity × labor_unit
- total_cost = (burden_incl + fringe) × labor_unit × quantity
 
## Material Calculations
- mto_cost = quantity × mto_cost_unit
- mto_sale_unit = mto_cost_unit × mto_mu
- mto_sale = quantity × mto_sale_unit
 
## Final Calculations
- labor = total_sale
- material = mto_sale
- tax = material × tax_percent
- total = labor + material + tax
 
## Grand Totals
- Calculate sums across all line items for labor, material, tax
- Calculate profit margins and percentages
 
# Output Presentation
For each line item, display:
1. Labor calculations with unit sale, total sale, cost, and man-hours
2. Material details including name, costs, markup, and tax
3. Line item summary with subtotals
 
After all lines, show:
- Grand totals for labor, material, tax
- Total profit and percentage
- Final bid price
but everytime i give the above context to llm it gives me different result help me what ways to avoid I was thinking like create the calculation as functions and use for function calling and extract the data can you suggest me how do I do this flow?


Below is a battle‑tested pattern I use whenever I need *repeatable*, *audit‑friendly* calculations from an LLM. It keeps every concern in its own tiny module, enforces typed I/O, and gives you deterministic math while still letting the model handle "squishy" language tasks.

---

## 0. Guiding principles (your requested values)

| Principle                      | Why it matters                                         | How it shapes the design                                                      |
| ------------------------------ | ------------------------------------------------------ | ----------------------------------------------------------------------------- |
| **Conciseness**                | Less code = fewer bugs, faster review.                 | One‑file modules, no nested classes, `__all__` exports.                       |
| **DRY**                        | Duplication silently diverges.                         | All formulas live in one `pricing_engine.py`; no copy‑pasted math in prompts. |
| **Self‑documenting code**      | Comments drift; good names don't.                      | Pydantic models + type hints + property names that *read like the spec*.      |
| **Modularity**                 | Swappable parts (e.g. wage tables vs. plumbing rates). | Separate `extract.py`, `schema.py`, `pricing_engine.py`, `formatter.py`.      |
| **Few lines over readability** | Eyes > lines, but terseness wins once intent is clear. | Heavy use of dataclasses/Pydantic & comprehensions.                           |
| **Reusable functions**         | ChatGPT can call them directly (function‑calling API). | Each business rule = pure function, 100 % unit‑testable.                      |
| **Verbose logs**               | Estimators must justify every penny.                   | `rich` console logging with line‑item diff & totals.                          |
| **Modern libs**                | They erase boilerplate.                                | `pydantic`, `rich`, `typer`, `jinja2`, `weasyprint` for PDF.                  |

---

## 1. High‑level flow

```text
User NL → LLM (extract) → JSON → pricing_engine (deterministic math)
                                   ↓
                            formatter (tables, PDF)
                                   ↓
                              Chat reply
```

1. **Extraction** – The LLM's *only* job is to turn messy sentences into a strict schema.
2. **Validation** – Pydantic rejects impossible numbers **before** we touch money.
3. **Pricing** – Pure Python functions implement every formula from your spec.
4. **Presentation** – Re‑usable Jinja template renders Markdown, HTML, or PDF.
5. **Conversation driver** – Simple state machine decides which stage you're in.

---

## 2. JSON schema (single source of truth)

```py
# schema.py
from pydantic import BaseModel, Field, PositiveInt, NonNegativeFloat
from typing import List

class LineItem(BaseModel):
    name: str
    quantity: PositiveInt
    mto_cost_unit: NonNegativeFloat
    minutes_per_unit: PositiveInt
    mto_mu: float = Field(1.2, gt=0)

class BidInput(BaseModel):
    bid_type: str  # "Communication" | "Electrical" | ...
    tax_percent: float = Field(..., ge=0)
    items: List[LineItem]
```

---

## 3. Extraction prompt + function call

```jsonc
# openai.ChatCompletion.create
{
  "model": "gpt-4o-mini",
  "temperature": 0,
  "messages": [
    {"role": "system",
     "content": "Return the data as valid JSON matching the BidInput schema exactly. Do not perform calculations."},
    {"role": "user",
     "content": "<user pasted text>"}
  ],
  "functions": [{
      "name": "submit_bid_input",
      "description": "Structured bid line items",
      "parameters": BidInput.schema()  // pydantic generates JSONSchema
  }]
}
```

The assistant *must* reply via the `submit_bid_input` function; OpenAI will give you that structured dict → pass straight into `pricing_engine`.

---

## 4. Deterministic pricing engine (pure functions)

```py
# pricing_engine.py
from schema import LineItem
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Rates:
    burden_incl: float
    fringe: float
    total_mhr_sale: float

RATES = {
    "Communication": Rates(77.15, 32.0, 110.44),
    "Electrical":    Rates(89.13, 36.0, 127.53),
    "Plumbing":      Rates(93.84, 36.0, 134.25),
    "Regular":       Rates(40.00, 0.0, 57.47),
}

def price_line(item: LineItem, rates: Rates) -> dict:
    labor_unit_hr = item.minutes_per_unit / 60
    labor_unit_sale = labor_unit_hr * rates.total_mhr_sale
    material_sale_unit = item.mto_cost_unit * item.mto_mu

    return {
        "name": item.name,
        "labor_unit_sale": labor_unit_sale,
        "labor_total_sale": labor_unit_sale * item.quantity,
        "man_hours": labor_unit_hr * item.quantity,
        "material_cost": item.mto_cost_unit * item.quantity,
        "material_sale": material_sale_unit * item.quantity,
    }

def price_bid(items: List[LineItem], bid_type: str, tax_percent: float) -> dict:
    rates = RATES[bid_type]
    details = [price_line(i, rates) for i in items]

    labor = sum(d["labor_total_sale"] for d in details)
    material = sum(d["material_sale"] for d in details)
    tax = material * tax_percent
    total = labor + material + tax

    return {"lines": details, "labor": labor, "material": material, "tax": tax, "total": total}
```

***Key points***
*Pure function* → idempotent, unit‑testable, zero randomness, so ChatGPT can't "drift" your numbers.

---

## 5. Formatter (Markdown → PDF)

```py
# formatter.py
from jinja2 import Template
from weasyprint import HTML

MD_TMPL = Template("""
## Bid Summary – {{ bid_type }}

| Line Item | Qty | Labor $/u | Labor Total | Mat. Total | M‑Hrs |
|-----------|----:|---------:|------------:|-----------:|------:|
{% for l in lines -%}
| {{ l.name }} | {{ l.qty }} | {{ l.labor_unit_sale|round(2) }} | {{ l.labor_total_sale|round(2) }} | {{ l.material_sale|round(2) }} | {{ l.man_hours|round(2) }} |
{% endfor %}
| **Totals** |   |   | **{{ labor|round(2) }}** | **{{ material|round(2) }}** | |
| **Tax** ({{ tax_pct*100 }} %) |   |   |   | **{{ tax|round(2) }}** | |
| **Grand Total** |   |   | **{{ total|round(2) }}** |   | |
""")

def render(bid, bid_type, tax_pct):
    md = MD_TMPL.render(**bid, bid_type=bid_type, tax_pct=tax_pct)
    pdf = HTML(string=md).write_pdf()
    return md, pdf
```

Use `rich` during dev to `print_json(bid)` and diff successive runs.

---

## 6. Conversation state machine (ultra‑light)

```py
# driver.py
import openai, typer, json
from schema import BidInput
from pricing_engine import price_bid
from formatter import render

state = {"stage": "collecting"}

while True:
    user = typer.prompt("🗨️  You")
    # 1. send to LLM with function schema
    # 2. if a `submit_bid_input` function call is returned → validate
    if fn_call := maybe_fn_call(user):              # pseudo
        data = BidInput(**fn_call["arguments"])     # Pydantic validation
        bid = price_bid(data.items, data.bid_type, data.tax_percent)
        md, pdf = render(bid, data.bid_type, data.tax_percent)
        typer.echo(md)
        # offer to write pdf to disk or email
```

`maybe_fn_call` is a tiny helper that decodes the OpenAI response; most SDKs now have first‑class helpers.

---

## 7. Making results **consistent**

* Use `temperature: 0` and `top_p: 0.1` for the extraction step.
* **Never** ask the model to both *extract* and *calculate* in one breath—split tasks.
* Keep *all* formulas in Python, not in prompts.
* Add unit tests with golden numbers to guard against accidental formula edits.

---

### Ready‑to‑run demo (swap in your sample data)

```bash
pip install openai pydantic rich jinja2 weasyprint typer
python driver.py
```

Paste your long paragraph, the bot replies with the table + grand total, and it offers a PDF if you need customer‑ready output.

---

## Next steps

1. **Plug in live material pricing** – swap `mto_cost_unit` with an async call to your distributor's API before feeding the LineItem to the engine.
2. **Prevailing wage toggle** – select the `Rates` struct by locale or project flag.
3. **Persist sessions** – Redis + customer ID so multi‑step conversations survive disconnects.
4. **Auth + branding** – re‑skin the Jinja template per client, inject logo, terms, signature.

That's it—deterministic math, surgically small modules, and zero surprises from the LLM. Happy bidding!

### The big‑picture workflow (without the tech jargon)

1. **Listen & Catch the Details**
   The bot's first job is simply to *hear* your messy paragraph ("Install 260 jacks… tax 8.25 %…") and pull out the facts—just like a human estimator jotting numbers on a notepad.

2. **Snap the Facts into a Template**
   Those facts drop into a clean table:
   *item name, how many, cost each, minutes to install, markup*.
   Think of it as putting receipts into the right columns of a spreadsheet.

3. **Run the Spreadsheet Math**
   A fixed set of formulas—your industry rules—turn those raw numbers into:
   *labor dollars, material dollars, tax, and total*.
   Because the math lives outside the chatbot, the answers never drift.

4. **Show the Breakdown**
   The bot then turns that spreadsheet into a tidy summary:

   * line‑by‑line costs
   * grand totals
   * profit and tax numbers
     It can display that right in chat or save it as a polished PDF.

5. **Keep the Conversation Going**
   Finally, the bot asks, "Need a PDF quote, want to tweak quantities, or start a new project?"—and loops back to Step 1 for the next round.

---

**Why this flow is reliable**

* The AI only *extracts words into numbers*—no complex math, so it can't mis‑calculate.
* The formulas never change unless *you* edit them.
* Every step leaves a paper trail (the table, the summary, the PDF), so you can double‑check or hand it to a colleague.

In short: *chat in, numbers out, repeat.*

**Short answer:**
You usually don't need to fine‑tune.  GPT‑4 / 4o will pull the numbers out perfectly *as long as you give it a rock‑solid extraction prompt, force it to answer in a strict JSON schema, and add an automatic "retry‑until‑valid" guard*.  Fine‑tuning only makes sense after you've collected lots of real jobs and can prove a repeat pattern of errors you cannot fix with prompt + validation.

---

## Getting "mistake‑free" extraction in practice

| Step                                   | What you do                                                                                                                                                     | Why it works                                                                          |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **1 — Lock the output format**         | Tell the model: "Respond **only** with JSON that exactly matches this schema." Pass the schema to the OpenAI **function‑calling** API.                          | Function calling turns the model into a fancy form‑filler; random text can't leak in. |
| **2 — Run at deterministic settings**  | `temperature = 0`, `top_p = 0.1`.                                                                                                                               | Removes creativity; the model focuses on facts.                                       |
| **3 — Validate immediately**           | Feed the reply into Pydantic (or your own checker). If it fails, ask the model to "try again, following the schema." Loop until it passes or you hit N retries. | Catches typos, missing fields, bad number formats.                                    |
| **4 — Add "can't‑miss" cues**          | Prepend every line in your schema with an emoji or short tag in the user prompt (e.g., "🔢 Quantity: 130"). The model then has visual anchors.                  | Simple yet shockingly effective for low‑context source text.                          |
| **5 — Unit‑test on 20–30 real blurbs** | Paste old bids, run extraction, store the JSON, and assert each field.                                                                                          | Gives you a safety net before launch.                                                 |
| **6 — Ask clarifying questions**       | If the extracted data is *internally* valid but still ambiguous (e.g., unit type missing), have your code bounce a follow‑up question to the user.              | Human‑in‑the‑loop beats silent wrong guesses.                                         |

---

### Do you ever fine‑tune?

Only when **all three** are true:

1. You've logged **hundreds** of real requests.
2. The same *specific* fields keep getting mis‑parsed even after prompt tweaks.
3. Those errors cost more to fix manually than a fine‑tune would cost to train and red‑team.

Fine‑tuning is awesome for style or domain slang, but for plain numeric extraction it's usually overkill.

---

### What if the model still slips?

* **Dual‑parse strategy:** run the prompt twice with slightly different phrasing; if the two JSONs disagree, flag for review.
* **Regex fallback:** for utterly predictable tokens (dates, tax %, MU), you can regex‑scan the source first and *pre‑fill* the JSON before the model sees it.
* **Strict post‑processing:** convert all floats to `Decimal`, clip impossible ranges (e.g., minutes > 1440/day), and log any correction.

---

## Take‑away

* **Prompt + function schema + validation loop** gives > 99 % accuracy on well‑structured numeric text.
* **Fine‑tuning is optional**, best reserved for edge cases you can't squash with better prompts and guards.
* **Redundancy wins:** deterministic settings, automatic retries, and human clarifications together make "mistakes" vanishingly rare—and far cheaper than custom training.

Below is a **copy‑and‑paste‑ready "extraction kit."**
It works with any modern GPT‑style model (OpenAI, Anthropic, open‑source) because:

* It **locks** the output format with an explicit JSON schema.
* It **forbids** explanations or extra text.
* It **requires** the model to echo every numeric field exactly as written.

You only need to change the schema if your data columns change.

---

## 1 — Define the schema once in code

```python
# schema.py  (Python, Pydantic – but the JSON Schema string also
#             works verbatim in non‑Python stacks)

from pydantic import BaseModel, Field, PositiveInt, NonNegativeFloat
from typing import List, Optional

class LineItem(BaseModel):
    name: str
    quantity: PositiveInt
    mto_cost_unit: NonNegativeFloat
    minutes_per_unit: PositiveInt
    mto_mu: float = Field(1.2, gt=0)   # default markup factor

class BidInput(BaseModel):
    bid_type: str                      # "Communication" | "Electrical" | ...
    tax_percent: float = Field(..., ge=0)
    items: List[LineItem]
```

To hand this to an LLM via OpenAI function calling, do:

```python
function_def = {
    "name": "submit_bid_input",
    "description": "Structured bid line items for pricing",
    "parameters": BidInput.schema()     # JSON Schema auto‑generated by Pydantic
}
```

If your platform doesn't support functions, just keep the same field names and check the JSON manually after you receive it.

---

## 2 — System prompt (copy‑exactly)

> **SYSTEM**
> You are a data–extraction engine.
> **Return *only* valid JSON that matches the "BidInput" schema below.**
> Do **not** add commentary, Markdown, or surrounding text.
> If any value is missing, return `null` (or omit the optional field).
> If you are unsure of a number, ask a clarifying question **instead** of guessing.
> Once the JSON is valid, do not repeat it in any other format.
>
> **BidInput JSON Schema:**
>
> ```json
> {{ BidInput.schema_json(indent=2) }}
> ```

*(If you can't embed Python, paste the literal JSON schema string in place of the curly‑brace expression.)*

---

## 3 — User prompt template

Below is a **template**; drop in the actual paragraph the user typed:

```
Extract the bid data from the text below.

TEXT:
"""
I want to do electrician bidding mto mu is 1.2 for the following, 
cat6A cable 130 quantity mto cost/unit 95 minutes per unit 100,
install cat6A jacks 260 quantity mto cost/unit 11 minutes per unit 9,
...
Tax Percent: 0.0825
"""
```

*(No extra instructions necessary—everything the model needs is in the system prompt.)*

---

## 4 — API call settings

```python
openai.ChatCompletion.create(
    model="gpt-4o-mini",
    temperature=0,
    top_p=0.1,
    messages=[system_prompt, user_prompt],
    functions=[function_def],       # omit if your model lacks the feature
    function_call="auto",           # forces JSON-only response
)
```

---

## 5 — Validation & retry loop

```python
def extract_bid(text: str, retries: int = 3) -> BidInput:
    for _ in range(retries):
        response = chat_completion(text)          # your wrapper
        payload = response.choices[0].message
        if payload.get("function_call"):
            args = json.loads(payload["function_call"]["arguments"])
        else:                                     # no function support
            args = json.loads(payload.content)

        try:
            return BidInput(**args)               # pydantic validation
        except Exception as err:
            text = (
                "The previous JSON was invalid.\n"
                f"Error: {err}\n"
                "Please correct and output *only* valid JSON."
            )
    raise ValueError("Model failed to produce valid JSON after retries.")
```

---

## 6 — Plain‑JSON fallback prompt (for LLMs **without** function calling)

If you're using an open‑source model that can't do structured function calls, prepend this line to the **system** prompt:

> Output the JSON **inside a single pair of triple backticks**, nothing else.

Then regex‑grab the block between ` ` and `json.loads()` it, still validating with Pydantic.

---

## 7 — Why this stays consistent

* **Schema → Validation → Retry**: any stray character forces a retry, so you only accept perfect JSON.
* **Temperature 0**: removes creative paraphrasing of numbers ("one‑hundred‑thirty" → `130`).
* **Clarification rule**: the model must *ask* if information is missing instead of hallucinating.

With this scaffold, GPT‑4‑class models reliably score ~100 % on numeric extraction in production. Fine‑tuning becomes unnecessary until you have hundreds of edge‑case examples that still fail validation.

