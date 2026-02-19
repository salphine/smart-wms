import sqlite3
import os

print("Initializing database...")

db_path = 'wms.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Removed existing database: {db_path}")

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
    status TEXT DEFAULT 'in_stock' CHECK (status IN ('in_stock', 'reserved', 'shipped', 'damaged')),
    location_zone TEXT NOT NULL,
    last_scanned_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (id)
);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfid_tag TEXT,
    action TEXT NOT NULL,
    location TEXT,
    scanned_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rfid_tag) REFERENCES inventory_items (rfid_tag)
);

CREATE TABLE reorder_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    current_quantity INTEGER NOT NULL,
    reorder_point INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'ordered', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (id)
);
''')

# Insert sample products
print("Adding sample products...")
cursor.executemany('''
INSERT INTO products (sku, name, description, reorder_point, reorder_quantity, unit_price)
VALUES (?, ?, ?, ?, ?, ?)
''', [
    ('LAP001', 'Dell XPS 13', '13-inch laptop, 16GB RAM', 3, 10, 999.99),
    ('MOU001', 'Logitech MX Master 3', 'Wireless mouse', 5, 20, 79.99),
    ('KEY001', 'Mechanical Keyboard', 'RGB mechanical keyboard', 4, 15, 129.99),
    ('MON001', 'Samsung 27" Monitor', '4K UHD Monitor', 2, 5, 299.99)
])

# Insert sample inventory items
print("Adding sample inventory items...")
cursor.executemany('''
INSERT INTO inventory_items (rfid_tag, product_id, location_zone)
VALUES (?, ?, ?)
''', [
    ('RFID001', 1, 'Aisle A-01'),
    ('RFID002', 1, 'Aisle A-01'),
    ('RFID003', 2, 'Aisle B-02'),
    ('RFID004', 2, 'Aisle B-02'),
    ('RFID005', 3, 'Aisle C-01'),
    ('RFID006', 4, 'Aisle D-03')
])

conn.commit()

# Verify the data
print("\\nVerifying data...")
products = cursor.execute("SELECT COUNT(*) FROM products").fetchone()[0]
items = cursor.execute("SELECT COUNT(*) FROM inventory_items").fetchone()[0]
print(f"Products added: {products}")
print(f"Inventory items added: {items}")

conn.close()
print("\\n✅ Database initialized successfully!")
print("Sample data ready to use!")
