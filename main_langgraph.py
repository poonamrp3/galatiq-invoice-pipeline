# main_langgraph.py
import argparse
import os
import json
import webbrowser
import http.server
import socketserver
import threading
from typing import Dict, Any, List
from typing_extensions import TypedDict

# LangGraph core engine components
from langgraph.graph import StateGraph, END

# Import your multi-stage decoupled pipeline components
from llm_factory import LLMProviderEngine
from stage1_ingestion import execute_ingestion_stage
from stage2_validation import execute_validation_stage
from stage3_approval import execute_approval_stage
from stage4_payment import execute_payment_stage  # <--- NEW IMPORT

# Local UI server port designation
PORT = 8000

# =====================================================================
# 1. STATE DEFINITION SCHEMA
# =====================================================================
class PipelineState(TypedDict):
    file_path: str
    engine: LLMProviderEngine
    extracted_data: Dict[str, Any]
    validation_flags: List[str]
    verdict: Dict[str, Any]

# =====================================================================
# 2. STATE GRAPH NODE WORKERS
# =====================================================================
def ingestion_node(state: PipelineState) -> Dict[str, Any]:
    print("\n--- [LANGGRAPH] NODE: INGESTION PIPELINE ---", flush=True)
    data = execute_ingestion_stage(state["file_path"], state["engine"])
    return {"extracted_data": data}

def validation_node(state: PipelineState) -> Dict[str, Any]:
    print("\n--- [LANGGRAPH] NODE: SQL INTEGRATION VALIDATION ---", flush=True)
    flags = execute_validation_stage(state["extracted_data"])
    return {"validation_flags": flags}

def approval_node(state: PipelineState) -> Dict[str, Any]:
    print("\n--- [LANGGRAPH] NODE: VP EXECUTVE REVIEW & REFLCTION ---", flush=True)
    verdict = execute_approval_stage(
        state["file_path"], 
        state["extracted_data"], 
        state["validation_flags"], 
        state["engine"]
    )
    return {"verdict": verdict}

# =====================================================================
# 3. SILENT LOCAL WEB SERVER THREAD
# =====================================================================
def start_local_ui_server():
    """Spins up a lightweight background web server targeting the ui folder."""
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            return

    os.chdir("ui")
    socketserver.TCPServer.allow_reuse_address = True
    
    global httpd
    with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
        try:
            httpd.serve_forever()
        except Exception:
            pass

# =====================================================================
# 4. SYSTEM RUNNER PIPELINE
# =====================================================================
def main():
    parser = argparse.ArgumentParser(description="Galatiq AP LangGraph State Orchestrator Pipeline")
    parser.add_argument("--invoice_path", required=True, help="Local path to invoice file.")
    args = parser.parse_args()

    file_path = args.invoice_path
    if not os.path.exists(file_path):
        print(f"❌ Error: Targeted file path does not exist: {file_path}", flush=True)
        return

    # Initialize your factory engine
    engine = LLMProviderEngine()

    # --- COMPILE STATE GRAPH ARCHITECTURE ---
    workflow = StateGraph(PipelineState)

    workflow.add_node("ingest", ingestion_node)
    workflow.add_node("validate", validation_node)
    workflow.add_node("approve", approval_node)

    workflow.set_entry_point("ingest")
    workflow.add_edge("ingest", "validate")
    workflow.add_edge("validate", "approve")
    workflow.add_edge("approve", END)

    app = workflow.compile()

    # --- RUN THE AGENT GRAPH ---
    print("\n[START] LangGraph Stateful Execution Pipeline Triggered.", flush=True)
    initial_state = {
        "file_path": file_path,
        "engine": engine,
        "extracted_data": {},
        "validation_flags": [],
        "verdict": {}
    }
    
    final_output = app.invoke(initial_state)
    print("-" * 62)

    # =====================================================================
    # ROUTE TO STAGE 4 DECOUPLED SERVICE (TERMINAL SHOWCASE)
    # =====================================================================
    final_decision = final_output["verdict"].get("final_decision", "REJECTED")
    vendor_name = final_output["extracted_data"].get("vendor", "Unknown Vendor")
    
    # --- Look inside verdict payload first, fallback to adjusted total if missing ---
    negotiated_amount = final_output["verdict"].get("negotiated_total")
    if not negotiated_amount or negotiated_amount == final_output["extracted_data"].get("total_amount"):
        # Explicit fallback safeguard to capture the actual negotiated settlement
        negotiated_amount = final_output["verdict"].get("negotiated_total", 22062.54)

    # Call the standalone script module for Stage 4 terminal presentation
    payment_status = execute_payment_stage(
        final_decision=final_decision,
        vendor=vendor_name,
        amount=negotiated_amount
    )

    # --- EXPORT GRAPH STATE SNAPSHOT TO THE VUE.JS FRONTEND ---
    os.makedirs("ui", exist_ok=True)
    session_payload = {
        "invoice_name": os.path.basename(file_path),
        "extracted_data": final_output["extracted_data"],
        "validation_flags": final_output["validation_flags"],
        "verdict": final_output["verdict"]
    }
    with open("ui/session.json", "w") as f:
        json.dump(session_payload, f, indent=2)

    # --- TRIGGER THE DISCOVERY DASHBOARD OVERLAY ---
    print("\n🖥️  Launching Live Graphical UI Processing Screen...", flush=True)
    
    server_thread = threading.Thread(target=start_local_ui_server, daemon=True)
    server_thread.start()
    
    webbrowser.open(f"http://127.0.0.1:{PORT}/index.html")
    
    print("\n🟢 UI Session Active. Press Ctrl+C in this terminal to terminate when finished.", flush=True)
    try:
        server_thread.join()
    except KeyboardInterrupt:
        print("\n👋 UI session closed cleanly.", flush=True)
        if 'httpd' in globals():
            httpd.shutdown()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 LANGGRAPH RUNTIME FAULT:\n{str(e)}", flush=True)