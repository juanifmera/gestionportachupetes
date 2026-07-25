"""Nombres de tablas de BigQuery.

Los modelos ORM fueron eliminados: BigQuery se consulta mediante SQL parametrizado.
"""

from database.client import table

MATERIALES = table("materiales")
STOCK = table("stock")
PEDIDOS = table("pedidos")
MATERIALES_PEDIDOS = table("materiales_pedidos")
MOVIMIENTOS_STOCK = table("movimientos_stock")
