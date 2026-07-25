"""Prueba manual mínima de conexión."""

from database.client import PROJECT_ID, DATASET_ID, LOCATION, query

query("SELECT 1")
print(f"Conexión exitosa: {PROJECT_ID}.{DATASET_ID} ({LOCATION})")
