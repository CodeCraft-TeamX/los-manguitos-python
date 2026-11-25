# 1. Gestión de productos e inventario

**Necesidad:** registrar productos, categorías y proveedores; controlar existencias y registrar entradas y salidas.

**Estado:** implementado en `src/productos.py`.

**Nota de implementación:** el stock efectivo es propiedad de `GestorUbicaciones` (fuente única de verdad); `Producto` no duplica el número. `Sistema.consultar_stock_total(sku)` lo obtiene sumando las ubicaciones, y la lista de movimientos queda como historial de auditoría.

## Estructuras elegidas

| Dato | Estructura | Uso |
| --- | --- | --- |
| Catálogo de productos | `dict[str, Producto]` (clave = `sku`) | Alta, consulta y actualización por identificador. |
| Movimientos de un producto | `dict[str, list[Movimiento]]` (clave = `sku`) | Historial cronológico de entradas y salidas. |
| Categorías | `dict[str, list[str]]` + recursividad | Categorías con subcategorías y listado de su catálogo. |

## Por qué estas estructuras

- **Diccionario por SKU:** la operación más frecuente es "dame el producto X" o "actualiza su stock"; con clave directa es `O(1)` promedio. El SKU es único e inmutable, por lo que es una clave natural.
- **Lista de movimientos:** cada entrada/salida se agrega al final (`append`, `O(1)` amortizado) y el negocio necesita el historial en orden de ocurrencia. No se eliminan movimientos: son la base del módulo de seguimiento.
- **Recursividad para categorías:** el árbol de categorías tiene profundidad desconocida (por ejemplo, *Indumentaria → Mangas → Térmicas*). Recorrerlo recursivamente evita fijar de antemano cuántos niveles existen.

## Por qué no otras

- Una **lista de productos** obligaría a buscar linealmente `O(n)` por SKU y a controlar duplicados a mano; crece mal con el catálogo.
- Una **pila** o una **cola** no aplican al stock: los productos no se consumen "por el último" ni "por el primero", sino por identificador; el orden solo importa en el historial.
- Un **grafo** sería excesivo aquí: las categorías forman un árbol (sin ciclos ni rutas alternativas), que se resuelve con recursividad.

## Operaciones previstas y complejidad

| Operación | Complejidad |
| --- | --- |
| `registrar_producto(sku, ...)` | `O(1)` + validación de duplicado |
| `consultar_producto(sku)` | `O(1)` |
| `registrar_movimiento(sku, tipo, cantidad)` | `O(1)` + actualización de stock |
| `listar_movimientos(sku)` | `O(k)`, donde `k` = movimientos de ese SKU |
| `listar_categoria(categoria)` | `O(n)` recursivo sobre los descendientes |

## Validaciones

- SKU vacío o duplicado; cantidad de movimiento `<= 0`.
- Stock insuficiente para una salida (nunca debe quedar negativo).
- Producto, categoría o proveedor inexistente al registrar movimientos.
- Catálogo o historial vacío: devolver mensaje claro, nunca fallar por índice.

## Datos de prueba sugeridos

`MANG-01` (Manga térmica, categoría *Indumentaria/Mangas*, proveedor `PROV-01`, stock 40), `MANG-02` (stock 12), `GUAN-01` (categoría *Indumentaria/Manos*). Movimientos de ejemplo: entrada 40, salida 5, entrada 20.
