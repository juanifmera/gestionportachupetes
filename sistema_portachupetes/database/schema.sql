-- Ejecutar en BigQuery con el proyecto hitobaby y ubicación us-east4.
CREATE OR REPLACE TABLE `hitobaby.hitobaby_dataset.materiales` (
  codigo_material STRING NOT NULL,
  descripcion STRING NOT NULL,
  color STRING NOT NULL,
  categoria STRING NOT NULL,
  subcategoria STRING NOT NULL,
  fecha_ingreso DATE NOT NULL,
  comentarios STRING,
  costo_unitario NUMERIC,
  activo BOOL NOT NULL,
  fecha_creacion TIMESTAMP NOT NULL,
  fecha_actualizacion TIMESTAMP NOT NULL
)
CLUSTER BY categoria, subcategoria, codigo_material;

CREATE OR REPLACE TABLE `hitobaby.hitobaby_dataset.stock` (
  codigo_material STRING NOT NULL,
  cantidad INT64 NOT NULL,
  fecha_modificacion TIMESTAMP NOT NULL
)
CLUSTER BY codigo_material;

CREATE OR REPLACE TABLE `hitobaby.hitobaby_dataset.pedidos` (
  id INT64 NOT NULL,
  cliente STRING NOT NULL,
  telefono STRING,
  fecha_pedido DATE NOT NULL,
  estado STRING NOT NULL,
  costo_total NUMERIC,
  precio_venta NUMERIC,
  tipo STRING NOT NULL,
  comentarios STRING,
  fecha_creacion TIMESTAMP NOT NULL,
  fecha_actualizacion TIMESTAMP NOT NULL
)
PARTITION BY fecha_pedido
CLUSTER BY estado, tipo;

CREATE OR REPLACE TABLE `hitobaby.hitobaby_dataset.materiales_pedidos` (
  detalle_id STRING NOT NULL,
  pedido_id INT64 NOT NULL,
  codigo_material STRING NOT NULL,
  cantidad_usada INT64 NOT NULL,
  costo_unitario NUMERIC,
  costo_total_material NUMERIC,
  fecha_creacion TIMESTAMP NOT NULL
)
CLUSTER BY pedido_id, codigo_material;

CREATE OR REPLACE TABLE `hitobaby.hitobaby_dataset.movimientos_stock` (
  movimiento_id STRING NOT NULL,
  codigo_material STRING NOT NULL,
  fecha_movimiento TIMESTAMP NOT NULL,
  tipo_movimiento STRING NOT NULL,
  cantidad INT64 NOT NULL,
  stock_anterior INT64,
  stock_resultante INT64,
  pedido_id INT64,
  comentario STRING,
  usuario STRING
)
PARTITION BY DATE(fecha_movimiento)
CLUSTER BY codigo_material, tipo_movimiento;
