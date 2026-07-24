-- Ejecutar una sola vez sobre el dataset existente.
ALTER TABLE `hitobaby.hitobaby_dataset.pedidos`
ADD COLUMN IF NOT EXISTS precio_venta NUMERIC;

CREATE TEMP TABLE mapa_pedidos AS
SELECT
  id AS id_anterior,
  ROW_NUMBER() OVER (ORDER BY fecha_creacion, id) AS id_nuevo
FROM `hitobaby.hitobaby_dataset.pedidos`;

BEGIN TRANSACTION;

UPDATE `hitobaby.hitobaby_dataset.materiales_pedidos` AS detalle
SET pedido_id = (
  SELECT id_nuevo
  FROM mapa_pedidos
  WHERE id_anterior = detalle.pedido_id
)
WHERE pedido_id IN (SELECT id_anterior FROM mapa_pedidos);

UPDATE `hitobaby.hitobaby_dataset.movimientos_stock` AS movimiento
SET pedido_id = (
  SELECT id_nuevo
  FROM mapa_pedidos
  WHERE id_anterior = movimiento.pedido_id
)
WHERE pedido_id IN (SELECT id_anterior FROM mapa_pedidos);

UPDATE `hitobaby.hitobaby_dataset.pedidos` AS pedido
SET id = (
  SELECT id_nuevo
  FROM mapa_pedidos
  WHERE id_anterior = pedido.id
)
WHERE id IN (SELECT id_anterior FROM mapa_pedidos);

COMMIT TRANSACTION;
