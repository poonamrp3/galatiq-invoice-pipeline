# stage4_payment.py
import sys

def mock_payment(vendor: str, amount: float) -> dict:
    """
    Official required banking API routing function.
    """
    print(f"Paid {amount} to {vendor}")  # Matches exact required signature
    return {"status": "success"}

def execute_payment_stage(final_decision: str, vendor: str, amount: float) -> dict:
    """
    Executes Stage 4: Processes payment if approved, or logs audit rejection if blocked.
    All outputs showcase directly in the terminal window.
    """
    print("\n🏁 [STAGE 4: PAYMENT ROUTING ENGINE] Initializing Transaction Gate...", flush=True)
    
    if final_decision == "APPROVED":
        print("🟢 Authorization verified. Routing to payment API...", flush=True)
        print("=" * 66)
        
        # Invoke the required core assignment tracking snippet
        receipt = mock_payment(vendor, amount)
        
        # Enhanced terminal output visualization
        print(f"💰 SUCCESS: Settlement completed via mock banking rail.")
        print(f"   Recipient: {vendor}")
        print(f"   Amount:    ${amount:,.2f}")
        print("=" * 66, flush=True)
        return receipt
    else:
        print("❌ Authorization denied. Final VP decision state was REJECTED.", flush=True)
        print("=" * 66)
        print(f"🚨 PAYMENT BLOCKED: Accounts Payable Audit Gate Kept Open.")
        print(f"   Vendor:    {vendor}")
        print(f"   Reason:    Line item mismatch or counter-offer refusal.")
        print("=" * 66, flush=True)
        return {"status": "blocked", "reason": "Invoice was rejected by executive authority."}