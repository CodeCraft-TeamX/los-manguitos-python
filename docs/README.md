# Decisiones de diseño — Estructuras de datos

Este directorio documenta, **antes de implementarlas**, las estructuras de datos previstas para cada una de las seis funcionalidades del caso Los Manguitos. Cada archivo responde: qué problema resuelve, por qué la estructura elegida es adecuada, por qué no otra, qué operaciones expone y qué validaciones deben acompañarla.

Estado actual: **diseñado / pendiente de implementación**.

| # | Funcionalidad | Estructuras previstas | Detalle |
| --- | --- | --- | --- |
| 1 | Productos e inventario | Diccionario, lista, recursividad | [01-productos-inventario.md](01-productos-inventario.md) |
| 2 | Bodegas y sucursales | Diccionario anidado, cola FIFO | [02-bodegas-sucursales.md](02-bodegas-sucursales.md) |
| 3 | Clientes y ventas | Diccionario, lista, pila LIFO | [03-clientes-ventas.md](03-clientes-ventas.md) |
| 4 | Pedidos | Cola FIFO, diccionario, pila de estados | [04-pedidos.md](04-pedidos.md) |
| 5 | Logística y distribución | Grafo, BFS/Dijkstra, recursividad DFS | [05-logistica-distribucion.md](05-logistica-distribucion.md) |
| 6 | Seguimiento de operaciones | Lista de eventos, índice por tipo, árbol | [06-seguimiento-operaciones.md](06-seguimiento-operaciones.md) |

## Principios comunes

- Toda estructura debe responder una necesidad real del negocio; no se incluye una sola "por cumplir el requisito".
- Las claves de consulta son identificadores estables (`sku`, `cliente_id`, `pedido_id`, `ubicacion`).
- Las entradas inválidas y las operaciones sobre estructuras vacías se validan antes de mutar el estado.
- Los eventos de seguimiento se registran con `append`, nunca se reescriben.
