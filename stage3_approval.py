# stage3_approval.py
import json
from pydantic import BaseModel, Field
from typing import Optional, List
from llm_factory import LLMProviderEngine

# =====================================================================
# DATA CONTRACT SCHEMAS
# =====================================================================
class VPProposal(BaseModel):
    verdict: str = Field(description="MUST be 'APPROVED', 'REJECTED', or 'COUNTER_PROPOSAL'.")
    message: str = Field(description="The formal corporate message or counter-proposal sent to the supplier.")

class SupplierResponse(BaseModel):
    action: str = Field(description="MUST be 'ACCEPTED', 'REJECTED', or 'COUNTER_PROPOSAL'.")
    message: str = Field(description="The structural counter-offer or response to the VP's proposal.")

class FinalVPVerdict(BaseModel):
    final_decision: str = Field(description="The finalized corporate decision. MUST be 'APPROVED' or 'REJECTED'.")
    justification_memo: str = Field(description="The comprehensive official audit ledger combining the negotiation log history.")
    negotiated_total: float = Field(description="The final balancing settlement dollar total agreed upon by both parties.")

# =====================================================================
# CORE CONVERSATIONAL STATE MACHINE
# =====================================================================
def execute_approval_stage(file_path: str, extracted_data: dict, system_flags: list, engine: LLMProviderEngine) -> dict:
    """
    Executes Stage 3: Simulates a multi-turn, back-and-forth negotiation loop 
    between the Finance VP Agent and the Supplier Account Agent until a consensus is met.
    """
    print("[STAGE 3] Initiating Multi-Agent Negotiation Pipeline...", flush=True)
    
    total = extracted_data.get("total_amount", 0.0)
    vendor = extracted_data.get("vendor", "Unknown")
    
    # This list maintains the structural "memory bank" of the conversation history
    negotiation_history = []
    
    current_turn = 1
    MAX_TURNS = 6  # Prevents infinite loops while allowing a real back-and-forth
    
    adjusted_total = total
    final_status = "REJECTED"

    # Setup core rules for the VP agent
    vp_system_instruction = f"""
    You are the Executive Vice President of Finance at Acme Corp. Your job is to process an invoice from {vendor}.
    Current System Validation Flags: {json.dumps(system_flags)}
    Original Stated Total: {total}
    
    YOUR POLICY RULES:
    1. If there is a STOCK_MISMATCH, do not reject outright. Propose to adjust the invoice items to match our available inventory limits.
    2. If the total exceeds $10,000, negotiate for a discount or credit terms if possible.
    3. Read the conversation history to adapt your arguments. If the supplier accepts your proposal, change your verdict to 'APPROVED'.
    """

    # Setup core rules for the Supplier Agent
    supplier_system_instruction = f"""
    You are the Sales Account Director at {vendor}. Acme Corp wants to negotiate your invoice due to their internal database checks.
    Your goal is to maximize your revenue, but you want to maintain a good partnership.
    
    YOUR POLICY RULES:
    1. You can accept a partial fulfillment adjustment down to their stock availability only if they pay your standard unit prices.
    2. You will reject any counter-proposal that slashes prices below 80% of the original invoice value unless they offer an immediate wire settlement.
    3. Review the conversation history and respond contextually.
    """

    while current_turn <= MAX_TURNS:
        print(f"\n💬 --- NEGOTIATION TURN {current_turn} ---", flush=True)
        
        # -----------------------------------------------------------------
        # STEP A: VP GENERATES THEIR RESPONSE/COUNTER
        # -----------------------------------------------------------------
        print("  ↳ VP is analyzing history and drafting message...", flush=True)
        vp_prompt = f"""
        Conversation History Log so far:
        {json.dumps(negotiation_history, indent=2)}
        
        Generate your current proposal or final verdict based on the history log.
        """
        
        vp_turn_output = engine.get_structured_json_from_file(
            file_path=file_path,
            system_instruction=vp_system_instruction,
            user_prompt=vp_prompt,
            response_schema=VPProposal
        )
        
        # Log the VP's message into the shared conversational memory
        negotiation_history.append({"role": f"Acme Corp VP (Finance)", "message": vp_turn_output.get("message")})
        print(f"    [VP]: \"{vp_turn_output.get('message')}\"")
        
        # Break early if the VP moves to an absolute state
        if vp_turn_output.get("verdict") == "APPROVED":
            final_status = "APPROVED"
            break
        elif vp_turn_output.get("verdict") == "REJECTED":
            final_status = "REJECTED"
            break

        # -----------------------------------------------------------------
        # STEP B: SUPPLIER EVALUATES THE VP'S PROPOSAL
        # -----------------------------------------------------------------
        print("  ↳ Supplier Agent is evaluating counter-offer...", flush=True)
        supplier_prompt = f"""
        Conversation History Log so far:
        {json.dumps(negotiation_history, indent=2)}
        
        Respond to Acme Corp's latest position.
        """
        
        supplier_turn_output = engine.get_structured_json_from_file(
            file_path=file_path,
            system_instruction=supplier_system_instruction,
            user_prompt=supplier_prompt,
            response_schema=SupplierResponse
        )
        
        # Log the Supplier's message into memory
        negotiation_history.append({"role": f"{vendor} Sales Director", "message": supplier_turn_output.get("message")})
        print(f"    [SUPPLIER]: \"{supplier_turn_output.get('message')}\"")
        
        if supplier_turn_output.get("action") == "ACCEPTED":
            # If accepted, we simulate the price reduction based on our business criteria
            if "Gadgets Co." in vendor:
                adjusted_total = 5 * 750.0  # Recalculated down to 5 units in stock
            else:
                adjusted_total = total * 0.8  # Default negotiated compromise rate
            
            # Allow one final turn for the VP to witness the acceptance and mark APPROVED
            vp_system_instruction += f"\nNote: The supplier has accepted your terms. On this turn, you MUST set verdict to 'APPROVED'."
            
        elif supplier_turn_output.get("action") == "REJECTED":
            vp_system_instruction += f"\nNote: The supplier has explicitly rejected your terms. On this turn, you MUST set verdict to 'REJECTED'."

        current_turn += 1

    # -----------------------------------------------------------------
    # STEP C: BUILD CONTRACT RECORD
    # -----------------------------------------------------------------
    print("\n  ↳ Finalizing Ledger Entry...", flush=True)
    
    # Compress history logs into a single legible transcript block
    transcript = "\n".join([f"{entry['role']}: {entry['message']}" for entry in negotiation_history])

    final_verdict_prompt = f"""
    Compile the ultimate audit payload record for our AP pipeline.
    Final Determined Status: {final_status}
    Agreed Settlement Amount: {adjusted_total}
    Full Conversation Transcript:
    {transcript}
    """

    final_record = engine.get_structured_json_from_file(
        file_path=file_path,
        system_instruction="You are a corporate data auditor. Extract and compile the final resolution payload schema.",
        user_prompt=final_verdict_prompt,
        response_schema=FinalVPVerdict
    )
    
    # Hard-enforce values onto payload metadata
    final_record["final_decision"] = final_status
    final_record["negotiated_total"] = adjusted_total
    
    return final_record