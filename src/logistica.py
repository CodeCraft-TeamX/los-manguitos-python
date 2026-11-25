"""Funcionalidad 5: red logística y entregas.

Grafo como diccionario de adyacencia; Dijkstra para la ruta más corta y DFS
recursivo para enumerar alternativas (con control de ciclos y profundidad).
"""

from __future__ import annotations

import heapq

from src.errores import ErrorDeNegocio, NoEncontrado, ValidacionError
from src.modelos import Entrega, ahora
from src.utils import texto_requerido


class RedLogistica:
    """Representa central, bodegas y sucursales como un grafo."""

    def __init__(self) -> None:
        self._grafo: dict[str, dict[str, float]] = {}
        self._entregas: dict[str, Entrega] = {}

    def agregar_nodo(self, nodo: str) -> None:
        """Agrega un nodo aislado a la red."""
        nodo = texto_requerido(nodo, "Nodo")
        self._grafo.setdefault(nodo, {})

    def _validar_nodo(self, nodo: str) -> None:
        if nodo not in self._grafo:
            raise NoEncontrado(f"Nodo '{nodo}' no existe en la red")

    def agregar_conexion(
        self, origen: str, destino: str, distancia: float, bidireccional: bool = True
    ) -> None:
        """Conecta dos nodos con una distancia positiva."""
        self._validar_nodo(origen)
        self._validar_nodo(destino)
        if (
            isinstance(distancia, bool)
            or not isinstance(distancia, (int, float))
            or distancia <= 0
        ):
            raise ValidacionError("La distancia debe ser un número mayor que cero")
        self._grafo[origen][destino] = float(distancia)
        if bidireccional:
            self._grafo[destino][origen] = float(distancia)

    def vecinos(self, nodo: str) -> dict[str, float]:
        """Copia de los destinos alcanzables directamente desde ``nodo``."""
        self._validar_nodo(nodo)
        return dict(self._grafo[nodo])

    def nodos(self) -> list[str]:
        """Nombres de todos los nodos de la red."""
        return list(self._grafo)

    def ruta_mas_corta(self, origen: str, destino: str) -> list[str]:
        """Devuelve la ruta de menor distancia total mediante Dijkstra."""
        self._validar_nodo(origen)
        self._validar_nodo(destino)
        distancias = {nodo: float("inf") for nodo in self._grafo}
        anteriores: dict[str, str] = {}
        distancias[origen] = 0.0
        cola: list[tuple[float, str]] = [(0.0, origen)]

        while cola:
            distancia, nodo = heapq.heappop(cola)
            if distancia > distancias[nodo]:
                continue
            if nodo == destino:
                break
            for vecino, peso in self._grafo[nodo].items():
                candidata = distancia + peso
                if candidata < distancias[vecino]:
                    distancias[vecino] = candidata
                    anteriores[vecino] = nodo
                    heapq.heappush(cola, (candidata, vecino))

        if distancias[destino] == float("inf"):
            raise ErrorDeNegocio(f"No hay ruta disponible de '{origen}' a '{destino}'")
        ruta = [destino]
        while ruta[-1] != origen:
            ruta.append(anteriores[ruta[-1]])
        ruta.reverse()
        return ruta

    def rutas_posibles(
        self, origen: str, destino: str, max_profundidad: int = 6, limite: int = 10
    ) -> list[list[str]]:
        """Enumera rutas simples con DFS recursivo, sin repetir nodos."""
        self._validar_nodo(origen)
        self._validar_nodo(destino)
        if max_profundidad < 1 or limite < 1:
            raise ValidacionError("Profundidad y límite deben ser mayores que cero")
        rutas: list[list[str]] = []

        def explorar(actual: str, camino: list[str], visitados: set[str]) -> None:
            if len(rutas) >= limite or len(camino) > max_profundidad:
                return
            for vecino in self._grafo[actual]:
                if vecino in visitados:
                    continue
                nuevo_camino = [*camino, vecino]
                if vecino == destino:
                    rutas.append(nuevo_camino)
                    if len(rutas) >= limite:
                        return
                else:
                    explorar(vecino, nuevo_camino, visitados | {vecino})

        explorar(origen, [origen], {origen})
        return rutas

    def registrar_entrega(self, id_entrega: str, pedido_id: str, ruta: list[str]) -> Entrega:
        """Guarda el despacho de un pedido por una ruta ya calculada."""
        id_entrega = texto_requerido(id_entrega, "ID de entrega")
        if id_entrega in self._entregas:
            raise ValidacionError(f"Entrega '{id_entrega}' ya registrada")
        entrega = Entrega(id_entrega, pedido_id, tuple(ruta), ahora())
        self._entregas[id_entrega] = entrega
        return entrega

    def consultar_entrega(self, id_entrega: str) -> Entrega:
        """Devuelve una entrega registrada."""
        try:
            return self._entregas[id_entrega]
        except KeyError as exc:
            raise NoEncontrado(f"Entrega '{id_entrega}' no encontrada") from exc

    def listar_entregas(self) -> list[Entrega]:
        """Copia de las entregas registradas."""
        return list(self._entregas.values())
