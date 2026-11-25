# 5. Logística y distribución

**Necesidad:** representar conexiones entre central, bodegas y sucursales; consultar rutas posibles y administrar entregas.

**Estado:** diseñado, pendiente de implementación.

## Estructuras elegidas

| Dato | Estructura | Uso |
| --- | --- | --- |
| Red de nodos | **Grafo** como diccionario de adyacencia: `dict[str, dict[str, float]]` | `grafo[origen][destino] = distancia`. |
| Ruta más corta | **Dijkstra** (o BFS si solo importan los saltos) | Entrega con menor distancia total. |
| Enumeración de rutas | **DFS recursivo** con conjunto `visitados` | Listar alternativas entre dos nodos. |
| Entregas en curso | `dict[str, Entrega]` por `entrega_id` | Seguimiento del despacho asociado a un pedido. |

## Por qué estas estructuras

- La red es un grafo por naturaleza: una bodega puede conectarse con varias sucursales y una sucursal puede tener más de una ruta de acceso. El diccionario de adyacencia hace `O(1)` la consulta "¿están conectados A y B?".
- Dijkstra responde la pregunta de negocio "ruta más corta para entregar", con pesos reales (kilómetros o tiempo).
- La **recursividad** es la forma natural de explorar caminos: desde el nodo actual se llama al mismo procedimiento para cada vecino, llevando `visitados` para evitar ciclos.

## Por qué no otras

- Una **matriz de adyacencia** desperdicia memoria: la red es dispersa (pocas conexiones por nodo) y crecería `O(V²)`.
- Una **lista simple de rutas** no permite descubrir conexiones indirectas (`CENTRAL → BODEGA-NORTE → SUC-02`) sin recorrer y reconstruir manualmente la red.
- Un **árbol** no sirve: las sucursales pueden tener más de un padre (rutas alternativas), lo que rompe la estructura jerárquica.

## Operaciones previstas y complejidad

| Operación | Complejidad |
| --- | --- |
| `agregar_conexion(origen, destino, distancia)` | `O(1)` |
| `vecinos(nodo)` | `O(1)` acceso, `O(grado)` iteración |
| `ruta_mas_corta(origen, destino)` | `O((V + E) log V)` con Dijkstra |
| `rutas_posibles(origen, destino)` | DFS recursivo, exponencial en el peor caso (se limita profundidad) |
| `registrar_entrega(pedido_id, ruta)` | `O(1)` |

## Validaciones

- Nodos origen/destino inexistentes; distancia `<= 0`.
- Grafo desconectado: informar "sin ruta disponible" en lugar de devolver `None` silencioso.
- Ciclos: controlados por `visitados` en el DFS; evitan recursión infinita.
- Límite de profundidad en la enumeración de rutas para no explorar indefinidamente.

## Datos de prueba sugeridos

Nodos: `CENTRAL`, `BODEGA-NORTE`, `BODEGA-SUR`, `SUC-01`, `SUC-02`. Conexiones: `CENTRAL-BODEGA-NORTE (12)`, `CENTRAL-BODEGA-SUR (8)`, `BODEGA-NORTE-SUC-01 (7)`, `BODEGA-SUR-SUC-02 (9)`, `BODEGA-NORTE-SUC-02 (15)`. Ruta esperada a `SUC-02`: `CENTRAL → BODEGA-SUR → SUC-02` (17).
