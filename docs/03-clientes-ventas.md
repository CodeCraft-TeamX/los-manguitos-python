# 3. Gestión de clientes y ventas

**Necesidad:** registrar clientes, productos vendidos, cantidades, precios y operaciones de venta.

**Estado:** diseñado, pendiente de implementación.

## Estructuras elegidas

| Dato | Estructura | Uso |
| --- | --- | --- |
| Clientes | `dict[str, Cliente]` (clave = `cliente_id`) | Alta y consulta rápida por identificador. |
| Ventas | `list[Venta]` (solo `append`) | Registro cronológico y auditoría. |
| Ventas por cliente | `dict[str, list[str]]` (`cliente_id -> venta_ids`) | Consulta del historial de un cliente sin recorrer todas las ventas. |
| Cancelaciones | `list[Venta]` usada como **pila LIFO** | Deshacer la última venta registrada y devolver el stock. |

## Por qué estas estructuras

- El cliente se consulta siempre por su ID: `dict` da `O(1)` y evita duplicados.
- Las ventas son un flujo append-only: la lista conserva el orden natural para reportes y no necesita inserciones por medio.
- La pila modela exactamente la operación "cancelar la última venta": `pop()` es `O(1)` y siempre devuelve la operación más reciente, que es la que se quiere revertir.

## Por qué no otras

- Un **diccionario para ventas** sería útil para consultar por ID, pero no aporta el orden cronológico que pide el informe; por eso se combina con la lista y un índice por cliente.
- Una **cola FIFO** para cancelaciones deshacería la venta más antigua, no la última: incorrecto para una corrección de registro.
- Un **árbol** ordenado por total de venta no responde ninguna pregunta del caso (no hay consultas por rangos de monto).

## Operaciones previstas y complejidad

| Operación | Complejidad |
| --- | --- |
| `registrar_cliente(cliente_id, ...)` | `O(1)` |
| `registrar_venta(cliente_id, items)` | `O(k)` sobre los ítems + descuento de stock |
| `consultar_ventas_cliente(cliente_id)` | `O(v)`, ventas de ese cliente |
| `cancelar_ultima_venta()` | `O(k)`: `pop()` + devolución de stock |
| `total_vendido()` | `O(n)` sobre el registro completo |

## Validaciones

- Cliente inexistente; venta sin ítems; cantidad `<= 0` o precio `<= 0`.
- Stock insuficiente: la venta se rechaza por completo (operación atómica, sin descuentos parciales).
- Pila vacía al cancelar: mensaje claro, sin `IndexError`.
- No permitir cancelar dos veces la misma venta (se marca como cancelada en el registro).

## Datos de prueba sugeridos

Clientes `CLI-01` (persona natural) y `CLI-02` (empresa). Venta `VEN-001`: 2 × `MANG-01` a 25.000 c/u para `CLI-01`; venta `VEN-002`: 1 × `GUAN-01` a 18.000 para `CLI-02`.
