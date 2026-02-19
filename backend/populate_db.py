import sqlite3
import os

db_path = 'wms.db'
print(f"Database path: {os.path.abspath(db_path)}")

# Remove existing database to start fresh (optional - comment out if you want to keep data)
if os.path.exists(db_path):
    print("Removing existing database...")
    os.remove(db_path)

print("Creating new database...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables
print("Creating tables...")
cursor.executescript('''
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    reorder_point INTEGER NOT NULL DEFAULT 10,
    reorder_quantity INTEGER NOT NULL DEFAULT 50,
    unit_price REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfid_tag TEXT UNIQUE NOT NULL,
    product_id INTEGER,
    status TEXT DEFAULT 'in_stock',
    location_zone TEXT NOT NULL,
    last_scanned_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (id)
);
''')

# Insert sample products
print("Adding sample products...")
products = [
    ('LAP001', 'Dell XPS 13', '13-inch laptop, 16GB RAM', 3, 10, 999.99),
    ('MOU001', 'Logitech MX Master 3', 'Wireless mouse', 5, 20, 79.99),
    ('KEY001', 'Mechanical Keyboard', 'RGB mechanical keyboard', 4, 15, 129.99),
    ('MON001', 'Samsung 27" Monitor', '4K UHD Monitor', 2, 5, 299.99)
]

for product in products:
    cursor.execute('''
    INSERT INTO products (sku, name, description, reorder_point, reorder_quantity, unit_price)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', product)
    print(f"  Added: {product[1]}")

# Insert sample inventory items
print("Adding sample inventory items...")
items = [
    ('RFID001', 1, 'Aisle A-01'),
    ('RFID002', 1, 'Aisle A-01'),
    ('RFID003', 2, 'Aisle B-02'),
    ('RFID004', 2, 'Aisle B-02'),
    ('RFID005', 3, 'Aisle C-01'),
    ('RFID006', 4, 'Aisle D-03')
]

for item in items:
    cursor.execute('''
    INSERT INTO inventory_items (rfid_tag, product_id, location_zone)
    VALUES (?, ?, ?)
    ''', item)
    print(f"  Added: {item[0]} at {item[2]}")

conn.commit()

# Verify
print("\nVerifying data...")
products_count = cursor.execute("SELECT COUNT(*) FROM products").fetchone()[0]
items_count = cursor.execute("SELECT COUNT(*) FROM inventory_items").fetchone()[0]
print(f"Products in database: {products_count}")
print(f"Inventory items in database: {items_count}")

# Show the data
print("\nProducts:")
for row in cursor.execute("SELECT id, sku, name, reorder_point FROM products"):
    print(f"  {row}")

print("\nInventory Items:")
for row in cursor.execute("SELECT rfid_tag, product_id, location_zone FROM inventory_items"):
    print(f"  {row}")

conn.close()
print("\n✅ Database populated successfully!")
