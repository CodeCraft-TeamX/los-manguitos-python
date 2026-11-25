# 2. Administración de bodegas y sucursales

**Necesidad:** controlar existencias por ubicación y gestionar transferencias entre bodegas y sucursales.

**Estado:** diseñado, pendiente de implementación.

## Estructuras elegidas

| Dato | Estructura | Uso |
| --- | --- | --- |
| Stock por ubicación | `dict[str, dict[str, int]]` (`ubicacion -> sku -> cantidad`) | Consulta y actualización directa del par (ubicación, producto). |
| Datos de la ubicación | `dict[str, Ubicacion]` (tipo, dirección, responsable) | Metadata separada del stock. |
| Transferencias solicitadas | `deque[Transferencia]` (cola FIFO) | Atención en orden de llegada. |

## Por qué estas estructuras

- El diccionario anidado responde a la pregunta real del operador: "¿cuántas unidades de `MANG-01` hay en la bodega central?". Acceso `O(1)` promedio con la clave compuesta `(ubicacion, sku)`, sin recorrer todas las bodegas.
- La cola FIFO refleja la regla operativa: la transferencia solicitada primero se procesa primero. `append` y `popleft` son `O(1)` con `collections.deque`.

## Por qué no otras

- Una **lista de registros** `(ubicacion, sku, cantidad)` exigiría recorrer toda la lista para cada consulta y para cada ajuste de stock (`O(n)`), además de validar duplicados del par.
- Una **pila LIFO** priorizaría la última transferencia solicitada, dejando "atascadas" las más antiguas: no es equitativo con las sucursales.
- Un **grafo** pertenece al módulo logístico (rutas); usarlo también para el stock mezclaría dos responsabilidades distintas.

## Operaciones previstas y complejidad

| Operación | Complejidad |
| --- | --- |
| `registrar_ubicacion(id, tipo)` | `O(1)` |
| `consultar_stock(ubicacion, sku)` | `O(1)` |
| `ajustar_stock(ubicacion, sku, delta)` | `O(1)` |
| `solicitar_transferencia(origen, destino, sku, cantidad)` | `O(1)` (encola) |
| `procesar_siguiente_transferencia()` | `O(1)` (`popleft`) + dos ajustes de stock |

## Validaciones

- Ubicación o SKU inexistente; transferencia entre la misma ubicación.
- Stock insuficiente en el origen: la transferencia se rechaza y no se encola.
- Cola vacía al procesar: mensaje explícito, sin `IndexError`.
- Cantidad `<= 0` y duplicados involuntarios de solicitud.

## Datos de prueba sugeridos

Ubicaciones: `CENTRAL` (bodega), `BODEGA-NORTE`, `SUC-01`, `SUC-02`. Stock inicial de `MANG-01`: 40 en `CENTRAL`, 8 en `SUC-01`. Transferencia de ejemplo: 10 unidades `CENTRAL -> SUC-02`.
