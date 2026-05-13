import cv2
import os


directorio_imagenes = "img"
fps = 12

configuraciones = [
    ("escena_frame_", "video/video_escena.mp4"),
    ("imagen_desplazada_", "video/video_desplazamiento.mp4"),
]

archivos_imagenes = []
nombre_video_salida = None

for prefijo, salida in configuraciones:
    candidatos = [
        img for img in os.listdir(directorio_imagenes)
        if img.startswith(prefijo) and img.endswith(".png")
    ]
    if candidatos:
        archivos_imagenes = sorted(candidatos)
        nombre_video_salida = salida
        break

if not archivos_imagenes:
    raise FileNotFoundError("No se encontraron imagenes generadas en la carpeta img")

imagen_ejemplo = cv2.imread(os.path.join(directorio_imagenes, archivos_imagenes[0]))
if imagen_ejemplo is None:
    raise FileNotFoundError("No se pudo leer la primera imagen generada")

altura, ancho, capas = imagen_ejemplo.shape
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
video_salida = cv2.VideoWriter(nombre_video_salida, fourcc, fps, (ancho, altura))

for archivo in archivos_imagenes:
    imagen = cv2.imread(os.path.join(directorio_imagenes, archivo))
    if imagen is not None:
        video_salida.write(imagen)

video_salida.release()

print("El video ha sido creado exitosamente.")
