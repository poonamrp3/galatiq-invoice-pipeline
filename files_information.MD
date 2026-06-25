# Galatiq Accounts Payable (AP) Multi-Agent Pipeline

An intelligent, multi-stage accounts payable ingestion and compliance audit workflow that transforms unstructured documents into strictly structured data, cross-checks parameters against local relational warehouse databases, and issues executive routing actions.

## File Registry & Module Directory

* **`llm_factory.py`** The core connectivity engine. Intercepts LLM calls and adaptive configurations, natively routing payloads to a cost-effective local `gemini-web-to-api` Docker proxy wrapper targeting the `gemini-advanced` web interface.
  
* **`stage1_ingestion.py`** The AI Ingestion Agent. Leverages Pydantic `BaseModel` structures (`ComprehensiveInvoice`, `InvoiceItem`, `OperationalReasoning`) to extract unstructured textual document data into strict, type-validated, machine-readable JSON contracts.
  
* **`stage2_validation.py`** The Database Compliance Controller. A deterministic Python validation engine that queries local SQLite (`inventory.db`) data toolsets to audit warehouse stock limits, isolate unknown SKU assets, and enforce multi-layered financial arithmetic guardrails.

**`stage3_approval.py`**  Multi-Agent Negotiation Loop. Simulates a conversational, back-and-forth state machine between a Finance VP Agent and a Supplier Account Agent to resolve stock/price anomalies up to a 6-turn maximum before building a final ledger entry. 

**`stage4_payment.py`** Payment Routing Engine. Evaluates the executive authorization state. If approved, executes an official mock banking API transaction routing function; if denied, acts as a compliance gate to block funds and log the audit failure. 

* **`init_db.py`** Database initializer utility. Seeds the local SQLite database (`inventory.db`) with test mock product rows, unit prices, and explicit inventory quantities to trigger boundary edge cases.
  
* **`main.py`** The Custom Imperative Orchestrator. Executes the stable pipeline stages sequentially line-by-line using explicit, fast, native Python functional data-flow handoffs driven by command-line path arguments.
  
* **`main_langgraph.py`** The Automated Graph Orchestrator. Wraps the identical, untouched functional agent modules as graph network Nodes, utilizing the LangGraph framework runtime to manage state transitions down a shared state conveyor belt.
  
* **`requirements.txt`** The centralized environment tracking manifest. Maps the exact package dependency versions (`langgraph`, `pydantic`, `openai`, etc.) to guarantee stable, reproducible pipeline deployments.