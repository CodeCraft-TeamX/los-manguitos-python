# Los Manguitos — Prototipo Python (CLI)

Prototipo de consola para el sistema integral de gestión de inventario, ventas y distribución de **Los Manguitos**. La versión web (HTML) del prototipo se desarrolla en un repositorio aparte.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `main.py` | Punto de entrada de la aplicación. |
| `src/cli.py` | Menú de terminal (6 módulos + recarga de datos de ejemplo). |
| `src/sistema.py` | Fachada que coordina los módulos y emite eventos. |
| `src/productos.py`, `src/ubicaciones.py`, `src/ventas.py`, `src/pedidos.py`, `src/logistica.py`, `src/seguimiento.py` | Gestores de las seis funcionalidades. |
| `src/modelos.py`, `src/errores.py`, `src/utils.py` | Entidades, errores de negocio y validaciones compartidas. |
| `src/datos.py` | Dataset de demostración (se carga al iniciar). |
| `docs/` | Justificación de las estructuras de datos por funcionalidad. |
| `tests/` | 34 pruebas con `unittest` (sin dependencias externas). |

El menú permite consultar/registrar productos, transferencias, ventas y pedidos, calcular rutas, revisar el registro de operaciones y recargar los datos de ejemplo. Para ver un despacho completo: **4 → 4** (atender `PED-001`), **4 → 5** (estado `LISTO`), **4 → 7** (despachar con ID de entrega).

## Cómo ejecutarlo

### Con uv (recomendado)

```bash
uv run python main.py
```

`uv` crea `.venv` automáticamente y respeta la versión de `.python-version` (Python 3.13).

### Con Python normal

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python main.py
```

Si ya tienes Python 3.13 disponible, también puedes ejecutar `python main.py` directamente: el proyecto no tiene dependencias externas.

## Pruebas

```bash
uv run python -m unittest discover -s tests
# o, con el entorno activado:
python -m unittest discover -s tests
```
