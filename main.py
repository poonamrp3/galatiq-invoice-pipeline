# main.py
import argparse
import os
import json
import webbrowser
import http.server
import socketserver
import threading

# Import your underlying proxy engine and decoupled pipeline stages
from llm_factory import LLMProviderEngine
from stage1_ingestion import execute_ingestion_stage
from stage2_validation import execute_validation_stage
from stage3_approval import execute_approval_stage
from stage4_payment import execute_payment_stage  # <--- NEW DECOUPLED IMPORT

# Local UI server port designation
PORT = 8000

def start_local_ui_server():
    """Spins up a lightweight background web server targeting the ui folder."""
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            return  # Suppress browser request traffic noise in terminal

    os.chdir("ui")
    socketserver.TCPServer.allow_reuse_address = True
    
    global httpd
    with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
        try:
            httpd.serve_forever()
        except Exception:
            pass

def main():
    parser = argparse.ArgumentParser(description="Galatiq Autonomous Invoice Processing Pipeline")
    parser.add_argument("--invoice_path", required=True, help="Local path to invoice file.")
    args = parser.parse_args()

    file_path = args.invoice_path
    if not os.path.exists(file_path):
        print(f"❌ Error: Targeted file path does not exist: {file_path}", flush=True)
        return

    # Initialize your factory engine (hooks onto active .env choices)
    engine = LLMProviderEngine()

    # -----------------------------------------------------------------
    # STAGE 1: DATA INGESTION & EXTRACTION
    # -----------------------------------------------------------------
    print("\n[START] Executing Stage 1: LLM Document Ingestion...", flush=True)
    extracted_data = execute_ingestion_stage(file_path, engine)

    # -----------------------------------------------------------------
    # STAGE 2: SQL DATABASE STOCK VALIDATION
    # -----------------------------------------------------------------
    print("\n[START] Executing Stage 2: SQLite Inventory Integrity Check...", flush=True)
    validation_flags = execute_validation_stage(extracted_data)

    # -----------------------------------------------------------------
    # STAGE 3: MULTI-AGENT ADVERSARIAL APPROVAL NEGOTIATION
    # -----------------------------------------------------------------
    print("\n[START] Executing Stage 3: Executive Reflection Review & Negotiation...", flush=True)
    verdict_payload = execute_approval_stage(file_path, extracted_data, validation_flags, engine)
    print("-" * 66)

    # -----------------------------------------------------------------
    # STAGE 4: STANDALONE PAYMENT ROUTING ENGINE
    # -----------------------------------------------------------------
    final_decision = verdict_payload.get("final_decision", "REJECTED")
    vendor_name = extracted_data.get("vendor", "Unknown Vendor")
    negotiated_amount = verdict_payload.get("negotiated_total", 0.0)

    # Execute your new decoupled terminal payment showcase
    payment_status = execute_payment_stage(
        final_decision=final_decision,
        vendor=vendor_name,
        amount=negotiated_amount
    )

    # -----------------------------------------------------------------
    # EXPORT PIPELINE SNAPSHOT SNAPSHOT FOR VUE.JS FRONTEND
    # -----------------------------------------------------------------
    os.makedirs("ui", exist_ok=True)
    session_payload = {
        "invoice_name": os.path.basename(file_path),
        "extracted_data": extracted_data,
        "validation_flags": validation_flags,
        "verdict": verdict_payload
    }
    with open("ui/session.json", "w") as f:
        json.dump(session_payload, f, indent=2)

    # -----------------------------------------------------------------
    # TRIGGER DISCOVERY DASHBOARD OVERLAY SERVER
    # -----------------------------------------------------------------
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
        print(f"\n💥 SYSTEM PIPELINE ERROR:\n{str(e)}", flush=True)