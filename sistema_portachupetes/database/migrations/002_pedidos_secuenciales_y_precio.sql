-- Ejecutar una sola vez sobre el dataset existente.
ALTER TABLE `hitobaby.hitobaby_dataset.pedidos`
ADD COLUMN IF NOT EXISTS precio_venta NUMERIC;

CREATE TEMP TABLE mapa_pedidos AS
SELECT
  id AS id_anterior,
  ROW_NUMBER() OVER (ORDER BY fecha_creacion, id) AS id_nuevo
FROM `hitobaby.hitobaby_dataset.pedidos`;

BEGIN TRANSACTION;

MERGE `hitobaby.hitobaby_dataset.materiales_pedidos` AS detalle
USING mapa_pedidos AS mapa
ON detalle.pedido_id = mapa.id_anterior
WHEN MATCHED THEN
  UPDATE SET pedido_id = mapa.id_nuevo;

MERGE `hitobaby.hitobaby_dataset.movimientos_stock` AS movimiento
USING mapa_pedidos AS mapa
ON movimiento.pedido_id = mapa.id_anterior
WHEN MATCHED THEN
  UPDATE SET pedido_id = mapa.id_nuevo;

MERGE `hitobaby.hitobaby_dataset.pedidos` AS pedido
USING mapa_pedidos AS mapa
ON pedido.id = mapa.id_anterior
WHEN MATCHED THEN
  UPDATE SET id = mapa.id_nuevo;

COMMIT TRANSACTION;
