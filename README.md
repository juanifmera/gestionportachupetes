# Gestión de portachupetes

Aplicación Streamlit para administrar materiales, stock y pedidos de Hito.
La persistencia utiliza BigQuery en:

- Proyecto: `hitobaby`
- Dataset: `hitobaby_dataset`
- Ubicación: `us-east4`

## Preparación de BigQuery

Las tablas existentes deben estar vacías antes de ejecutar el archivo
`sistema_portachupetes/database/schema.sql`, ya que el script las recrea con el
esquema requerido por la aplicación.

## Desarrollo local

```powershell
gcloud config configurations activate hito-baby
gcloud auth application-default login
gcloud auth application-default set-quota-project hitobaby
pip install -r sistema_portachupetes/requirements.txt
cd sistema_portachupetes
streamlit run app.py
```

La configuración puede cambiarse mediante:

```text
GCP_PROJECT_ID
BQ_DATASET_ID
BQ_LOCATION
```

No se deben guardar claves JSON ni secretos en el repositorio.
