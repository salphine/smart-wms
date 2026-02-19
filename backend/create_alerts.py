import sqlite3
from datetime import datetime

conn = sqlite3.connect('wms.db')
cursor = conn.cursor()

print('Creating reorder alerts...')

# First, make sure the reorder_alerts table exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS reorder_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    current_quantity INTEGER NOT NULL,
    reorder_point INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (id)
)
''')

# Get current inventory levels with product details
inventory = cursor.execute('''
SELECT 
    p.id,
    p.name,
    p.reorder_point,
    p.reorder_quantity,
    COUNT(i.id) as current_quantity
FROM products p
LEFT JOIN inventory_items i ON p.id = i.product_id AND i.status = 'in_stock'
GROUP BY p.id, p.name, p.reorder_point, p.reorder_quantity
''').fetchall()

print('\nCurrent Inventory Levels:')
for item in inventory:
    needs_reorder = 'YES' if item[4] <= item[2] else 'NO'
    print(f'  {item[1]}: {item[4]} units (reorder at {item[2]}) - Needs reorder: {needs_reorder}')

# Clear existing pending alerts
cursor.execute("DELETE FROM reorder_alerts WHERE status = 'pending'")
print('\nCleared existing pending alerts')

# Create new alerts for products below reorder point
alerts_created = 0
for item in inventory:
    if item[4] <= item[2]:  # if current quantity <= reorder point
        cursor.execute('''
        INSERT INTO reorder_alerts (product_id, current_quantity, reorder_point, status, created_at)
        VALUES (?, ?, ?, 'pending', ?)
        ''', (item[0], item[4], item[2], datetime.now()))
        alerts_created += 1
        print(f'  ✓ Alert created for {item[1]}')

conn.commit()

# Verify alerts were created
alerts = cursor.execute('''
SELECT ra.*, p.name 
FROM reorder_alerts ra
JOIN products p ON ra.product_id = p.id
WHERE ra.status = 'pending'
''').fetchall()

print(f'\n✅ Total alerts created: {len(alerts)}')
for alert in alerts:
    print(f'  Alert for {alert[5]}: {alert[2]} units (reorder at {alert[3]})')

conn.close()
