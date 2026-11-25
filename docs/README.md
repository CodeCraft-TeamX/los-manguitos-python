# Decisiones de diseño — Estructuras de datos

Este directorio documenta, **antes de implementarlas**, las estructuras de datos previstas para cada una de las seis funcionalidades del caso Los Manguitos. Cada archivo responde: qué problema resuelve, por qué la estructura elegida es adecuada, por qué no otra, qué operaciones expone y qué validaciones deben acompañarla.

Estado actual: **implementado** en `src/`; este documento conserva la justificación técnica de cada decisión.

| # | Funcionalidad | Estructuras elegidas | Módulo | Detalle |
| --- | --- | --- | --- | --- |
| 1 | Productos e inventario | Diccionario, lista, recursividad | `src/productos.py` | [01-productos-inventario.md](01-productos-inventario.md) |
| 2 | Bodegas y sucursales | Diccionario anidado, cola FIFO | `src/ubicaciones.py` | [02-bodegas-sucursales.md](02-bodegas-sucursales.md) |
| 3 | Clientes y ventas | Diccionario, lista, pila LIFO | `src/ventas.py` | [03-clientes-ventas.md](03-clientes-ventas.md) |
| 4 | Pedidos | Cola FIFO, diccionario, pila de estados | `src/pedidos.py` | [04-pedidos.md](04-pedidos.md) |
| 5 | Logística y distribución | Grafo, Dijkstra, recursividad DFS | `src/logistica.py` | [05-logistica-distribucion.md](05-logistica-distribucion.md) |
| 6 | Seguimiento de operaciones | Lista de eventos, índice por tipo, árbol | `src/seguimiento.py` | [06-seguimiento-operaciones.md](06-seguimiento-operaciones.md) |

`src/sistema.py` coordina los seis módulos; `src/cli.py` es la interfaz y `src/datos.py` carga el dataset de demostración.

## Principios comunes

- Toda estructura debe responder una necesidad real del negocio; no se incluye una sola "por cumplir el requisito".
- Las claves de consulta son identificadores estables (`sku`, `cliente_id`, `pedido_id`, `ubicacion`).
- Las entradas inválidas y las operaciones sobre estructuras vacías se validan antes de mutar el estado.
- Los eventos de seguimiento se registran con `append`, nunca se reescriben.
