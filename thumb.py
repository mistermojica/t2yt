from PIL import Image, ImageDraw, ImageFont
import textwrap
import moviepy.editor as mpe

def crear_thumbnail(titulo, ruta_fondo, ruta_persona):
    # Cargar la imagen de fondo y la imagen de la persona
    fondo = Image.open(ruta_fondo)
    persona = Image.open(ruta_persona)

    # Redimensionar las imágenes si es necesario
    fondo = fondo.resize((720, 1280))  # Tamaño para YouTube Shorts
    persona = persona.resize((700, 700))

    # Crear una imagen base
    imagen_final = Image.new('RGB', fondo.size, (255, 255, 255))
    imagen_final.paste(fondo, (0,0))

    # Superponer la imagen de la persona
    posicion_persona = (30, 600)  # Cambiar según sea necesario
    imagen_final.paste(persona, posicion_persona, persona)

    # Agregar texto
    draw = ImageDraw.Draw(imagen_final)
    # font = ImageFont.truetype('./fonts/lemon_milk/LEMONMILK-Medium.otf', 90)  # Puedes cambiar la fuente y el tamaño
    font = ImageFont.truetype('./fonts/bebas_neue/BebasNeue-Regular.ttf', 110)  # Puedes cambiar la fuente y el tamaño
    draw.text((100, 175), textwrap.fill(titulo, width=15), (255, 255, 255), font=font, align='center')

    # Guardar la imagen
    filename = './thumbnails/thumbnail_youtube_shorts.jpg'
    imagen_final.save(filename)

    return filename


# Uso de la función
thumbnail_image = crear_thumbnail("mensaje\nmotivacional\npara\ntrabajar", './backgrounds/background3.jpg', './fotos/omar1.png')

# print(thumbnail_image.convert("RGB").tobytes())

thumbnail_clip = mpe.ImageClip(thumbnail_image).set_duration(5)  # Duración de 5 segundos, ajusta según necesites

print(thumbnail_clip)