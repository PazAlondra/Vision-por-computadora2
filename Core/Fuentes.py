import cv2
import os
from datetime import datetime


class Fuentes():
    def __init__(self, ruta_imagen, area, posicion_inicial, posicion_final, numero_imagenes=720):
        self.ruta_imagen = ruta_imagen
        self.area = area
        self.posicion_inicial = posicion_inicial
        self.posicion_final = posicion_final
        self.numero_imagenes = numero_imagenes
        self.imagen = self.leer_imagen()
        self.directorio_salida = os.path.dirname(ruta_imagen) or "."
        self.ruta_tabla_posiciones = os.path.join(self.directorio_salida, "tabla_posiciones.txt")

    def leer_imagen(self):
        imagen = cv2.imread(self.ruta_imagen)
        if imagen is None:
            print("La imagen no existe")
            return None
        return imagen

    def seleccionar_area(self):
        return self.imagen[
            self.area.yInicial:self.area.yInicial + self.area.alto,
            self.area.xInicial:self.area.xInicial + self.area.ancho
        ]

    def borrar_area_original(self, imagen_modificada, color_fondo):
        origen = imagen_modificada[
            self.area.yInicial:self.area.yInicial + self.area.alto,
            self.area.xInicial:self.area.xInicial + self.area.ancho
        ]

        alto_efectivo = min(origen.shape[0], self.area.alto)
        ancho_efectivo = min(origen.shape[1], self.area.ancho)

        if self.area.mascara is None:
            origen[:alto_efectivo, :ancho_efectivo] = color_fondo
            return

        mascara = self.area.mascara[:alto_efectivo, :ancho_efectivo]
        origen[:alto_efectivo, :ancho_efectivo][mascara] = color_fondo

    def generar_tabla_posiciones(self, fps=24):
        if self.numero_imagenes <= 1:
            return [{
                "frame": 0,
                "tiempo": 0.0,
                "x": round(self.posicion_inicial.posX),
                "y": round(self.posicion_inicial.posY),
            }]

        dx = (self.posicion_final.posX - self.posicion_inicial.posX) / (self.numero_imagenes - 1)
        dy = (self.posicion_final.posY - self.posicion_inicial.posY) / (self.numero_imagenes - 1)
        tabla = []

        for i in range(self.numero_imagenes):
            tabla.append({
                "frame": i,
                "tiempo": i / fps,
                "x": round(self.posicion_inicial.posX + dx * i),
                "y": round(self.posicion_inicial.posY + dy * i),
            })

        return tabla

    def guardar_tabla_posiciones(self, tabla_posiciones, fps=24):
        especificaciones = [
            "========================================",
            f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Imagen: {self.ruta_imagen}",
            (
                f"Area: xInicial={self.area.xInicial}, yInicial={self.area.yInicial}, "
                f"ancho={self.area.ancho}, alto={self.area.alto}"
            ),
            (
                f"Posicion inicial: ({self.posicion_inicial.posX}, "
                f"{self.posicion_inicial.posY})"
            ),
            (
                f"Posicion final: ({self.posicion_final.posX}, "
                f"{self.posicion_final.posY})"
            ),
            f"Numero de cuadros: {self.numero_imagenes}",
            f"FPS de referencia: {fps}",
            "Tabla de posiciones:",
            "frame\ttiempo(s)\tx\ty",
        ]

        with open(self.ruta_tabla_posiciones, "a", encoding="utf-8") as archivo:
            archivo.write("\n".join(especificaciones) + "\n")
            for posicion in tabla_posiciones:
                archivo.write(
                    f"{posicion['frame']}\t"
                    f"{posicion['tiempo']:.4f}\t"
                    f"{posicion['x']}\t"
                    f"{posicion['y']}\n"
                )
            archivo.write("\n")

    def generar_fuentes(self, color_fondo=None, fps=24):
        if self.imagen is None:
            return

        if color_fondo is None:
            color_fondo = self.imagen[0, 0].copy()

        tabla_posiciones = self.generar_tabla_posiciones(fps)
        self.guardar_tabla_posiciones(tabla_posiciones, fps)

        for i, posicion in enumerate(tabla_posiciones):
            imagen_modificada = self.imagen.copy()
            self.borrar_area_original(imagen_modificada, color_fondo)

            nueva_posicion_x = posicion["x"]
            nueva_posicion_y = posicion["y"]

            seccion_desplazada = self.seleccionar_area()

            alto_efectivo = min(seccion_desplazada.shape[0], imagen_modificada.shape[0] - nueva_posicion_y)
            ancho_efectivo = min(seccion_desplazada.shape[1], imagen_modificada.shape[1] - nueva_posicion_x)

            if alto_efectivo <= 0 or ancho_efectivo <= 0:
                print("La seccion desplazada esta fuera de los limites de la imagen.")
                continue

            seccion_para_insertar = seccion_desplazada[:alto_efectivo, :ancho_efectivo]
            destino = imagen_modificada[
                nueva_posicion_y:nueva_posicion_y + alto_efectivo,
                nueva_posicion_x:nueva_posicion_x + ancho_efectivo
            ]

            if self.area.mascara is None:
                destino[:, :] = seccion_para_insertar
            else:
                mascara = self.area.mascara[:alto_efectivo, :ancho_efectivo]
                destino[mascara] = seccion_para_insertar[mascara]

            ruta_salida = os.path.join(self.directorio_salida, f'imagen_desplazada_{i + 1:02d}.png')
            cv2.imwrite(ruta_salida, imagen_modificada)
