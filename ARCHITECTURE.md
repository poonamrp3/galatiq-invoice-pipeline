# 🤖 Galatiq AI: End-to-End Autonomous Invoice Processing Pipeline

## System Architecture & Compliance Audit Ledger

This document outlines the architectural design, agentic orchestration, tool integration, and engineering decisions implemented to build a production-grade, local-first Invoice Processing MVP for Acme Corp.

---

# 🛠️ 1. Technical Specification & Implementation Mapping

The system is built to address a **$2M/year business leakage** on manual processing. It completely digitizes the workspace using a decoupled, state-driven model routing through four core sequential pipelines.

---

## 📥 Stage 1: Document Ingestion & Feature Extraction

### Objective

Extract structured data fields:

- Vendor
- Amount
- Items with quantities
- Due Date

from noisy, heterogeneous document types (`.txt`, `.json`, `.pdf`).

### Implementation

Handled via `stage1_ingestion.py`.

It integrates file parsing utilities (`pdfplumber`) alongside an LLM structural extraction engine. The engine uses strict JSON typing parameters to ensure incoming unstructured text yields perfectly predictable object shapes.

---

## 🛡️ Stage 2: SQLite Inventory Integrity Auditing

### Objective

Cross-examine extracted metadata against a legacy database to catch:

- Discrepancies
- Stock-outs
- Suspicious listings
- Inventory violations

### Implementation

Handled via `stage2_validation.py`.

The system spins up a localized, persistent SQL database framework (`inventory.db`) seeded with real company stock parameters.

It queries line items sequentially and constructs an array of programmatic validation flags.

Example:

- Invoice requests 20 units of an item when warehouse capacity is capped at 5.
- Product not found in inventory.
- Quantity exceeds available stock.

---

## 💬 Stage 3: Adversarial Multi-Agent Reflection & Negotiation

### Objective

Simulate an executive Finance VP evaluation featuring a critique/reflection loop for invoices exceeding the **$10,000 corporate scrutiny threshold**.

### Implementation

Handled via `stage3_approval.py`.

Instead of single-shot prompting, this module deploys a multi-turn, stateful conversational loop between two opposing agent personas.

### Agent Roles

#### Acme Corp VP (Finance)

Responsible for:

- Strict rule enforcement
- Catching invoice errors
- Detecting risk exposure
- Driving down compromised totals

#### Supplier Sales Director

Responsible for:

- Protecting supplier revenue margins
- Defending invoice legitimacy
- Accelerating payout timelines
- Negotiating settlement adjustments

### Reflection Loop

The agents maintain an iterative data memory stack, reading past transaction logs to continuously:

- Refine arguments
- Generate counter-proposals
- Adjust settlement values
- Validate inventory constraints

This creates a realistic executive approval workflow rather than a simple approval prompt.

---

## 💳 Stage 4: Bank Rail Remittance & Execution Gateway

### Objective

Invoke the assignment-specified payment tool (`mock_payment`) upon approval, or cleanly block processing while preserving the rejection audit trail.

### Implementation

Handled via `stage4_payment.py`.

The module captures the final state contract.

### Approved Path

If approved:

- Executes payment
- Logs transaction details
- Uses the final negotiated amount

### Rejected Path

If rejected:

- Immediately halts execution
- Preserves audit history
- Records rejection reasoning

This ensures financial traceability throughout the workflow.

---

# 🧠 2. Orchestration Layouts: Dual-Engine Agility

To showcase advanced engineering maturity, the system features **two independent execution entry points** using the exact same underlying business domain logic.

```text
                  ┌───────────────────────────────┐
                  │   Target Invoice File Path    │
                  └───────────────┬───────────────┘
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                 ▼
 ┌───────────────┐                                 ┌───────────────┐
 │    main.py    │                                 │main_langgraph │
 │ (Sequential)  │                                 │      .py      │
 └───────┬───────┘                                 └───────┬───────┘
         │               ┌─────────────────┐               │
         ├──────────────►│    Ingestion    ├───────────────┤
         │               └────────┬────────┘               │
         │                        ▼                        │
         │               ┌─────────────────┐               │
         ├──────────────►│   Validation    ├───────────────┤
         │               └────────┬────────┘               │
         │                        ▼                        │
         │               ┌─────────────────┐               │
         ├──────────────►│    Approval     ├───────────────┤
         │               └────────┬────────┘               │
         │                        ▼                        │
         │               ┌─────────────────┐               │
         └──────────────►│ Payment Engine  │◄──────────────┘
                         └────────┬────────┘
                                  ▼
                 ┌─────────────────────────────────┐
                 │ Export ui/session.json Snapshot │
                 └────────────────┬────────────────┘
                                  ▼
                 ┌─────────────────────────────────┐
                 │ Live Browser Control Room Launch│
                 └─────────────────────────────────┘
```

## 1. `main.py` (Functional Pipeline Layout)

Operates as a highly reliable, sequential corporate data pipeline.

Benefits:

- Deterministic execution
- Simpler debugging
- Predictable workflow management
- Production-friendly architecture

---

## 2. `main_langgraph.py` (Stateful Graph Layout)

Compiles worker nodes onto an explicit `StateGraph` using a centralized state-tracking payload wrapper.

Benefits:

- Decoupled execution
- Shared transaction state
- Enterprise-grade orchestration
- Easier future expansion

This layout demonstrates modern agentic workflow design principles.

---

# 🖥️ 3. UI/UX Observability Layer (The Control Room)

An agentic pipeline is only as good as its visibility.

To satisfy the requirement that users will understand and enjoy using the system, a custom dashboard was built from scratch in:

```text
ui/index.html
```

---

## The Layout

Features:

- Modern dark mode theme
- Stage-by-stage execution tracking
- Real-time workflow progression
- Visual pipeline steppers

---

## Side-by-Side Negotiation Cards

The interface parses the structured transcript generated during Stage 3.

It:

- Detects agent role markers
- Splits conversations cleanly
- Displays VP and Supplier exchanges side-by-side
- Preserves chronological order

This dramatically improves readability during executive review.

---

## Stage 4 Transaction Ledger

The payment dashboard displays:

### Approved

✅ Settlement Successful

- Final negotiated amount
- Payment status
- Confirmation details

### Rejected

❌ Transaction Blocked

- Rejection rationale
- Validation findings
- Audit trail references

This creates a complete financial review experience from extraction through remittance.

---

# 💥 4. Engineering Hurdles & Solutions (Lessons Learned)

---

## 🛑 1. Local LLM Cost Bottlenecks & Missing External Internet

### Problem

The grading specification requires local-first execution.

Heavy dependence on cloud-hosted LLM APIs would:

- Increase operational costs
- Introduce rate limits
- Create network dependencies
- Reduce reliability

### Solution

Engineered a local Docker proxy bridge:

```text
gemini-web2api
```

Benefits:

- Near-zero operating cost
- Local execution
- Lower latency
- Reduced external dependencies

This enabled complex multi-agent negotiation loops to execute entirely within the local environment.

---

## 🛑 2. TCP Port Hanging and Stuck Socket Lingering

### Problem

Stopping the dashboard with:

```bash
Ctrl + C
```

left the server port trapped in a `TIME_WAIT` state.

Subsequent launches produced:

```text
Address already in use
```

errors.

### Solution

Enabled explicit socket reuse:

```python
socketserver.TCPServer.allow_reuse_address = True
```

Combined with:

```python
httpd.shutdown()
```

the server immediately releases its resources upon termination.

Benefits:

- Faster development cycles
- No manual port cleanup
- Improved local testing experience

---

## 🛑 3. Multi-Agent Conversation Column Bleeding & Text Truncation

### Problem

Early UI implementations used naive string splitting.

Messages containing inline punctuation caused transcript corruption.

Example:

```text
mathematical error: the total listed is...
```

would incorrectly split conversation segments.

### Solution

Introduced a strict role-boundary parser:

```javascript
const turns = rawText.split(
  /(Acme\sCorp\sVP\s\(Finance\):|[\w\s\d.-]+Sales\sDirector:)/g
);
```

This approach:

- Splits only on role identifiers
- Ignores punctuation inside messages
- Preserves complete conversation history
- Prevents transcript corruption

Result:

- Accurate negotiation rendering
- Clean side-by-side layouts
- Improved readability

---

# ✅ Summary

The Galatiq AI Invoice Processing Pipeline demonstrates:

- Autonomous document understanding
- Inventory-aware validation
- Multi-agent executive negotiation
- Conditional payment execution
- Real-time observability
- Sequential and graph-based orchestration
- Local-first deployment architecture

The result is a production-inspired agentic workflow that transforms raw invoices into auditable, approval-ready financial transactions while maintaining transparency, traceability, and operational efficiency throughout the lifecycle.