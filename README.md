# Los Manguitos — Prototipo Python (CLI)

Prototipo de consola para el sistema integral de gestión de inventario, ventas y distribución de **Los Manguitos**. La versión web (HTML) del prototipo se desarrolla en un repositorio aparte.

## Estructura base

| Ruta | Contenido |
| --- | --- |
| `main.py` | Punto de entrada de la aplicación. |
| `src/cli.py` | Interfaz de línea de comandos (menú). |
| `src/utils.py` | Funciones auxiliares reutilizables. |
| `docs/` | Decisiones de estructuras de datos por funcionalidad. |
| `tests/` | Pruebas automatizadas con `unittest` (sin dependencias). |

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
