# main.py
import argparse
import os
import json
import webbrowser
import http.server
import socketserver
import threading
from llm_factory import LLMProviderEngine
from stage1_ingestion import execute_ingestion_stage
from stage2_validation import execute_validation_stage
from stage3_approval import execute_approval_stage

PORT = 8000

def start_local_ui_server():
    """Spins up a lightweight background web server targeting the ui folder."""
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            return  # Suppress standard logging traffic in terminal window

    os.chdir("ui")
    with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
        httpd.serve_forever()

def main():
    parser = argparse.ArgumentParser(description="Galatiq AP Multi-Agent Orchestrator Pipeline")
    parser.add_argument("--invoice_path", required=True, help="Local path to invoice file.")
    args = parser.parse_args()

    file_path = args.invoice_path
    if not os.path.exists(file_path):
        print(f"❌ Error: Targeted file path does not exist: {file_path}", flush=True)
        return

    # --- STAGE 0: CONNECTIVITY CHECK ---
    print("\n--- STAGE 0: CLIENT CONNECTIVITY CHECK ---", flush=True)
    engine = LLMProviderEngine()
    
    # --- STAGE 1: INGESTION PIPELINE ---
    print("\n--- STAGE 1: INGESTION PIPELINE NODE ---", flush=True)
    extracted_data = execute_ingestion_stage(file_path, engine)

    # --- STAGE 2: VALIDATION PIPELINE ---
    print("\n--- STAGE 2: VALIDATION PIPELINE NODE ---", flush=True)
    system_flags = execute_validation_stage(extracted_data)

    # --- STAGE 3: EXECUTIVE VP REFLCTION APPROVAL PIPELINE ---
    print("\n--- STAGE 3: MULTI-AGENT APPROVAL CRITIQUE NODE ---", flush=True)
    verdict = execute_approval_stage(file_path, extracted_data, system_flags, engine)
    print("-" * 62)

    # --- SAVE ENHANCED SNAPSHOT FOR VUE.JS FRONTEND ---
    os.makedirs("ui", exist_ok=True)
    session_payload = {
        "invoice_name": os.path.basename(file_path),
        "extracted_data": extracted_data,
        "validation_flags": system_flags,
        "verdict": verdict
    }
    with open("ui/session.json", "w") as f:
        json.dump(session_payload, f, indent=2)

    # --- LAUNCH GRAPHICAL MONITOR LAYER ---
    print("\n🖥️  Launching Live Graphical UI Processing Screen...", flush=True)
    
    server_thread = threading.Thread(target=start_local_ui_server, daemon=True)
    server_thread.start()
    
    webbrowser.open(f"http://127.0.0.1:{PORT}/index.html")
    
    print("\n🟢 UI Session Active. Press Ctrl+C in this terminal to terminate when finished.", flush=True)
    try:
        server_thread.join()
    except KeyboardInterrupt:
        print("\n👋 UI session closed cleanly.", flush=True)

if __name__ == "__main__":
    try:
        print("[START] Multi-Agent Processing Sequence Activated.", flush=True)
        main()
    except Exception as e:
        print(f"\n💥 PIPELINE EXCEPTION:\n{str(e)}", flush=True)