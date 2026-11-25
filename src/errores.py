"""Errores de dominio del sistema.

El CLI los captura para mostrar mensajes comprensibles al operador.
"""


class ErrorDeNegocio(Exception):
    """Clase base para cualquier regla de negocio incumplida."""


class ValidacionError(ErrorDeNegocio):
    """Dato de entrada inválido o ausente."""


class NoEncontrado(ErrorDeNegocio):
    """La entidad consultada no existe."""


class StockInsuficiente(ErrorDeNegocio):
    """No hay unidades disponibles para la operación."""


class TransicionInvalida(ErrorDeNegocio):
    """El cambio de estado solicitado no está permitido."""
