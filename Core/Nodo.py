import os
import math

import cv2
import numpy as np

from Core.Posicion2D import Posicion2D


class Nodo():
    def __init__(self, nombre, ruta_imagen=None, posicion_local=None, padre=None, z_index=0, area=None):
        self.nombre = nombre
        self.ruta_imagen = ruta_imagen
        self.posicion_local = posicion_local or Posicion2D(0, 0)
        self.padre = None
        self.hijos = []
        self.z_index = z_index
        self.area = area
        self.sprite = None
        self.movimiento_inicial = None
        self.movimiento_final = None
        self.amplitud_ondulacion_y = 0
        self.ciclos_ondulacion = 0

        if padre is not None:
            padre.agregar_hijo(self)

    def agregar_hijo(self, hijo):
        hijo.padre = self
        self.hijos.append(hijo)

    def configurar_movimiento(self, posicion_inicial, posicion_final):
        self.movimiento_inicial = posicion_inicial
        self.movimiento_final = posicion_final
        self.posicion_local = Posicion2D(posicion_inicial.posX, posicion_inicial.posY)

    def configurar_ondulacion(self, amplitud_y, ciclos):
        self.amplitud_ondulacion_y = amplitud_y
        self.ciclos_ondulacion = ciclos

    def actualizar(self, frame_actual, total_frames):
        if self.movimiento_inicial is not None and self.movimiento_final is not None:
            if total_frames <= 1:
                nueva_x = round(self.movimiento_inicial.posX)
                nueva_y = round(self.movimiento_inicial.posY)
            else:
                proporcion = frame_actual / (total_frames - 1)
                nueva_x = round(
                    self.movimiento_inicial.posX
                    + (self.movimiento_final.posX - self.movimiento_inicial.posX) * proporcion
                )
                nueva_y_base = (
                    self.movimiento_inicial.posY
                    + (self.movimiento_final.posY - self.movimiento_inicial.posY) * proporcion
                )
                ondulacion_y = 0
                if self.amplitud_ondulacion_y > 0 and self.ciclos_ondulacion > 0:
                    angulo = 2 * math.pi * self.ciclos_ondulacion * proporcion
                    ondulacion_y = self.amplitud_ondulacion_y * math.sin(angulo)

                nueva_y = round(nueva_y_base + ondulacion_y)

            self.posicion_local = Posicion2D(nueva_x, nueva_y)

        for hijo in self.hijos:
            hijo.actualizar(frame_actual, total_frames)

    def obtener_posicion_global(self):
        if self.padre is None:
            return Posicion2D(self.posicion_local.posX, self.posicion_local.posY)

        posicion_padre = self.padre.obtener_posicion_global()
        return Posicion2D(
            posicion_padre.posX + self.posicion_local.posX,
            posicion_padre.posY + self.posicion_local.posY
        )

    def _cargar_imagen(self):
        if self.ruta_imagen is None:
            return None

        imagen = cv2.imread(self.ruta_imagen, cv2.IMREAD_UNCHANGED)
        if imagen is None:
            raise FileNotFoundError(f"No se pudo leer la imagen: {self.ruta_imagen}")
        return imagen

    def _imagen_a_bgra(self, imagen):
        if imagen.ndim == 2:
            return cv2.cvtColor(imagen, cv2.COLOR_GRAY2BGRA)

        if imagen.shape[2] == 4:
            return imagen.copy()

        bgra = cv2.cvtColor(imagen, cv2.COLOR_BGR2BGRA)
        bgra[:, :, 3] = 255
        return bgra

    def _crear_sprite_desde_area(self, imagen):
        seccion = self.area.obtener_seccion(imagen)
        mascara = self.area.mascara

        if mascara is None:
            return self._imagen_a_bgra(seccion)

        if not np.any(mascara):
            raise ValueError(f"La mascara del nodo '{self.nombre}' no contiene pixeles seleccionados")

        filas, columnas = np.where(mascara)
        y_min = filas.min()
        y_max = filas.max() + 1
        x_min = columnas.min()
        x_max = columnas.max() + 1

        seccion_recortada = seccion[y_min:y_max, x_min:x_max]
        mascara_recortada = mascara[y_min:y_max, x_min:x_max]

        sprite = self._imagen_a_bgra(seccion_recortada)
        sprite[:, :, 3] = np.where(mascara_recortada, 255, 0).astype(np.uint8)
        return sprite

    def cargar_sprite(self):
        if self.sprite is not None:
            return self.sprite

        imagen = self._cargar_imagen()
        if imagen is None:
            return None

        if self.area is None:
            self.sprite = self._imagen_a_bgra(imagen)
        else:
            self.sprite = self._crear_sprite_desde_area(imagen)

        return self.sprite

    def dibujar(self, lienzo):
        sprite = self.cargar_sprite()
        if sprite is None:
            return

        posicion = self.obtener_posicion_global()
        x = int(posicion.posX)
        y = int(posicion.posY)

        alto_sprite, ancho_sprite = sprite.shape[:2]
        alto_lienzo, ancho_lienzo = lienzo.shape[:2]

        x_inicio = max(0, x)
        y_inicio = max(0, y)
        x_fin = min(ancho_lienzo, x + ancho_sprite)
        y_fin = min(alto_lienzo, y + alto_sprite)

        if x_inicio >= x_fin or y_inicio >= y_fin:
            return

        sprite_x_inicio = x_inicio - x
        sprite_y_inicio = y_inicio - y
        sprite_x_fin = sprite_x_inicio + (x_fin - x_inicio)
        sprite_y_fin = sprite_y_inicio + (y_fin - y_inicio)

        region_lienzo = lienzo[y_inicio:y_fin, x_inicio:x_fin]
        region_sprite = sprite[sprite_y_inicio:sprite_y_fin, sprite_x_inicio:sprite_x_fin]

        if region_sprite.shape[2] == 4:
            alpha = region_sprite[:, :, 3].astype(np.float32) / 255.0
            alpha = alpha[:, :, np.newaxis]
            region_lienzo[:] = (
                region_sprite[:, :, :3].astype(np.float32) * alpha
                + region_lienzo.astype(np.float32) * (1.0 - alpha)
            ).astype(np.uint8)
        else:
            region_lienzo[:] = region_sprite[:, :, :3]
