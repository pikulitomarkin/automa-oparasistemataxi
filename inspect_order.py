import sqlite3
import json

DB = 'data/taxi_orders.db'
ORDER_ID = 8

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
print('Tables:', [r['name'] for r in cur.fetchall()])

cur.execute('PRAGMA table_info(orders)')
cols = [r['name'] for r in cur.fetchall()]
print('\nOrders columns:', cols)

cur.execute('SELECT * FROM orders WHERE id=?', (ORDER_ID,))
row = cur.fetchone()
if not row:
    print(f'Order {ORDER_ID} not found')
else:
    print(f'\nOrder {ORDER_ID}:')
    for k in row.keys():
        v = row[k]
        # try to pretty-print JSON fields
        try:
            parsed = json.loads(v)
            v = json.dumps(parsed, ensure_ascii=False, indent=2)
        except Exception:
            pass
        print(f' - {k}: {v}')

conn.close()
