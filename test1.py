import os

import cv2

from Core.Area import Area
from Core.Color import Color
from Core.Escena import Escena
from Core.Nodo import Nodo
from Core.Posicion2D import Posicion2D


def crear_area_con_mascara(ruta_imagen, tolerancia=40):
    imagen = cv2.imread(ruta_imagen)
    if imagen is None:
        raise FileNotFoundError(f"No se pudo leer la imagen: {ruta_imagen}")

    alto, ancho = imagen.shape[:2]
    area = Area(0, 0, ancho, alto)

    color_fondo_bgr = imagen[0, 0]
    color_fondo = Color(
        int(color_fondo_bgr[2]),
        int(color_fondo_bgr[1]),
        int(color_fondo_bgr[0]),
        255
    )
    area.refinarPorColor(imagen, color_fondo, tolerancia=tolerancia)
    return area


ruta_fondo = "img/mar.png"
ruta_tortuga = "img/tortuga.png"
ruta_tiburon = "img/tiburon.png"

if not os.path.exists(ruta_tiburon):
    print("No se encontro img/tiburon.png. Se usara temporalmente img/tortuga.png como respaldo.")
    ruta_tiburon = ruta_tortuga

raiz = Nodo("escena")

fondo = Nodo(
    "fondo",
    ruta_imagen=ruta_fondo,
    posicion_local=Posicion2D(0, 0),
    padre=raiz,
    z_index=0
)

area_tortuga = crear_area_con_mascara(ruta_tortuga, tolerancia=45)
tortuga = Nodo(
    "tortuga",
    ruta_imagen=ruta_tortuga,
    posicion_local=Posicion2D(-120, 650),
    padre=raiz,
    z_index=1,
    area=area_tortuga
)
tortuga.configurar_movimiento(Posicion2D(-120, 650), Posicion2D(920, 560))
tortuga.configurar_ondulacion(amplitud_y=18, ciclos=4)

area_tiburon = crear_area_con_mascara(ruta_tiburon, tolerancia=45)
tiburon = Nodo(
    "tiburon",
    ruta_imagen=ruta_tiburon,
    posicion_local=Posicion2D(-220, 260),
    padre=raiz,
    z_index=2,
    area=area_tiburon
)
tiburon.configurar_movimiento(Posicion2D(-220, 260), Posicion2D(1080, 220))
tiburon.configurar_ondulacion(amplitud_y=12, ciclos=3)

escena = Escena(
    raiz=raiz,
    numero_frames=360,
    fps=12,
    directorio_salida="img",
    prefijo_salida="escena_frame_"
)
escena.generar_frames()
