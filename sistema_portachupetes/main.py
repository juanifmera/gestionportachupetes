"""Comprueba la conexión y existencia de las tablas de BigQuery."""

from database.client import query, table

for nombre in ("materiales", "stock", "pedidos", "materiales_pedidos", "movimientos_stock"):
    query(f"SELECT 1 FROM {table(nombre)} LIMIT 1")
    print(f"OK: {nombre}")
