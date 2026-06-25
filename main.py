# main.py
import argparse
import os
import json
from llm_factory import LLMProviderEngine
from stage1_ingestion import execute_ingestion_stage
# Import Stage 2 Validation Node
from stage2_validation import execute_validation_stage

def main():
    parser = argparse.ArgumentParser(description="Galatiq AP Multi-Agent Orchestrator Pipeline")
    parser.add_argument("--invoice_path", required=True, help="Local path to invoice file.")
    args = parser.parse_args()

    file_path = args.invoice_path
    if not os.path.exists(file_path):
        print(f"❌ Error: Targeted file path does not exist: {file_path}", flush=True)
        return

    # --- STAGE 0: CLIENT CONNECTIVITY CHECK ---
    print("\n--- STAGE 0: CLIENT CONNECTIVITY CHECK ---", flush=True)
    engine = LLMProviderEngine()
    
    # --- STAGE 1: INGESTION PIPELINE NODE ---
    print("\n--- STAGE 1: INGESTION PIPELINE NODE ---", flush=True)
    extracted_data = execute_ingestion_stage(file_path, engine)

    # Display the results cleanly on screen
    print("\n[INGESTION STATE CAPTURED SUCCESS]")
    print(f"Vendor Detected: {extracted_data.get('vendor')}")
    print(f"Grand Total Parsed: {extracted_data.get('currency')} {extracted_data.get('total_amount')}")
    print("\nFull Structured Data Payload:")
    print(json.dumps(extracted_data, indent=2))
    print("-" * 62)

    # --- STAGE 2: VALIDATION PIPELINE NODE ---
    print("\n--- STAGE 2: VALIDATION PIPELINE NODE ---", flush=True)
    # Feed Stage 1's dictionary directly into the database cross-check engine
    system_flags = execute_validation_stage(extracted_data)
    print("-" * 62)

if __name__ == "__main__":
    try:
        print("[START] Multi-Agent Processing Sequence Activated.", flush=True)
        main()
        print("\n[END] Workflow step completed cleanly.", flush=True)
    except Exception as e:
        print(f"\n💥 PIPELINE EXCEPTION:\n{str(e)}", flush=True)