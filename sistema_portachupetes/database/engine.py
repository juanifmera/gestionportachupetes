"""Compatibilidad temporal: el proyecto ahora utiliza BigQuery."""

from database.client import get_client

engine = get_client()
