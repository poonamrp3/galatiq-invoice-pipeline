# stage2_validation.py
import sqlite3
from typing import List, Dict, Any

def execute_validation_stage(extracted_data: Dict[str, Any]) -> List[str]:
    """
    Executes Stage 2 Validation: Audits data integrity, cross-checks 
    line items with SQLite inventory stock levels, and raises warning flags.
    """
    print("[STAGE 2] Running validation compliance checks...", flush=True)
    flags = []

    items = extracted_data.get("items", [])
    total_amount = extracted_data.get("total_amount", 0.0)

    # Connect to your local seeded database
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    calculated_subtotal = 0.0

    for item in items:
        name = item.get("name")
        quantity = item.get("quantity", 0)
        unit_price = item.get("unit_price", 0.0)

        # 1. DATA INTEGRITY CHECK (INV-1009 Scenario)
        if quantity <= 0:
            flags.append(f"DATA_INTEGRITY_ISSUE: Item '{name}' has an invalid or negative quantity: {quantity}.")
            continue

        calculated_subtotal += (quantity * unit_price)

        # Query the database for the item
        cursor.execute("SELECT stock FROM inventory WHERE item = ?", (name,))
        row = cursor.fetchone()

        # 2. UNKNOWN ITEM CHECK (INV-1008, INV-1016 Scenarios)
        if not row:
            flags.append(f"UNKNOWN_ITEM: Product '{name}' does not exist in the inventory database records.")
        else:
            stock_available = row[0]
            
            # 3. FRAUD / ZERO-STOCK CHECK (INV-1003 Scenario)
            if stock_available == 0:
                flags.append(f"FRAUD_ALERT: Invoice references '{name}' which has 0 available warehouse stock.")
            
            # 4. QUANTITY EXCEEDS STOCK CHECK (INV-1002 Scenario)
            elif quantity > stock_available:
                flags.append(f"STOCK_MISMATCH: Requested {quantity} units of '{name}', but only {stock_available} are in stock.")

    conn.close()

    # 5. MATHEMATICAL VERIFICATION CHECK
    if abs(calculated_subtotal - total_amount) > 1.0:
        flags.append(f"MATH_MISMATCH: Grand total states {total_amount}, but row items total {calculated_subtotal}.")

    # Present validation findings cleanly
    if flags:
        print(f"[STAGE 2 FAILED] {len(flags)} validation flags raised:")
        for flag in flags:
            print(f"  ⚠️  {flag}")
    else:
        print("[STAGE 2 PASSED] Order parameters verified within acceptable parameters.")

    return flags