# 4. Administración de pedidos

**Necesidad:** registrar pedidos, consultar estados y organizar la atención y el despacho.

**Estado:** diseñado, pendiente de implementación.

## Estructuras elegidas

| Dato | Estructura | Uso |
| --- | --- | --- |
| Pedidos en espera | `deque[Pedido]` (**cola FIFO**) | Atención por orden de llegada. |
| Índice de pedidos | `dict[str, Pedido]` (clave = `pedido_id`) | Consulta de estado por ID. |
| Historial de estados | `list[Estado]` por pedido, usado como **pila** | Deshacer el último cambio de estado. |

Ciclo previsto: `RECIBIDO → PREPARANDO → LISTO → DESPACHADO` (con `CANCELADO` como salida alternativa).

## Por qué estas estructuras

- La cola FIFO representa la regla de atención justa: quien pide primero, se prepara primero; `popleft()` es `O(1)`.
- El diccionario resuelve la consulta frecuente "¿en qué estado está el pedido X?" sin recorrer la cola (que además se va vaciando).
- La pila de estados permite corregir un cambio mal registrado volviendo exactamente al estado anterior (`pop()`), algo que una cola no haría.

## Por qué no otras

- Una **lista con `pop(0)`** para la cola desplaza todos los elementos: `O(n)` por pedido atendido. Con `deque` es `O(1)`.
- Un **heap por prioridad** no aplica: el caso no define prioridades de clientes ni urgencias, solo orden de llegada. Introducir prioridad sería inventar una regla de negocio.
- Una **cola para el historial** devolvería el estado más antiguo al deshacer, no el inmediatamente anterior.

## Operaciones previstas y complejidad

| Operación | Complejidad |
| --- | --- |
| `crear_pedido(cliente_id, items)` | `O(k)` ítems + `O(1)` encolado |
| `consultar_estado(pedido_id)` | `O(1)` |
| `atender_siguiente()` | `O(1)` (`popleft`) + transición de estado |
| `cambiar_estado(pedido_id, nuevo)` | `O(1)` + validación de transición |
| `deshacer_ultimo_cambio(pedido_id)` | `O(1)` (`pop`) |
| `pedidos_pendientes()` | `O(n)` sobre la cola |

## Validaciones

- Pedido sin ítems o con cantidades inválidas; cliente o SKU inexistente.
- Transiciones inválidas (por ejemplo, `RECIBIDO → DESPACHADO` sin preparación).
- Consulta de un `pedido_id` inexistente y atención con cola vacía: mensajes explícitos.
- Pila de historial vacía al deshacer; mantener coherente la cola si un pedido se cancela.

## Datos de prueba sugeridos

`PED-001` (CLI-01, 2 × MANG-01), `PED-002` (CLI-02, 1 × GUAN-01), `PED-003` (CLI-01, 3 × MANG-02). Demostración: encolar los tres, atender `PED-001`, consultar su estado, cambiar a `LISTO`, deshacer el cambio.
