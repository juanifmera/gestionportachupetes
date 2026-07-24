"""Cliente y utilidades compartidas para BigQuery."""

from __future__ import annotations

import os
from functools import lru_cache

from google.cloud import bigquery

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "hitobaby")
DATASET_ID = os.getenv("BQ_DATASET_ID", "hitobaby_dataset")
LOCATION = os.getenv("BQ_LOCATION", "us-east4")


def table(name: str) -> str:
    return f"`{PROJECT_ID}.{DATASET_ID}.{name}`"


@lru_cache(maxsize=1)
def get_client() -> bigquery.Client:
    """Usa ADC localmente o la identidad del servicio en producción."""
    return bigquery.Client(project=PROJECT_ID, location=LOCATION)


def query(sql: str, parameters: list[bigquery.query.ScalarQueryParameter] | None = None):
    config = bigquery.QueryJobConfig(query_parameters=parameters or [])
    return get_client().query(sql, job_config=config, location=LOCATION).result()


def query_dataframe(
    sql: str,
    parameters: list[bigquery.query.ScalarQueryParameter] | None = None,
):
    config = bigquery.QueryJobConfig(query_parameters=parameters or [])
    return get_client().query(
        sql, job_config=config, location=LOCATION
    ).result().to_dataframe(create_bqstorage_client=False)

