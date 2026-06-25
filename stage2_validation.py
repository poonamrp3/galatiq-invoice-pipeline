# stage2_validation.py
import sqlite3
from typing import List, Dict, Any

def execute_validation_stage(extracted_data: Dict[str, Any]) -> List[str]:
    """
    Executes Stage 2 Validation: Audits data integrity, cross-checks line items 
    with SQLite inventory stock levels, and enforces strict mathematical arithmetic 
    guardrails across subtotals, tax rate applications, and grand totals.
    """
    print("[STAGE 2] Running validation compliance checks...", flush=True)
    flags = []

    items = extracted_data.get("items", [])
    
    # Extract structural ledger fields cleanly (with safety defaults)
    stated_subtotal = extracted_data.get("subtotal") or 0.0
    stated_tax_rate = extracted_data.get("tax_rate") or 0.0
    stated_tax_amount = extracted_data.get("tax_amount") or 0.0
    stated_shipping = extracted_data.get("shipping_amount") or 0.0
    stated_total = extracted_data.get("total_amount") or 0.0

    # Connect to your local seeded database
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    calculated_items_subtotal = 0.0

    for item in items:
        name = item.get("name")
        quantity = item.get("quantity", 0)
        unit_price = item.get("unit_price", 0.0)

        # 1. DATA INTEGRITY CHECK (e.g., Negative Quantity Guardrail)
        if quantity <= 0:
            flags.append(f"DATA_INTEGRITY_ISSUE: Item '{name}' has an invalid or negative quantity: {quantity}.")
            continue

        # Aggregate line totals for the mathematical subtotal proof
        calculated_items_subtotal += (quantity * unit_price)

        # Query the database for item verification
        cursor.execute("SELECT stock FROM inventory WHERE item = ?", (name,))
        row = cursor.fetchone()

        # 2. UNKNOWN ITEM CHECK
        if not row:
            flags.append(f"UNKNOWN_ITEM: Product '{name}' does not exist in the inventory database records.")
        else:
            stock_available = row[0]
            
            # 3. FRAUD / ZERO-STOCK CHECK
            if stock_available == 0:
                flags.append(f"FRAUD_ALERT: Invoice references '{name}' which has 0 available warehouse stock.")
            
            # 4. QUANTITY EXCEEDS STOCK CHECK
            elif quantity > stock_available:
                flags.append(f"STOCK_MISMATCH: Requested {quantity} units of '{name}', but only {stock_available} are in stock.")

    conn.close()

    # Float rounding delta tolerance threshold (1.0 currency unit)
    TOLERANCE = 1.0

    # 5. GUARDRAIL A: Verify Line Items Sum to the Stated Subtotal
    if stated_subtotal > 0.0 and abs(calculated_items_subtotal - stated_subtotal) > TOLERANCE:
        flags.append(
            f"MATH_MISMATCH: Stated subtotal is {stated_subtotal}, but individual item lines "
            f"calculate to {calculated_items_subtotal}."
        )

    # 6. GUARDRAIL B: Verify Tax Rate Percent Calculation Against Calculated Subtotal
    # Using calculated subtotal ensures tax fraud or extraction discrepancies are exposed
    expected_tax_amount = calculated_items_subtotal * stated_tax_rate
    if stated_tax_amount > 0.0 and abs(expected_tax_amount - stated_tax_amount) > TOLERANCE:
        flags.append(
            f"MATH_MISMATCH: Stated tax amount is {stated_tax_amount}, but applying the "
            f"tax rate of {stated_tax_rate * 100}% to the items subtotal yields {expected_tax_amount}."
        )

    # 7. GUARDRAIL C: Complete Ledger Balance Proof (Subtotal + Tax + Shipping = Total)
    # Uses our computed items subtotal plus extracted taxes and shipping
    calculated_grand_total = calculated_items_subtotal + stated_tax_amount + stated_shipping
    if abs(calculated_grand_total - stated_total) > TOLERANCE:
        flags.append(
            f"MATH_MISMATCH: Grand total states {stated_total}, but breaking down "
            f"calculated items subtotal ({calculated_items_subtotal}) + tax ({stated_tax_amount}) "
            f"+ shipping ({stated_shipping}) sums to {calculated_grand_total}."
        )

    # Present validation findings cleanly
    if flags:
        print(f"[STAGE 2 FAILED] {len(flags)} validation flags raised:")
        for flag in flags:
            print(f"  ⚠️  {flag}")
    else:
        print("[STAGE 2 PASSED] Order parameters verified within acceptable parameters.")

    return flags