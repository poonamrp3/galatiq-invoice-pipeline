# Galatiq Case: Invoice Processing Automation System

An intelligent, multi-agent automated system engineered to eliminate manual invoice parsing, detect financial anomalies/fraud, and streamline VP-level risk approvals using local tool validation and state reflection loops.

---

## 🚀 Quick Start (Local Environment Setup)

Follow these steps sequentially to configure your local runtime environment and initialize the required persistent data layers.

### 1. Environment & Dependency Setup

Open your terminal (on Mac, use your standard shell; on Windows, use the **Anaconda Prompt** or **Miniconda Prompt**) and execute:

```bash
# Create an isolated Python 3.11 environment
conda create -n galatiq-invoice-env python=3.11 -y

# Activate the environment
conda activate galatiq-invoice-env

# Install all required dependencies
pip install -r requirements.txt
```

### 2. Initialize the Legacy Database System

Before executing any agent workflows, you must seed the mock local inventory tracking database. This establishes the structural baselines for validation testing:

```bash
python setup_db.py
```

## Environment Configuration

Add the following API keys to your project's `.env` file if they are available:

```env
GEMINI_API_KEY=your_gemini_api_key
TOGETHER_API_KEY=your_together_api_key
XAI_API_KEY=your_xai_api_key
```

---

## Verify LLM Connectivity

Run the following command to test connectivity with the configured LLM provider:

```bash
python test_connection.py
```

This script will communicate with the LLM corresponding to the API key you have configured and perform a connectivity check to verify that the credentials and endpoint are functioning correctly.

---

## Execute the Agentic Framework

### 1. Custom Agentic Framework Implementation

Run the following command to execute the custom multi-agent invoice processing workflow:

```bash
python -u main.py --invoice_path=data/invoices/invoice_1012.txt
```

---

### 2. LangGraph-Based Agentic Workflow

Run the following command to execute the LangGraph implementation of the agentic invoice processing workflow:

```bash
python -u main_langgraph.py --invoice_path=data/invoices/invoice_1012.txt
```

The workflow will process the specified invoice, perform validation checks, route approvals when required, and generate the final processing output.

---

## 📚 Technical Documentation & System Reference

For a deep dive into the inner workings, engineering layouts, and file structures of this multi-agent system, please refer to our dedicated architecture guides:

* **[ARCHITECTURE.md](ARCHITECTURE.md)** – Detailed architectural blueprint spanning the four sequential execution stages, dual-engine orchestrator design specs (`main.py` vs. `main_langgraph.py`), UI/UX control room mapping, and core engineering hurdles/solutions.
* **[FILES_REGISTER.md](FILES_REGISTER.md)** – Core module index mapping individual script purposes (`llm_factory.py`, `stage1_ingestion.py` through `stage4_payment.py`) and programmatic configurations.