# setup_db.py
import sqlite3
import os

def init_db():
    db_name = 'inventory.db'
    
    # Clean up old database file if it exists to ensure a fresh, predictable seed state
    if os.path.exists(db_name):
        os.remove(db_name)
        print(f"Removed existing stale {db_name} file.")

    # Establish a persistent connection to the local SQLite file
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    print("Creating 'inventory' table schema...")
    # item: string primary key matching invoice line items
    # stock: current quantity available in warehouse inventory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            item TEXT PRIMARY KEY, 
            stock INTEGER NOT NULL
        )
    ''')
    
    # Injecting core testing matrix seeds as specified by the case requirements
    print("Seeding initial inventory records...")
    cursor.execute("""
        INSERT INTO inventory (item, stock) VALUES
        ('WidgetA', 15),
        ('WidgetB', 10),
        ('GadgetX', 5),
        ('FakeItem', 0)
    """)
    
    # Save transactions and close connections safely
    conn.commit()
    
    # Quick verification trace to ensure tables wrote successfully
    cursor.execute("SELECT * FROM inventory")
    records = cursor.fetchall()
    
    print("\nDatabase initialization complete. Current Verified Inventory State:")
    print("-" * 55)
    for row in records:
        print(f" Item: {row[0]:<12} | Available Warehouse Stock: {row[1]}")
    print("-" * 55)
    
    conn.close()

if __name__ == "__main__":
    init_db()