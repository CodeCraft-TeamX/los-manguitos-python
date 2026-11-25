"""Validaciones y ayudas de entrada reutilizables por los módulos y el CLI."""

from __future__ import annotations

from src.errores import ValidacionError


def texto_requerido(valor: str, nombre: str) -> str:
    """Valida que un texto no esté vacío y lo devuelve sin espacios."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValidacionError(f"{nombre} no puede estar vacío")
    return valor.strip()


def entero_requerido(valor: int, nombre: str, minimo: int = 1) -> int:
    """Valida que un número entero sea válido y mayor o igual que ``minimo``."""
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < minimo:
        raise ValidacionError(f"{nombre} debe ser un entero mayor o igual que {minimo}")
    return valor


def pedir_texto(mensaje: str) -> str:
    """Lee una línea de texto desde la terminal."""
    return input(mensaje).strip()


def pedir_entero(mensaje: str, minimo: int = 1) -> int:
    """Pide un entero válido, repitiendo la pregunta si la entrada es inválida."""
    while True:
        valor = pedir_texto(mensaje)
        try:
            return entero_requerido(int(valor), "Valor", minimo)
        except ValueError:
            print("  Ingrese un número entero válido.")


def pausar() -> None:
    """Espera a que el operador presione Enter antes de seguir."""
    input("\nPresione Enter para continuar...")
