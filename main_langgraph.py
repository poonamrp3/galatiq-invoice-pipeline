# main_langgraph.py
import argparse
import os
import json
from typing import Dict, Any, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END

# Import your untouched, modular agent files
from llm_factory import LLMProviderEngine
from stage1_ingestion import execute_ingestion_stage
from stage2_validation import execute_validation_stage

# =====================================================================
# 1. DEFINE THE ORCHESTRATOR GRAPH STATE CONTRACT
# =====================================================================
class PipelineState(TypedDict):
    invoice_path: str
    extracted_data: Dict[str, Any]
    system_flags: List[str]

# Initialize the shared proxy engine once globally
engine = LLMProviderEngine()

# =====================================================================
# 2. WRAP YOUR PIPELINE STAGES INTO GRAPH NODES
# =====================================================================
def ingestion_node(state: PipelineState) -> Dict[str, Any]:
    print("\n--- [LANGGRAPH] NODE 1: INGESTION PIPELINE NODE ---", flush=True)
    # Pass the custom file path from the state into your ingestion agent
    data = execute_ingestion_stage(state["invoice_path"], engine)
    return {"extracted_data": data}

def validation_node(state: PipelineState) -> Dict[str, Any]:
    print("\n--- [LANGGRAPH] NODE 2: VALIDATION PIPELINE NODE ---", flush=True)
    # Pass the data dict from the state into your SQLite validation agent
    flags = execute_validation_stage(state["extracted_data"])
    return {"system_flags": flags}

# =====================================================================
# 3. BUILD THE ORCHESTRATION GRAPH COMPILER
# =====================================================================
workflow = StateGraph(PipelineState)

# Define our execution nodes
workflow.add_node("stage1_ingest", ingestion_node)
workflow.add_node("stage2_validate", validation_node)

# Map out our directed edges sequence
workflow.set_entry_point("stage1_ingest")
workflow.add_edge("stage1_ingest", "stage2_validate")
workflow.add_edge("stage2_validate", END)

# Compile into an executable state machine application
graph_orchestrator = workflow.compile()

# =====================================================================
# 4. COMMAND LINE ENTRY POINT RUNNER
# =====================================================================
def main():
    parser = argparse.ArgumentParser(description="Galatiq AP LangGraph Orchestrator Pipeline")
    parser.add_argument("--invoice_path", required=True, help="Local path to invoice file.")
    args = parser.parse_args()

    file_path = args.invoice_path
    if not os.path.exists(file_path):
        print(f"❌ Error: Targeted file path does not exist: {file_path}", flush=True)
        return

    print("\n[START] LangGraph Orchestrator Runtime Activated.", flush=True)
    
    # Initialize the graph conveyor belt with the command line input argument
    initial_inputs = {"invoice_path": file_path}
    
    # Fire up the graph processing engine
    final_state = graph_orchestrator.invoke(initial_inputs)
    
    # Extract data maps from the final state snapshot for printing
    extracted_data = final_state.get("extracted_data", {})
    routing = extracted_data.get("strategic_routing", {})
    system_flags = final_state.get("system_flags", [])

    print("\n================== LANGGRAPH ORCHESTRATION FINAL SUMMARY ==================")
    print("[STAGE 1: EXTRACTED STRUCTURAL DATA]")
    print(f"Vendor Detected    : {extracted_data.get('vendor')}")
    print(f"Grand Total Parsed : {extracted_data.get('currency')} {extracted_data.get('total_amount')}")
    print(json.dumps(extracted_data, indent=2))
    print("-" * 74)
    
    print("\n[STAGE 1: STRATEGIC REASONING]")
    print(f"  ▪ Payment Priority   : {routing.get('payment_priority', 'N/A')}")
    print(f"  ▪ Settlement Buffer : {routing.get('days_to_settlement', 'N/A')} Days remaining")
    print(f"  ▪ Action Memo       : {routing.get('action_required_memo', 'N/A')}")
    print("-" * 74)
    
    print("\n[STAGE 2: DATABASE COGNITIVE COMPLIANCE]")
    if system_flags:
        print(f"  ❌ AUDIT WARNING: {len(system_flags)} compliance anomalies flagged:")
        for flag in system_flags:
            print(f"    ⚠️  {flag}")
    else:
        print("  🟢 PASSED: All parameters successfully cleared by database inventory engine.")
    print("===========================================================================")

if __name__ == "__main__":
    try:
        main()
        print("\n[END] LangGraph execution sequence completed cleanly.", flush=True)
    except Exception as e:
        print(f"\n💥 GRAPH RUNTIME EXCEPTION:\n{str(e)}", flush=True)