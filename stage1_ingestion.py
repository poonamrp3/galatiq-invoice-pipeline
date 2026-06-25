# stage1_ingestion.py
import os
from typing import List, Optional
from pydantic import BaseModel, Field
from llm_factory import LLMProviderEngine

# =====================================================================
# STRATEGIC REASONING SCHEMAS
# =====================================================================
class OperationalReasoning(BaseModel):
    urgency_score: int = Field(description="Scale 1 to 5 (5 being critical). Factor in tight due dates, payment terms, or phrases in notes.")
    payment_priority: str = Field(description="ENUM: 'IMMEDIATE', 'STANDARD', or 'DEFERRABLE'.")
    days_to_settlement: int = Field(description="Calculated buffer days left based on current timeline and payment terms.")
    action_required_memo: str = Field(description="Explicit actionable instruction from notes or terms (e.g., 'Call admin contact John Doe').")

class InvoiceItem(BaseModel):
    name: str = Field(description="The clean name of the product or service.")
    quantity: int = Field(description="Integer quantity ordered. Converts typos like 'O' to 0.")
    unit_price: float = Field(description="The price per single unit as a float.")

class ComprehensiveInvoice(BaseModel):
    vendor: str = Field(description="The clear, standardized issuing company name.")
    invoice_number: str = Field(description="The parsed unique identification tracking number.")
    date: str = Field(description="The issue date standardized to YYYY-MM-DD.")
    due_date: str = Field(description="The due date standardized to YYYY-MM-DD.")
    items: List[InvoiceItem] = Field(description="The breakdown list of line item rows.")
    subtotal: Optional[float] = Field(None)
    tax: Optional[float] = Field(None)
    total_amount: float = Field(description="The final grand total sum.")
    currency: str = Field(default="USD")
    payment_terms: Optional[str] = Field(None, description="Payment expectations parameter (e.g., 'Net 30').")
    notes: Optional[str] = Field(None, description="Any miscellaneous comments or remarks found.")
    
    # THE REASONING ENGINE HOOK
    strategic_routing: OperationalReasoning = Field(description="Advanced reasoning evaluating payment terms, notes, and dates to determine operational priority.")

# =====================================================================
# CORE INGESTION WORKFLOW STEP
# =====================================================================
def execute_ingestion_stage(file_path: str, engine: LLMProviderEngine) -> dict:
    """
    Executes Stage 1 Ingestion: Passes the file to the LLM and extracts
    the ideal structure alongside explicit contextual note/terms reasoning.
    """
    # Simulated current system date context for date buffer math (June 2026)
    current_date_sim = "2026-06-24"

    system_instruction = f"""
    You are an expert strategic accounts payable router. Analyze the attached document and parse fields cleanly.
    
    CRITICAL AGENTIC REASONING TASK:
    You must evaluate the `payment_terms`, `notes`, and `due_date` compared to the current simulated system date ({current_date_sim}) to formulate the `strategic_routing` object:
    
    1. PAYMENT TERMS EVALUATION: 
       - 'Due on Receipt' or 'Net 0' means high urgency. Payment Priority must be 'IMMEDIATE'.
       - 'Net 15', 'Net 30' or 'Net 60' provides buffer room. Set Payment Priority to 'STANDARD' or 'DEFERRABLE'.
    2. NOTES ANALYSIS:
       - Inspect notes for words like 'urgent', 'expedited', 'late fees', or administrative directives (e.g., 'Call person X'). 
       - If a specific note says to call someone or flag an item, synthesize a clear operational workflow inside `action_required_memo`.
    """

    user_prompt = "Process the attached invoice and translate its components into our target ideal JSON contract."

    extracted_data = engine.get_structured_json_from_file(
        file_path=file_path,
        system_instruction=system_instruction,
        user_prompt=user_prompt,
        response_schema=ComprehensiveInvoice
    )

    return extracted_data