import os

import cv2
import numpy as np


class Escena():
    def __init__(self, raiz, numero_frames=120, fps=24, directorio_salida="img", prefijo_salida="escena_frame_"):
        self.raiz = raiz
        self.numero_frames = numero_frames
        self.fps = fps
        self.directorio_salida = directorio_salida
        self.prefijo_salida = prefijo_salida

    def _recorrer_nodos(self, nodo):
        nodos = [nodo]
        for hijo in nodo.hijos:
            nodos.extend(self._recorrer_nodos(hijo))
        return nodos

    def obtener_nodos_dibujables(self):
        nodos = self._recorrer_nodos(self.raiz)
        nodos = [nodo for nodo in nodos if nodo.ruta_imagen is not None]
        nodos.sort(key=lambda nodo: nodo.z_index)
        return nodos

    def crear_lienzo_base(self):
        nodos = self.obtener_nodos_dibujables()
        if not nodos:
            raise ValueError("La escena no contiene nodos con imagen para dibujar")

        sprite_base = nodos[0].cargar_sprite()
        if sprite_base is None:
            raise ValueError("No se pudo cargar la imagen base de la escena")

        alto, ancho = sprite_base.shape[:2]
        return np.zeros((alto, ancho, 3), dtype=np.uint8)

    def generar_frames(self):
        os.makedirs(self.directorio_salida, exist_ok=True)
        nodos = self.obtener_nodos_dibujables()

        for frame in range(self.numero_frames):
            self.raiz.actualizar(frame, self.numero_frames)
            lienzo = self.crear_lienzo_base()

            for nodo in nodos:
                nodo.dibujar(lienzo)

            ruta_salida = os.path.join(
                self.directorio_salida,
                f"{self.prefijo_salida}{frame + 1:03d}.png"
            )
            cv2.imwrite(ruta_salida, lienzo)
