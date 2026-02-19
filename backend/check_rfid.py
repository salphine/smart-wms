import sqlite3

conn = sqlite3.connect('wms.db')
cursor = conn.cursor()

print('RFID tags in database:')
try:
    rows = cursor.execute('SELECT rfid_tag, product_id, location_zone FROM inventory_items').fetchall()
    if rows:
        for row in rows:
            print(f'  {row[0]} (Product ID: {row[1]}, Location: {row[2]})')
    else:
        print('  No RFID tags found in database')
except sqlite3.OperationalError as e:
    print(f'Error: {e}')
    print('The inventory_items table might not exist')

conn.close()
