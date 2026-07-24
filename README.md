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

## Usuarios de la aplicación

Copiar la plantilla privada:

```powershell
cd sistema_portachupetes
copy .streamlit\secrets.example.toml .streamlit\secrets.toml
```

Generar el hash de la contraseña elegida:

```powershell
python -c "import streamlit_authenticator as stauth; print(stauth.Hasher.hash('TU_CONTRASEÑA'))"
```

Pegar el resultado en `password` y reemplazar también la clave de la cookie.
`secrets.toml` está ignorado por Git y nunca debe publicarse.
