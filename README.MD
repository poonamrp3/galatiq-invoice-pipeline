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