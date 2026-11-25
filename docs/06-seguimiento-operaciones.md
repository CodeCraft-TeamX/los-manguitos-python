# 6. Seguimiento de operaciones

**Necesidad:** mantener registros de movimientos de inventario, ventas, pedidos y despachos realizados.

**Estado:** diseñado, pendiente de implementación.

## Estructuras elegidas

| Dato | Estructura | Uso |
| --- | --- | --- |
| Registro de eventos | **Lista append-only** `list[Evento]` | Log cronológico inmutable; una sola fuente de verdad. |
| Índice por tipo | `dict[str, list[int]]` (`tipo -> posiciones`) | Filtrar movimientos/ventas/pedidos/despachos sin escanear todo. |
| Consultas por fecha | **Árbol binario de búsqueda** por `timestamp` | Reportes por rango temporal (`desde`, `hasta`) con recorrido recursivo in-order. |

Cada `Evento` lleva: `timestamp`, `tipo`, `id_operacion` y una descripción corta. Los módulos 1 a 5 emiten eventos hacia aquí.

## Por qué estas estructuras

- El log solo crece: `append` es `O(1)` amortizado y nunca se reescribe el pasado, lo que facilita auditoría.
- El índice por tipo evita recorrer todo el historial cuando el gerente pregunta solo por "despachos de hoy": se accede a las posiciones de ese tipo en `O(1)` y se visitan solo `k` eventos.
- El árbol mantiene los eventos ordenados por tiempo **mientras se insertan**, permitiendo consultas por rango sin ordenar cada vez. El recorrido in-order usa **recursividad**.

## Por qué no otras

- Un **diccionario plano** por ID no conserva el orden temporal ni permite rangos de fecha; necesitaría ordenar en cada consulta (`O(n log n)`).
- Una **pila** o una **cola** descartaría eventos al consultarlos: son estructuras de trabajo, no de auditoría; el historial completo debe permanecer.
- Una **lista ordenada con `bisect`** también resolvería los rangos y es más simple; se elige árbol para practicar inserciones dinámicas y recursividad, con la salvedad de que un ABB desbalanceado puede degradarse a `O(n)`. Si el volumen crece, se sustituye por un árbol balanceado (AVL) o un índice de base de datos.

## Operaciones previstas y complejidad

| Operación | Complejidad |
| --- | --- |
| `registrar_evento(tipo, id_operacion, descripcion)` | `O(1)` + `O(log n)` inserción en el árbol |
| `eventos_por_tipo(tipo)` | `O(k)` usando el índice |
| `eventos_entre(desde, hasta)` | `O(log n + k)` con árbol balanceado |
| `ultimos_eventos(n)` | `O(1)` acceso al final de la lista |
| `resumen_por_tipo()` | `O(t)` sobre los tipos registrados |

## Validaciones

- Evento sin tipo, sin ID de operación o con `timestamp` inválido.
- Tipos permitidos: `inventario`, `venta`, `pedido`, `despacho` (extensible).
- Log vacío e índices vacíos: devolver lista vacía con mensaje, no error.
- Correlación: todo evento debe apuntar a una operación existente en su módulo de origen.

## Datos de prueba sugeridos

Eventos: entrada de stock (`inventario`), `VEN-001` (`venta`), `PED-001` creado y despachado (`pedido`, `despacho`). Consulta de ejemplo: todos los eventos entre dos timestamps y conteo por tipo.
