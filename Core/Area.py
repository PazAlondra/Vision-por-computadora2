import cv2
import numpy as np


class Area():
    def __init__(self, xInicial, yInicial, ancho, alto):
        self.xInicial = xInicial
        self.yInicial = yInicial
        self.ancho = ancho
        self.alto = alto
        self.mascara = None

    def obtener_seccion(self, imagen):
        if imagen is None:
            raise ValueError("La imagen no puede ser None")

        y_final = self.yInicial + self.alto
        x_final = self.xInicial + self.ancho
        return imagen[self.yInicial:y_final, self.xInicial:x_final]

    def _guardar_mascara(self, nueva_mascara):
        nueva_mascara = nueva_mascara.astype(bool)

        if self.mascara is None:
            self.mascara = nueva_mascara
        else:
            if self.mascara.shape != nueva_mascara.shape:
                raise ValueError("La nueva mascara no coincide con el tamano del area")
            self.mascara = np.logical_and(self.mascara, nueva_mascara)

        return self.mascara

    def refinarPorColor(self, imagen, color, tolerancia=0):
        seccion = self.obtener_seccion(imagen)

        # OpenCV lee imagenes en formato BGR.
        color_bgr = np.array([color.azul, color.verde, color.rojo])
        pixeles_bgr = seccion[:, :, :3]

        if tolerancia == 0:
            coincide_color = np.all(pixeles_bgr == color_bgr, axis=2)
        else:
            diferencia = np.abs(pixeles_bgr.astype(int) - color_bgr.astype(int))
            coincide_color = np.all(diferencia <= tolerancia, axis=2)

        if seccion.shape[2] == 4:
            coincide_alpha = seccion[:, :, 3] == color.alpha
            coincide_color = np.logical_and(coincide_color, coincide_alpha)

        return self._guardar_mascara(np.logical_not(coincide_color))

    def refinarPorBorde(self, imagen=None, bandera=0, umbral=127, invertir=False):
        if imagen is not None:
            return self.refinarPorContorno(imagen, bandera, umbral, invertir)

        borde = np.zeros((self.alto, self.ancho), dtype=bool)

        if self.alto > 0:
            borde[0, :] = True
            borde[-1, :] = True

        if self.ancho > 0:
            borde[:, 0] = True
            borde[:, -1] = True

        if bandera == 0:
            mascara = np.logical_not(borde)
        elif bandera == 1:
            mascara = borde
        else:
            raise ValueError("La bandera debe ser 0 para interior o 1 para borde")

        return self._guardar_mascara(mascara)

    def refinarPorContorno(self, imagen, bandera=0, umbral=127, invertir=False):
        seccion = self.obtener_seccion(imagen)
        escala_grises = cv2.cvtColor(seccion, cv2.COLOR_BGR2GRAY)

        tipo_umbral = cv2.THRESH_BINARY_INV if invertir else cv2.THRESH_BINARY
        _, mascara_bn = cv2.threshold(escala_grises, umbral, 255, tipo_umbral)

        contornos, _ = cv2.findContours(mascara_bn, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        mascara_figura = np.zeros((seccion.shape[0], seccion.shape[1]), dtype=np.uint8)
        if contornos:
            contorno_principal = max(contornos, key=cv2.contourArea)
            cv2.drawContours(mascara_figura, [contorno_principal], -1, 255, thickness=cv2.FILLED)

        if bandera == 0:
            mascara = mascara_figura == 255
        elif bandera == 1:
            borde = cv2.Canny(mascara_figura, 100, 200)
            mascara = borde > 0
        else:
            raise ValueError("La bandera debe ser 0 para figura completa o 1 para borde")

        return self._guardar_mascara(mascara)

    def refinarPorMascara(self, imagen, umbral=127, invertir=False):
        seccion = self.obtener_seccion(imagen)
        escala_grises = cv2.cvtColor(seccion, cv2.COLOR_BGR2GRAY)
        _, mascara_bn = cv2.threshold(escala_grises, umbral, 1, cv2.THRESH_BINARY)

        if invertir:
            mascara = mascara_bn == 1
        else:
            mascara = mascara_bn == 0

        return self._guardar_mascara(mascara)
