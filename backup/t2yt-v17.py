import os
import io
from openai import OpenAI
import requests
import argparse
import subprocess
import boto3
import random
import json
import numpy as np
import math
import time
import hashlib
import hmac
from base64 import b64decode
from PIL import Image, ImageDraw, ImageFont
import textwrap
from textwrap import wrap

from pydub import AudioSegment
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import moviepy.editor as mpe
import moviepy.video as mpv
import moviepy.audio as mpa
from moviepy.editor import VideoFileClip, concatenate_videoclips, concatenate_audioclips, AudioFileClip, TextClip, ImageClip, ColorClip
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime
from google.cloud import texttospeech
from google.cloud import translate_v2 as translate
from tqdm import tqdm

from pathlib import Path
from io import BytesIO
import moviepy.video.fx.resize as resize_fx

dt = datetime.now()
tiempo = int(datetime.timestamp(dt))

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
except Exception as err:
    print(err)


BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Configurar credenciales y claves API
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client_secret.json"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

ENVATO_API_KEY = os.environ.get("ENVATO_API_KEY", "")

ADOBE_STOCK_API_KEY = os.environ.get("ADOBE_STOCK_API_KEY", "")
ADOBE_STOCK_X_PRODUCT = os.environ.get("ADOBE_STOCK_X_PRODUCT", "")
ADOBE_ACCESS_CLIENT_ID = os.environ.get("ADOBE_ACCESS_CLIENT_ID", "")
ADOBE_ACCESS_CLIENT_SECRET = os.environ.get("ADOBE_ACCESS_CLIENT_SECRET", "")

STORYBLOCKS_PUBLIC_KEY = os.environ.get("STORYBLOCKS_PUBLIC_KEY", "")
STORYBLOCKS_PRIVATE_KEY = os.environ.get("STORYBLOCKS_PRIVATE_KEY", "")
                                            
CONTADOR_ESCENAS = 0

# Información de autenticación
api_key = os.environ.get('STORYBLOCKS_PUBLIC_KEY', '')
secret_key = os.environ.get('STORYBLOCKS_PRIVATE_KEY', '')
user_id = os.environ.get('STORYBLOCKS_USER_ID', '')
project_id = os.environ.get('STORYBLOCKS_PROJECT_ID', '')
expires = int(time.time()) + 3600  # 1 hora en el futuro

# print(ADOBE_ACCESS_CLIENT_SECRET)

client = OpenAI()

# openai.api_key = OPENAI_API_KEY
client.api_key = OPENAI_API_KEY


def log(param):
    print("==========================================")
    print(param)
    print("==========================================")

# creds = Credentials.from_authorized_user_info(info='client_secret.json')

# Aquí va la implementación de GPT-4 para generar el guión
def generate_script(outline, palabraclave, idioma, duracion):
    # Generate a JSON file and act as an educational tutorial creator for YouTube, creating a script with as many parts as necessary that transform common questions such as "How to...?" in detailed and captivating explanations about [{outline}], with clear and consistent descriptions in each part, and enriched with an educational and engaging narrative to immerse the audience in learning.
    
    # prompt = f"""
    #     Goal:

    #     Generate a JSON file and act as an educational video creator for YouTube Shorts, creating a script with as many parts as necessary that transform common questions such as "How to...?" in short and captivating explanations about this main topic ["{outline}"], with clear and consistent descriptions in each part, and enriched with an educational and engaging narrative to immerse the audience in learning. The script should also incorporate the following elements without mention them literaly in narration, that are used for viral success on YouTube Shorts:

    #     1. Striking Initial Hook: Start with something that immediately captures attention. Examples: "AI composes a song in 1 minute: Hit or flop?", "AI chatbot organizes my schedule: Better than an assistant?", "AI Challenge: Who edits photos better, human or machine?", "AI for saving: Does it really cut my monthly expenses?". (Do not mention this element literaly in the narration)
    #     2. Brief and Concise Content: Limit the duration to 34 seconds or less, ensuring the content is quick and easy to consume.
    #     3. Relevant and Current Content: Address trending topics, such as current events, viral challenges, popular memes, or topics of great interest. (Do not mention this element literaly in the narration)
    #     4. Surprise or Unexpected Element: Include a twist or unexpected event that generates excitement or surprise, such as an abrupt change in the narrative or an uncommon reaction. (Do not mention this element literaly in the narration)
    #     5. Clear Call to Action: Conclude with a direct message for viewer action, such as sharing, liking, commenting, or engaging in a specific activity, thus promoting participation and spreading the video. (Do not mention this element literaly in the narration)

    #     Identification of titles and subtitles:

    #     - Important Instruction: Each title or subtitle must be described in a detailed and coherent manner.

    #     - Name of the title: [Condensed description of the title, including steps, actions that the student must execute to learn about the topic.]
    #     - Name of the subtitle: [Condensed description of the subtitle, including steps, actions that the student must execute to learn about the topic.]
    #     - [Continue with other subtitles as necessary.]

    #     JSON structure:

    #     The JSON should contain an object in an array of one element, representing a the title of the tutorial, placed in a field called "script_video_ia".

    #     Each title object must include:

    #     - scene_dialog: A one only array of narrative entries, corresponding to a title. The array of narrative entries must include elements with this structure:
    #     -- scene_part: A tag or identifier for the specific part of the title being narrated.
    #     -- narration: In Spanish, the actual narrative text spoken by the narrator, which must describe the title, steps, and actions in detail, in a style consistent with the overall approach of the tutorial.
    #     -- prompt_dalle: in English, develop a message for DALL·E that describes the "narration" in detail and precision. It should be detailed enough so that GPT-4 can send it directly to DALL·E without any additional adjustments.
    #     -- video_keyword: in English, specify one keyword that represents the main topic ["{outline}"]. It is very important that the keywords are in english.

    #     Consistency in the descriptions and definitions of title and subtitle:

    #     - Ensure that the title and subtitle are identical in each object of the tutorial, to the text provided in the main topic.
    #     - Avoid any distortion of information and be very precise and accurate, speaking with the language of a teacher educator.
    #     - Pay attention to the language of each part, the default language is Spanish for the indications and descriptions of the titles, and for the narrations of the subtitles.
    # """

    # Generar un archivo JSON y actuar como un creador de videos educativos para YouTube Shorts, creando un guion con tantas partes como sean necesarias que transformen preguntas comunes como "¿Cómo...?" en explicaciones cortas y cautivadoras sobre este tema principal ["{outline}"], con descripciones claras y consistentes en cada parte, y enriquecidas con una narrativa educativa y atractiva para sumergir a la audiencia en el aprendizaje. El guion también debe incorporar los siguientes elementos sin mencionarlos literalmente en la narración, que se usan para el éxito viral en YouTube Shorts:



    if idioma.lower() in ["español", "espanol", "spanish"]:
        video_keyword = palabraclave or f'en Inglés, especificar 3 palabras claves que representen el tema principal ["{outline}"] y el campo ["narration"]. Repite las primeras 2 palabras claves en todos los elementos de "scene_dialog" y agrega una adicional. Es muy importante que sean 3 palabras claves en idioma inglés y que en sea una cadena de texto.'

        prompt = f"""
            Objetivo:

            Actúa como un experto creador de videos para YouTube Shorts de {duracion} segundos o menos, creando un guión que transformen expresiones en contenidos cortos y cautivadores sobre este tema principal ["{outline}"], con descripciones claras y consistentes en cada parte, y enriquecidas con una narrativa educativa y atractiva para sumergir a la audiencia en el aprendizaje. El guion también debe incorporar los siguientes elementos sin mencionarlos literalmente en la narración, que se usan para el éxito viral en YouTube Shorts:

            - Comenzar con algo que sirva de gancho, que capte inmediatamente la atención. Ejemplos: "¿La IA compone una canción en 1 minuto: éxito o fracaso?", "Chatbot de IA organiza mi agenda: ¿Mejor que un asistente?", "Desafío de IA: ¿Quién edita fotos mejor, humano o máquina?", "IA para ahorrar: ¿Realmente reduce mis gastos mensuales?". (No mencionar este elemento literalmente en la narración)
            - Luego ofrecer la solución al gancho con una frase y recomendar quedarse hasta el final del video.
            - Limitar la duración del guión a {duracion} segundos o menos, asegurando que el contenido sea rápido y fácil de consumir.
            - Abordar temas de tendencia, como eventos actuales, desafíos virales, memes populares o temas de gran interés. (No mencionar este elemento literalmente en la narración)
            - Incluir un giro o evento inesperado que genere emoción o sorpresa (OJO: sin mencionar la palabra giro o evento), como un cambio abrupto en la narrativa o una reacción poco común. (No mencionar este elemento literalmente en la narración)
            - Concluir con un mensaje directo para la acción del espectador, como compartir, dar me gusta, comentar o participar en una actividad específica, promoviendo así la participación y difusión del video. (No mencionar este elemento literalmente en la narración)
            - No personalices el guión como si fuera presentado por un anfitrión, ya que este video será producido por una IA por completo.
            - Si vas a hablar de Inteligencia Artificial no uses la palabra "IA", usa el nombre completo.
            
            Identificación de títulos y subtítulos:

            Instrucción Importante: Cada título o subtítulo debe ser descrito de manera detallada y coherente.

            - Nombre del título: [Descripción condensada del título, incluyendo pasos, acciones que el estudiante debe ejecutar para aprender sobre el tema.]
            - Nombre del subtítulo: [Descripción condensada del subtítulo, incluyendo pasos, acciones que el estudiante debe ejecutar para aprender sobre el tema.]
            - [Continuar con otros subtítulos según sea necesario.]

            Estructura JSON del resultado final:

            El JSON es un objeto con un campo principal tipo objeto llamado "script_video_ia", con dos propiedades: "thumbnail_prompt_dalle" y "scene_dialog".

            thumbnail_prompt_dalle: en Inglés, desarrollar un mensaje para DALL·E que describa el tema principal ["{outline}"] con detalle y precisión.
            scene_dialog: Un solo arreglo de entradas narrativas, correspondiente a un título. El arreglo de entradas narrativas debe incluir elementos con esta estructura:
            -- scene_part: Una etiqueta o identificador para la parte específica del título que se está narrando.
            -- narration: El texto narrativo real hablado por el narrador, que debe describir el título, los pasos y las acciones en detalle, en un estilo consistente con el enfoque general del video.
            -- prompt_dalle: en inglés, desarrollar un mensaje para DALL·E que describa la "narración" con detalle y precisión. Debe ser lo suficientemente detallado para que GPT-4 pueda enviarlo directamente a DALL·E sin ningún ajuste adicional.
            -- video_keyword: {video_keyword}
            
            Consistencia en las descripciones y definiciones de título y subtítulo:

            Asegurar que el título y subtítulo sean idénticos en cada objeto del video, al texto proporcionado en el tema principal.
            Evitar cualquier distorsión de la información y ser muy preciso y exacto, hablando con el lenguaje de un educador.
            Prestar atención al idioma de cada parte.
        """
    elif idioma.lower() == "english":
        video_keyword = palabraclave or f'Specify 3 keywords that represent the main topic ["{outline}"] and the field ["narration"]. Repeat the first 2 keywords in all elements of "scene_dialog" and add an additional one. It is very important that they are 3 keywords in a text string.'
    
        prompt = f"""
            Objective:

            Act as an expert video creator for YouTube Shorts of {duracion} seconds or less, creating a script that transforms expressions into short and captivating content about this main topic ["{outline}"], with clear and consistent descriptions in each part, enriched with an educational and engaging narrative to immerse the audience in learning. The script must also incorporate the following elements without mentioning them literally in the narration, which are used for viral success on YouTube Shorts:

            - Start with a hook that immediately captures attention. Examples: "AI composes a song in 1 minute: hit or miss?", "AI chatbot organizes my schedule: Better than an assistant?", "AI Challenge: Who edits photos better, human or machine?", "AI for savings: Does it really reduce my monthly expenses?". (Do not mention this element literally in the narration)
            - Then offer the solution to the hook with a phrase and recommend staying until the end of the video.
            - Limit the script duration to {duracion} seconds or less, ensuring the content is quick and easy to consume.
            - Address trending topics, such as current events, viral challenges, popular memes, or topics of great interest. (Do not mention this element literally in the narration)
            - Include a twist or unexpected event that generates excitement or surprise (NOTE: without mentioning the word twist or event), such as an abrupt change in the narrative or an uncommon reaction. (Do not mention this element literally in the narration)
            - Conclude with a direct message for the viewer's action, such as sharing, liking, commenting, or participating in a specific activity, thereby promoting engagement and dissemination of the video. (Do not mention this element literally in the narration)
            - Do not personalize the script as if presented by a host, as this video will be fully produced by an AI.
            - If talking about Artificial Intelligence, do not use the abbreviation "AI", use the full name.

            Identification of titles and subtitles:

            Important Instruction: Each title or subtitle must be described in a detailed and coherent manner.

            - Title Name: [Condensed description of the title, including steps, actions the student must take to learn about the topic.]
            - Subtitle Name: [Condensed description of the subtitle, including steps, actions the student must take to learn about the topic.]
            - [Continue with other subtitles as necessary.]

            JSON structure of the final result:

            The JSON is an object with a main object-type field called "script_video_ia", with two properties: "thumbnail_prompt_dalle" and "scene_dialog".

            thumbnail_prompt_dalle: Develop a message for DALL·E that describes the main topic ["{outline}"] with detail and precision.
            scene_dialog: A single array of narrative entries, corresponding to a title. The array of narrative entries should include elements with this structure:
            -- scene_part: A label or identifier for the specific part of the title being narrated.
            -- narration: The actual spoken narrative text by the narrator, which should describe the title, steps, and actions in detail, in a style consistent with the overall approach of the video.
            -- prompt_dalle: In English, develop a message for DALL·E that describes the "narration" with detail and precision. It should be detailed enough for GPT-4 to send it directly to DALL·E without any additional adjustments.
            -- video_keyword: {video_keyword}

            Consistency in title and subtitle descriptions and definitions:

            Ensure that the title and subtitle are identical in each video object to the text provided in the main topic.
            Avoid any distortion of information and be very precise and exact, speaking in the language of an educator.
            Pay attention to the language of each partas.
        """

    print("====================================")
    print("prompt, idioma:", prompt, idioma)
    print("====================================")

    # (c) Imagina una serie de ilustraciones para un libro de cuentos para niños que relata una historia bíblica. Cada imagen debe tener una coherencia visual con las demás, manteniendo el mismo estilo artístico y la misma apariencia para los personajes y escenarios a lo largo de toda la historia. Los personajes deben ser fácilmente reconocibles y mantener su identidad en cada imagen, con vestimentas y rasgos consistentes. Genera una descripción detallada de cada personaje y colócala en el campo 'personajes_acto', con el objetivo de preservar la coherencia visual entre las imágenes generadas con DALL-E.

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a useful virtual assistant for story telling about YouTube Shorts."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o",
        # max_tokens=1000,
        temperature=0.7,
        response_format={"type": "json_object"}
    )

    respuesta = response.choices[0].message.content

    respuesta_objeto = json.loads(respuesta)

    # Extract narrations
    narrations = [scene["narration"] for scene in respuesta_objeto["script_video_ia"]["scene_dialog"]]

    print("\n===================================================================\n")

    # Print narrations with new line between them
    for narration in narrations:
        print(narration)
        print()  # Add a new line between narrations

    return respuesta


def generate_keywords(outline):

    prompt = f"""
        Act as an expert finding keywords in outlines like this: [{outline}]. Then generate the main keyword in English that help to find videos related to the outline.
    """

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a useful virtual assistant for story telling about YouTube Shorts. Just return the main keywords separed by spaces between."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o",
        # max_tokens=1000,
        temperature=0.7,
        # response_format={"type": "json_object"}
    )

    respuesta = response.choices[0].message.content
    
    print("KEYWORDS:", respuesta)
    
    return respuesta


def generate_images(script_json):
   
    # print(script)

    acts = script_json["script_video_ia"]["scene_dialog"]

    image_paths = []

    previous_image_prompt = ""

    carpeta = int(time.time())

    for act in acts:
        print("============================", act)
        # personajes = "\n".join([f"{p['name']}: {p['description']}" for p in act['characters']])

        # escena = f"""Crea una imagen en un estilo de animación vibrante y detallado, con estilo Pixar a partir de estos elementos:\n\n
        # [ESCENA: {act['prompt_dalle'].strip()}]\n\n
        # [PERSONAJES: {personajes.strip()}]\n\n
        # """
        # DO NOT add any detail to the prompt, just use it AS-IS: 

        print('ACTS:', acts)

        escena = f"""Create an image rendered in a vibrant and colorful three-dimensional style, inspired by the visual quality and atmosphere of 3D animated movies like 'Toy Story' and 'Shrek'. This image should appeal to a wide audience, with expressive characters and friendly environments that capture the essence of a lively animated world. The focus should be on creating a clear and cheerful presentation, conveying the story in a visually enchanting and easy-to-understand manner, without replicating specific characters from these movies and avoiding traditional clipart or cartoon styles, for a YouTube Short video using this elements:\n\n
        [STEP: {act['prompt_dalle'].strip()}]\n\n
        """

        # [IMPORTANT: Always follow the Prompt Guidelines. Avoid words or concepts that go against terms of service. Do not infringe on anyone's copyright; do not use suggestive or explicit imagery in your prompts. Do not emphasize or imply any elements that would not be considered G-rated.]\r\n
        
        # [BIBLE CHARACTERS: {personajes.strip()}]. Remember to use the Bible characters description exactly as defined in the DALL·E prompt!\n\n

        if (previous_image_prompt != ""):
            continuidad = f"""[FOR VISUAL CONTINUITY: To ensure visual continuity and consistent style with the previous image, I am including the original prompt used in the previous image generation below. This prompt, delimited by three backticks (```), will serve as a reference for DALLE 3, facilitating the creation of a new image that maintains stylistic and visual similarities with the previous one. ```{previous_image_prompt}```]"""
        else:
            continuidad = ""

        prompt = escena # + continuidad
        log(prompt)

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            # size="1024x1024",
            size="1792x1024",
            quality="hd", # hd / standard
            n=1, # 1 a 10
            style="vivid", # natural / vivid
            response_format="b64_json"
        )

        # print(response)

        if hasattr(response, "data"):

            data = response.data

            # log(data)

            # image_url = data[0].url
            image_data = data[0].b64_json
            previous_image_prompt = data[0].revised_prompt

            print("previous_image_prompt:", previous_image_prompt)

            # print(image_url)
            # print(image_data)
            
            # Suponiendo que la respuesta incluye la imagen generada en el campo 'data'
            # image_data = response.json()['data']
            if not os.path.exists(f"./imagenes/{carpeta}"):
                os.mkdir(f"./imagenes/{carpeta}")

            image_path = f"./imagenes/{carpeta}/{acts.index(act)}.png"

            # Aquí deberías escribir la imagen en el sistema de archivos
            with open(image_path, 'wb') as f:
                # f.write(requests.get(image_url).content)
                f.write(b64decode(image_data))
            
            image_paths.append(image_path)
        else:
            log(f"Error generating image", response.text)
            image_paths.append(None)

    return image_paths


def generate_image_prompt(prompt, carpeta, orientacion):
    global CONTADOR_ESCENAS

    MINIATURAS_PATH = os.path.join(BASE_PATH, carpeta)
    IMAGENES_PATH = os.path.join(BASE_PATH, "imagenes")

    print('PROMPT:', prompt)

    # escena = f"""Create a image with orientation {orientacion} and rendered in a vibrant and colorful three-dimensional style, inspired by the visual quality and atmosphere of 3D animated movies like 'Toy Story' and 'Shrek'. This image should appeal to a wide audience, with expressive characters and friendly environments that capture the essence of a lively animated world. The focus should be on creating a clear and cheerful presentation, conveying the story in a visually enchanting and easy-to-understand manner, without replicating specific characters from these movies and avoiding traditional clipart or cartoon styles, for a YouTube Shorts video using this elements:\n\n
    # [STEP: {prompt}]\n\n
    # """

    escena = f"""Create an image with orientation {orientacion} and rendered in a realistic and cinematic three-dimensional style, inspired by the visual quality and atmosphere of modern films. This image should appeal to a wide audience, with expressive characters and detailed environments that capture the essence of a modern world. The focus should be on creating a clear and engaging presentation, conveying the story in a visually captivating and easy-to-understand manner, without replicating specific characters from these movies and avoiding traditional clipart or cartoon styles, for a YouTube Shorts video using this elements:\n\n
        [STEP: {prompt}]\n\n
    """

    # [IMPORTANT: Always follow the Prompt Guidelines. Avoid words or concepts that go against terms of service. Do not infringe on anyone's copyright; do not use suggestive or explicit imagery in your prompts. Do not emphasize or imply any elements that would not be considered G-rated.]\r\n

    # [BIBLE CHARACTERS: {personajes.strip()}]. Remember to use the Bible characters description exactly as defined in the DALL·E prompt!\n\n

    # if (previous_image_prompt != ""):
    #     continuidad = f"""[FOR VISUAL CONTINUITY: To ensure visual continuity and consistent style with the previous image, I am including the original prompt used in the previous image generation below. This prompt, delimited by three backticks (```), will serve as a reference for DALLE 3, facilitating the creation of a new image that maintains stylistic and visual similarities with the previous one. ```{previous_image_prompt}```]"""
    # else:
    #     continuidad = ""

    # prompt = escena # + continuidad
    log(escena)

    if (orientacion == "portrait"):
        desired_size = "1024x1792"
    else:
        desired_size = "1792x1024"

    response = client.images.generate(
        model="dall-e-3",
        prompt=escena,
        # size="1024x1024",
        size=desired_size,
        quality="hd", # hd / standard
        n=1, # 1 a 10
        style="vivid", # natural / vivid
        response_format="b64_json"
    )

    # print(response)

    if hasattr(response, "data"):

        data = response.data
        image_data = data[0].b64_json
        previous_image_prompt = data[0].revised_prompt

        # Usar las constantes para construir las rutas absolutas
        if carpeta == "miniaturas":
            image_path = os.path.join(MINIATURAS_PATH, f"{CONTADOR_ESCENAS}.png")
        else:
            carpeta_path = os.path.join(IMAGENES_PATH, carpeta)
            if not os.path.exists(carpeta_path):
                os.makedirs(carpeta_path)

            image_path = os.path.join(carpeta_path, f"{CONTADOR_ESCENAS}.png")

        # Decodificar la imagen base64 y guardarla usando PIL Image
        image_bytes = b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        image.save(image_path, 'PNG')

        resultado = image_path
    else:
        log(f"Error generating image", response.text)
        resultado = None

    return resultado


def generate_script2(frase_central):
    # prompt = f"Genera un texto breve, coherente y persuasivo para un video corto basado en el título y que dure un minuto o menos, que sea un solo texto corrido, en español, en primera persona, no te presentes, no incluyas las palabras 'discurso', 'motivadora', 'charla'. La frase central es: {title}\n\nGuión:"
    # prompt = f"Genera un texto breve, coherente y persuasivo para un video corto basado en la frase central. Que dure aproximadamente un minuto. Que sea un solo texto corrido. En español. En primera persona. No te presentes. No incluyas las palabras 'discurso', 'motivadora', 'charla'. Evalúa el sentimiento de la frase central utilizando el parámetro '__SENTIMETRIA__:'. La frase central es: {frase_central}\n\nTexto:"
    # prompt = f'Genera un texto breve, coherente y persuasivo para un video corto en español basado en la frase central "{frase_central}". El texto debe durar aproximadamente un minuto y ser un solo párrafo a manera de consejo. No incluyas las palabras o frases "{frase_central}", "discurso", "motivadora", "charla" o "frase central". No incluyas la frase central en el texto. Al final del texto, evalúa la frase central y resúmela en una sola palabra traducida en inglés utilizando el parámetro CDKCENTRO\n\nTexto:\n\nCDKCENTRO:'
    # prompt = f'Genera un guión breve, coherente y persuasivo para un video de un minuto en español basado en esta idea principal "{frase_central}". El guión debe presentarse como un único párrafo en forma de consejo. Evita utilizar palabras o expresiones como "{frase_central}", "discurso", "motivadora", "charla" o "idea principal". No incluyas la idea principal "{frase_central}" directamente en el guión. Al concluir el guión, evalúa la idea principal y resume su esencia en una sola palabra, utilizando el parámetro "CDKTEXTO".\n\nTexto:\n\CDKTEXTO:'
    # prompt = f'Por favor, genera un guión breve y persuasivo para un video corto en español. El video se centrará en la idea de "{frase_central}". Por favor, evita utilizar las palabras "{frase_central}", "discurso", "motivadora", "charla" o "idea principal" en el guión. El guión debe durar aproximadamente un minuto y presentarse como un único párrafo en forma de consejo. Al final del guión, evalúa la idea de "{frase_central}" y resume su esencia en una sola palabra utilizando el parámetro "CDKCENTRO". Por favor, incluye la palabra que resuma su esencia en el parámetro "CDKCENTRO" al final del texto.\n\nGuión:\n\nCDKCENTRO:'
    # prompt = f'Please generate a short and persuasive script for a short video in Spanish. The video will focus on the idea of "{frase_central}". Please avoid using the words "{frase_central}", "speech", "motivational", "chat", or "main idea" in the script. The script should be approximately one minute long and presented as a single paragraph in the form of advice. At the end of the script, it evaluates the idea of "{frase_central}" and summarizes its essence in a single word using the "CDKCENTRO" parameter. Please include the word that sums up your essence in the "CDKCENTRO" parameter at the end of the text.\n\nScript:\n\nCDKCENTRO:'
    # prompt = f'Genera un texto breve, coherente, lenguaje abundante, persuasivo para un video corto de un minuto en español basado en la frase central "{frase_central}". No repitas una misma frase o un mismo patrón. No incluyas las palabras o frases "{frase_central}", "discurso", "motivadora", "charla" o "frase central". No incluyas la frase central en el texto. El resultado final debes retornarlo en formato JSON. El guión colócalo en un parámetro llamado CDKTEXTO. Y valúa la frase central y resúmela en una palabra utilizando el parámetro CDKCENTRO.'
    # prompt = f'Genera un texto, coherente, lenguaje abundante, persuasivo para un video corto de un minuto en español basado en la frase central "{frase_central}". No repitas una misma frase o un mismo patrón. No incluyas las palabras o frases "{frase_central}", "discurso", "motivadora", "charla" o "frase central". No incluyas la frase central en el texto. El resultado final debes retornarlo en formato JSON. El guión colócalo en un parámetro llamado CDKTEXTO. Y valúa la frase central, identifica el sujeto y resúmelo en dos palabras utilizando el parámetro CDKCENTRO.'

    prompt = f'Genera un guión claro, detallado y educativo para un video instruccional de cinco minutos en español basado en la pregunta y los sub-temas contenidos en este outline: ["{frase_central}"]. Asegúrate de que cada sección del guión aborde un sub-tema específico, proporcionando información relevante y coherente. Evita repetir información o patrones. Excluye las palabras o frases "{frase_central}", "tutorial", "instruccional", "lección" o "pregunta principal" dentro del guión. El guión debe presentarse en un formato JSON, con el contenido principal en el parámetro CDKTEXTO. Analiza la pregunta principal y resume su tema en dos palabras, utilizando el parámetro CDKCENTRO para una rápida referencia del tema central del video.'

    print('\n\n', prompt, '\n\n')

    response = client.chat.completions.create(
         messages=[
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o",
        temperature=0.7,
        response_format={"type": "json_object"}
    )

    print('\n\n', response, '\n\n')

    generated_text = response.choices[0].message.content.strip()
    # generated_text = response.choices[0].text.strip()

    print('\ngenerated_text:\n', generated_text, '\n\n')

    response_object = json.loads(generated_text)

    print("CDKTEXTO:", response_object['CDKTEXTO'])
    print("CDKCENTRO:", response_object['CDKCENTRO'])

    result = {
        "generated_text": response_object['CDKTEXTO'],
        "feeling_value": response_object['CDKCENTRO'].lower()
    }

    return result

# Google Text-to-Speech
# Aquí va la implementación para convertir texto a voz
def synthesize_speech(text, output_filename):
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="es-US",
        name="es-US-Studio-B",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        effects_profile_id=["small-bluetooth-speaker-class-device"],
        pitch=-20,
        speaking_rate=0.55
    )

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    with open(output_filename, "wb") as out:
        out.write(response.audio_content)


voices = [
    {"Engine": "generative", "LanguageCode": "en-US", "VoiceId": "Matthew", "Gender": "Male", "TextType": "text", "Newscaster": "news"},
    {"Engine": "generative", "LanguageCode": "en-US", "VoiceId": "Ruth", "Gender": "Female", "TextType": "text", "Newscaster": ""},
    {"Engine": "long-form", "LanguageCode": "en-US", "VoiceId": "Danielle", "Gender": "Female", "TextType": "text", "Newscaster": ""},
    {"Engine": "long-form", "LanguageCode": "en-US", "VoiceId": "Gregory", "Gender": "Male", "TextType": "text", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Danielle", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Gregory", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Ivy", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Joanna", "Gender": "Female", "TextType": "ssml", "Newscaster": "news"},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Kendra", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Kimberly", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Salli", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Joey", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Justin", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Kevin", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Matthew", "Gender": "Male", "TextType": "ssml", "Newscaster": "news"},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Ruth", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Stephen", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "es-US", "VoiceId": "Lupe", "Gender": "Female", "TextType": "ssml", "Newscaster": "news"},
    {"Engine": "neural", "LanguageCode": "es-US", "VoiceId": "Pedro", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "standard", "LanguageCode": "es-US", "VoiceId": "Miguel", "Gender": "Male", "TextType": "ssml", "Newscaster": ""}
]

def get_polly_response(engine, voiceid, text, prosodyrate="90%"):
    voice = next((v for v in voices if v["Engine"] == engine and v["VoiceId"] == voiceid), None)

    print(voice)
    
    if not voice:
        raise ValueError(f"Voice with Engine '{engine}' and VoiceId '{voiceid}' not found.")
    
    text_type = voice["TextType"]
    language_code = voice["LanguageCode"]
    newscaster = voice["Newscaster"]

    if text_type == "text":
        polly_text = text
    elif text_type == "ssml":
        if newscaster == "news":
            polly_text = f'<speak><prosody rate="{prosodyrate}"><amazon:domain name="news">{text}</amazon:domain></prosody></speak>'
        else:
            polly_text = f'<speak><prosody rate="{prosodyrate}">{text}</prosody></speak>'
    else:
        raise ValueError("Invalid TextType")

    print("Engine:", engine)
    print("OutputFormat:", "mp3")
    print("Text:", polly_text)
    print("TextType:", text_type)
    print("VoiceId:", voiceid)
    print("LanguageCode:", language_code)
    
    polly_client = boto3.Session(profile_name='doccumi', region_name="us-east-1").client("polly") #doccumi or cdkpolly
    response = polly_client.synthesize_speech(
        Engine=engine,
        OutputFormat="mp3",
        Text=polly_text,
        TextType=text_type,
        VoiceId=voiceid,
        LanguageCode=language_code,
    )
    
    return response

def text_to_speech_polly(text, output_filename, idioma):
    
    voice = ""
    if idioma.lower() in ["español", "espanol", "spanish"]:
        voice = "Pedro"
    elif idioma.lower() in ["english", "ingles", "inglés"]:
        voice = "Matthew"

    response = get_polly_response("neural", voice, text, "90%")
    
    audio_data = response["AudioStream"].read()
    # audio = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")

    output_file_path = os.path.join(BASE_PATH, output_filename)

    with open(output_file_path, "wb") as out:
        out.write(audio_data)

    # speech_file_path =  Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
        model="tts-1-hd", #tts-1
        voice="nova",
        input=text
    )

    # response.stream_to_file(output_filename)

    # audio = response.read()

    return output_file_path # audio_data or audio or output_filename


def obtener_token_adobe():
    # URL del endpoint para obtener el token
    url = 'https://ims-na1.adobelogin.com/ims/token/v3'

    # Datos que serán enviados en el cuerpo de la solicitud POST
    data = {
        'grant_type': 'client_credentials',
        'client_id': ADOBE_ACCESS_CLIENT_ID,
        'client_secret': ADOBE_ACCESS_CLIENT_SECRET,
        'scope': 'AdobeID,openid,read_organizations,additional_info.projectedProductContext,additional_info.roles,adobeio_api,read_client_secret,manage_client_secrets'
    }

    # Headers para la solicitud
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Realizar la solicitud POST
    response = requests.post(url, headers=headers, data=data)
    return response.json()


# Pexels API
# Aquí va la implementación para buscar videos en Pexels
def search_adobe_stock_video(query):
    bearer_token = obtener_token_adobe()
    # print("bearer_token:", bearer_token['access_token'])
    # Endpoint de la API de Adobe Stock para buscar videos
    # url = "https://stock.adobe.io/Rest/Media/1/Search/Files"
    url = 'https://stock.adobe.io/Rest/Libraries/1/Content/License'

    # Parámetros para la búsqueda
    params = {
        # 'ids': '596582944',
        # 'result_columns[]': ['nb_results','id','video_preview_url','is_premium','premium_level_id','thumbnail_1000_url','video_small_preview_url','comp_url','thumbnail_url'],

        'locale': 'es-ES',  # Ajusta al idioma de preferencia
        # 'search_parameters[words]': query,
        # 'search_parameters[filters][content_type:video]': 1,
        # 'search_parameters[filters][premium]': 'all',
        # 'search_parameters[filters][orientation]': 'vertical',
        # 'search_parameters[limit]': 100,
        # 'result_columns[]': ['nb_results','id','video_preview_url','is_premium','premium_level_id','thumbnail_1000_url','video_small_preview_url','comp_url','thumbnail_url'],
    
        'content_id': '549758956',
        'license': 'Video_HD',
    }

    # Headers con la API Key
    headers = {
        'x-api-key': ADOBE_STOCK_API_KEY,
        'x-product': ADOBE_STOCK_X_PRODUCT,
        'Authorization': 'Bearer ' + bearer_token['access_token']
    }
    
    # print("headers:", headers)

    # Realizar la solicitud
    response = requests.get(url, headers=headers, params=params)
    return response.json()


# Pexels API
# Aquí va la implementación para buscar videos en Pexels
def search_pexels_video(query, orientacion):
    url = f"https://api.pexels.com/v1/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        'query': query,
        'per_page': 20,
        'orientation': orientacion, #'portrait', #'landscape',
        'order_by':'popular'
    }

    print("search_pexels_video - params:", params)

    response = requests.get(url, headers=headers, params=params)
    video_results = response.json()["videos"]

    desired_size = 1280   #640
    # desired_width =  720    #360
    # desired_height = 1280   #640

    background_videos_urls = []

    # random.shuffle(video_results)

    for video in video_results:
        for video_file in video["video_files"]:
            video_width = video_file["width"]
            video_height = video_file["height"]
            
            # if video_width == desired_width and video_height == desired_height:
            if (orientacion == "portrait"):
                if video_height == desired_size:
                # if desired_width == desired_width:
                    video_url = video_file["link"]
                    # print(f"video_url: {video_url}")
                    background_videos_urls.append(video_url)
                    print(video_url)
                    break
                # else:
                    # print(f"link: {video_file}")

            if (orientacion == "landscape"):
                if video_width == desired_size:
                # if desired_width == desired_width:
                    video_url = video_file["link"]
                    # print(f"video_url: {video_url}")
                    background_videos_urls.append(video_url)
                    print(video_url)
                    break
                # else:
                    # print(f"link: {video_file}")

    return background_videos_urls


# Pexels API
# Aquí va la implementación para buscar videos en Pexels
def search_envato_video(query, orientacion):
    url = f"https://api.envato.com/v1/discovery/search/search/item"
    headers = {"Authorization": f"Bearer {ENVATO_API_KEY}" }
    params = {
        'term': query,
        'site': 'videohive.net',
        # 'orientation': orientacion, #'portrait', #'landscape',
        'resolution_min': '720p',
        'page': 1,
        'page_size': 20,
        'sort_by': 'relevance',
        'sort_direction': 'asc'
    }

    print("search_envato_video - params:", params)

    response = requests.get(url, headers=headers, params=params)

    items = response.json().get('matches', [])

    if response.status_code == 200:
        items = response.json().get('matches', [])
        download_urls = []
        
        for item in items:
            item_id = item['id']
            print(f'Processing item ID: {item_id}')
            if envato_check_item_purchasable(item_id):
                download_url = get_envato_video_url(item_id)
                if download_url:
                    download_urls.append(download_url)
        
        print("search_envato_video - download_urls:", download_urls)
        return download_urls
    else:
        print('Error in search request:', response.status_code, response.text)
        return []


def get_envato_video_url(item_id):
    url = f'https://api.envato.com/v3/market/buyer/download?item_id={item_id}'
    headers = {
        'Authorization': f'Bearer {ENVATO_API_KEY}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('download_url', None)
    else:
        print('Error in download link request:', response.status_code, response.text)
        return None


def envato_check_item_purchasable(item_id):
    url = f'https://api.envato.com/v3/market/buyer/purchase?item_id={item_id}'
    headers = {
        'Authorization': f'Bearer {ENVATO_API_KEY}'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return True
    else:
        print(f'Item ID {item_id} is not purchasable. Response: {response.status_code}, {response.text}')
        return False


# Aquí va la implementación para descargar videos
def download_video(url, output_filename):
    print('----------------------- url:', url)
    response = requests.get(url, stream=True)
    print('----------------------- response:', response)
    
    # Obtener el ancho de la terminal actual
    terminal_width = os.get_terminal_size().columns / 2
    print('----------------------- terminal_width:', terminal_width)
    
    total_size = int(response.headers.get("content-length", 0))
    print('----------------------- total_size:', total_size)

    block_size = 8192
    progress_bar = tqdm(total=total_size, unit="iB", unit_scale=True, ncols=int(terminal_width))
    print('----------------------- progress_bar:', progress_bar)
    print('----------------------- output_filename:', output_filename)

    with open(output_filename, "wb") as output_file:
        for chunk in response.iter_content(block_size):
            progress_bar.update(len(chunk))
            output_file.write(chunk)

    progress_bar.close()


def resize_video(input_file, output_file, width, height):
    # Open video file
    video = mpe.VideoFileClip(input_file)
    video_resized = video.resize(width=width, height=height, method='black')
    video_resized.write_videofile(output_file)

def resize_and_pad(input_file, output_file, width, height):
    # Abrir el archivo de video con MoviePy
    video_clip = mpe.VideoFileClip(input_file)
    # Cambiar el tamaño del video mientras mantiene la proporción
    resized_clip = video_clip.resize(height=height)
    # Verificar si el ancho del video se ha reducido después de cambiar su altura para que quepa dentro del nuevo tamaño de la ventana
    if resized_clip.size[0] < width:
        # Calcular la cantidad de relleno necesario a la izquierda y derecha del video
        padding_size = (width - resized_clip.size[0]) / 2
        # Crear un clip de color sólido del tamaño de la ventana deseada
        padding_clip = mpe.ColorClip((width, height), color=(0, 0, 0))
        # Combinar los clips de video y de relleno
        # print(resized_clip)
        print(resized_clip.duration)
        final_clip = mpe.CompositeVideoClip([padding_clip.set_position(('left', 0)), resized_clip.set_position(('left', 0))])
        # print(final_clip)
        final_clip.write_videofile(output_file) #, codec='libx264', duration=resized_clip.duration
    else:
        # Si el ancho del video es igual o mayor que el ancho de la ventana, simplemente devolvemos el clip redimensionado
        resized_clip.write_videofile(output_file)


def find_file_by_keyword(directory, keyword):
    # Crea una lista con todos los archivos que contienen la palabra clave
    matching_files = [f for f in os.listdir(directory) if keyword in f]

    # Si no se encontraron archivos que coincidan, regresa None
    if len(matching_files) == 0:
        return None

    # Si se encontró un archivo que coincide, regresa su nombre
    if len(matching_files) == 1:
        return matching_files[0]

    # Si se encontraron múltiples archivos que coinciden, elige uno aleatoriamente
    archivo_seleccionado = os.path.join(directory, random.choice(matching_files))
    return archivo_seleccionado

# Crear video con video de fondo y audio
# Aquí va la implementación para combinar video de fondo y audio
def create_video_with_background_video_old(images, background_videos, audio_files, background_music, output_filename):
    # Descargar los videos de fondo
    segundos_videos = 3
    video_filenames = []
    for i, url in enumerate(background_videos):
        input_filename = f'./resources/background_video_{i}.mp4'
        download_video(url, input_filename)
        video_filenames.append(input_filename)

    # Cargar y recortar fragmentos de N segundos al azar de cada video de fondo
    video_clips = []
    for f in video_filenames:
        clip = mpe.VideoFileClip(f)
        clip_duration = clip.duration
        start_times = [random.uniform(0, clip_duration - segundos_videos) for i in range(int(clip_duration / segundos_videos))]
        start_times.sort()
        clips = [clip.subclip(t, t+segundos_videos) for t in start_times]
        video_clips.append(clips)
        print(f'filename: {f} | clip_duration: {clip_duration} | num_clips: {len(clips)}')

    # Consolidar los fragmentos del video
    final_clips = []
    max_num_clips = max([len(clips) for clips in video_clips])
    for i in range(max_num_clips):
        for j in range(len(video_clips)):
            if i < len(video_clips[j]):
                clip = video_clips[j][i]
                if clip.duration < segundos_videos:
                    # Si el fragmento es menor a N segundos, se suma al siguiente fragmento
                    if i < max_num_clips - 1 and len(video_clips[j]) > i + 1:
                        next_clip = video_clips[j][i+1]
                        if next_clip.duration >= segundos_videos:
                            next_clip = next_clip.subclip(0, segundos_videos - clip.duration)
                            clip = mpe.concatenate_videoclips([clip, next_clip])
                            video_clips[j][i+1] = next_clip.subclip(segundos_videos - clip.duration)
                    else:
                        # Si es el último fragmento, se agrega tal cual
                        pass
                else:
                    # Si el fragmento es de N segundos, se agrega tal cual
                    pass
                final_clips.append(clip)

    # Concatenar los clips de video
    video = mpe.concatenate_videoclips(final_clips)

    # Cargar y combinar archivos de audio
    voice_audio = mpe.CompositeAudioClip([mpe.AudioFileClip(f) for f in audio_files])
    music_audio = mpe.AudioFileClip(background_music).volumex(0.10)
    music_audio = music_audio.set_duration(voice_audio.duration)
    final_audio = mpe.CompositeAudioClip([voice_audio, music_audio])
    final_audio = add_fade_in_out_audio(final_audio, 1)

    # Repetir el video de fondo para cubrir la duración del audio
    video_duration = video.duration
    audio_duration = final_audio.duration
    repetitions = int(audio_duration / video_duration) + 1

    print(f'audio_duration: {audio_duration}')
    print(f'video_duration: {video_duration}')
    print(f'repetitions: {repetitions}')

    # PENDIENTE GUARDAR EN DISCO LOS VIDEO CLIPS GENERADOS CON UNA SECUENCIA NUMERICA.

    video = mpe.concatenate_videoclips([video] * repetitions)
    video = video.subclip(0, audio_duration)

    # Establecer el audio del video
    video = video.set_audio(final_audio)

    # Agregar efectos de fundido en entrada y salida
    video = add_fade_in_out_effect(video, 2)

    # Guardar el video resultante
    video.write_videofile(output_filename, codec='libx264', audio_codec='aac') #libmp3lame

    # Eliminar archivos temporales de video
    for filename in video_filenames:
        os.remove(filename)


def create_video_with_background_video(elementos_partes, titulo, output_filename, background_music, thumbnail_background_filename, orientacion):
    
    # print("elementos_partes:", elementos_partes)
    print("output_filename:", output_filename)
    print("background_music:", background_music)
    print("thumbnail_background_filename:", thumbnail_background_filename)
    # return None

    elementos = {}

    # Recorrer el arreglo
    for elemento in elementos_partes:
        # Recorrer cada clave en el elemento
        for clave in elemento:
            # Si la clave no está en el diccionario, agregarla y crear una lista vacía
            # Añadir el valor correspondiente a la lista de esa clave
            elementos.setdefault(clave, []).append(elemento[clave])

    # Concatenar los clips de video
    print("====================== KLK ===========================")
    print(elementos["clip"])
    print("====================== KLK ===========================")
    print(elementos["audio"])
    print("====================== KLK ===========================")
    video = mpe.concatenate_videoclips(elementos["clip"])

    # voice_audio = mpe.CompositeAudioClip([mpe.AudioFileClip(f) for f in audio_paths])
    voice_audio = concatenate_audioclips([AudioFileClip(f) for f in elementos["audio"]])
    print(f'voice_audio.duration: {voice_audio.duration}')

    music_audio = mpe.AudioFileClip(background_music).volumex(0.10)
    print(f'music_audio.duration A: {music_audio.duration}')
    music_audio = music_audio.set_duration(voice_audio.duration)
    print(f'music_audio.duration B: {music_audio.duration}')
    final_audio = mpe.CompositeAudioClip([voice_audio, music_audio])
    print(f'final_audio.duration: {final_audio.duration}')

    final_audio = add_fade_in_out_audio(final_audio, 1)

    # Repetir el video de fondo para cubrir la duración del audio
    video_duration = video.duration
    audio_duration = final_audio.duration
    repetitions = int(audio_duration / video_duration) + 1

    print(f'audio_duration: {audio_duration}')
    print(f'video_duration: {video_duration}')
    print(f'repetitions: {repetitions}')
    print(f'voice_audio.duration: {voice_audio.duration}')

    # PENDIENTE GUARDAR EN DISCO LOS VIDEO CLIPS GENERADOS CON UNA SECUENCIA NUMERICA.

    video = mpe.concatenate_videoclips([video] * repetitions)
    video = video.subclip(0, audio_duration)

    # Establecer el audio del video
    video = video.set_audio(final_audio)

    if 'narration' in elementos:
        narration_clips = []
        current_time = 0

        # for text in elementos['narration']:
        for index, text in enumerate(elementos['narration']):
            text = text.replace(",", "").replace(".", "")
            audio_file = elementos["audio"][index]
            audio_clip = AudioFileClip(audio_file)
            audio_duration_calculated = audio_clip.duration
            # Calcular el tiempo de despliegue de cada palabra
            tiempos_palabras = calcular_tiempo_por_palabra(text, audio_duration_calculated)  # Asumiendo que 'duracion_total' es la duración total del video en segundos

            for palabra, duracion in tiempos_palabras:
                # text_clip = TextClip(palabra, fontsize=50, color='white', size=video.size).set_duration(duracion).set_pos('center').set_start(current_time)

                text_clip = TextClip(
                    palabra, #.replace(",", "").replace(".", "")
                    # size=(200, 50),
                    font='Lane',
                    fontsize=50,
                    color='white',
                    method='caption',
                    align='center'
                ).set_duration(duracion).set_pos(('center', 'center')).set_start(current_time) #, size=video.size
                txt_size = text_clip.size
                # print("create_video_with_background_video -> txt_size:", txt_size)

                bg_size = (txt_size[0] + 10, txt_size[1] + 10)
                # print("create_video_with_background_video -> bg_size:", bg_size)

                bg_clip = ColorClip(size=bg_size, color=(0, 0, 0), duration=duracion).set_opacity(0.7).set_position(('center', 'center')).set_start(current_time)
            
                tamano_video = video.size
                altura_deseada = tamano_video[1] - (tamano_video[1] * 0.3)

                combined_clip_temp = mpe.CompositeVideoClip([bg_clip.set_position("center"), text_clip], size=(300, 100))

                combined_clip = combined_clip_temp.set_position(("center", altura_deseada))

                narration_clips.append(combined_clip)
                current_time += duracion


        print("create_video_with_background_video -> current_time:", current_time)

        # Añadir los TextClips al video

        thumbnail_filename = crear_thumbnail(titulo.replace(" ", "\n"), thumbnail_background_filename, "", orientacion)

        # Convertir la imagen en un ImageClip
        thumbnail_clip_temp = mpe.ImageClip(os.path.join(BASE_PATH, thumbnail_filename)).set_duration(1) #.set_start(0)  # Duración de 5 segundos, ajusta según necesites

        thumbnail_clip = thumbnail_clip_temp.set_position("center")

        video_con_narracion = mpe.CompositeVideoClip([video] + narration_clips)

        clips_finales = [thumbnail_clip, video_con_narracion]

        video_final = mpe.concatenate_videoclips(clips_finales)

    # Agregar efectos de fundido en entrada y salida
    video = add_fade_in_out_effect(video_final, 2)

    # Guardar el video resultante

    partes = output_filename.split(":")

    print(partes)

    output_filename = os.path.join(BASE_PATH, partes[0])

    video.write_videofile(output_filename, codec='libx264', audio_codec='aac') #libmp3lame

    # Eliminar archivos temporales de video OJO
    # for filename in elementos["clip"]:
    #     os.remove(filename)


def add_fade_in_out_effect(video_file, fade_duration=2):
    # fadein = mpv.fx.all.fadein(video_file, fade_duration)
    fadeout = mpv.fx.all.fadeout(video_file, fade_duration)
    return fadeout


def add_fade_in_out_audio(audio_file, fade_duration=1):
    fadein = mpa.fx.all.audio_fadein(audio_file, fade_duration)
    fadeout = mpa.fx.all.audio_fadeout(fadein, fade_duration / 2)
    return fadeout


# YouTube Data API v3
# Aquí va la implementación para autenticar con la API de YouTube
def get_authenticated_service():
    # Configura tus credenciales aquí
    CLIENT_SECRET_FILE = "client_secret_desktopapp.json"
    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    #https://www.googleapis.com/auth/youtube.force-ssl

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    # print(flow)
    credentials = flow.run_local_server(port=0)
    # print(credentials)
    youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    return youtube


# Aquí va la implementación para subir el video a YouTube
def upload_video(youtube, video_file, title, description):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": "22",
            "tags": ["motivacion", "Motivación", "Éxito", "Superación"],
            "defaultLanguage": "",
            "defaultAudioLanguage": "",
            "defaultLanguage": "",
        },
        "status": {
            "privacyStatus": "unlisted",
            "madeForKids": True,
            "embeddable": True,
            "publicStatsViewable": True,
            "hideLikes": True,
            "license": "youtube" # "creativeCommon"
        }
    }

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        _, response = request.next_chunk()

    return response


# Función para extraer todos los valores de "narration"
def extract_narrations(script):
    narrations = []
    json_data = json.loads(script)
    for script in json_data['script_video_ia']:
        for scene in script['scene_dialog']:
            narrations.append(scene['narration'])
    return "\r\n".join(narrations)


def obtener_duracion_audio(ruta_audio):
    # Cargar el archivo de audio
    print("ruta_audio:", ruta_audio)
    audio = AudioSegment.from_file(ruta_audio)

    # Calcular la duración en milisegundos y convertirla a segundos
    duracion_ms = len(audio)
    duracion_sec = duracion_ms / 1000.0

    return duracion_sec


def calcular_ppm(texto, duracion_segundos):
    num_palabras = len(texto.split())  # Contar el número total de palabras
    duracion_minutos = duracion_segundos / 60  # Convertir la duración a minutos
    ppm = num_palabras / duracion_minutos  # Calcular las palabras por minuto

    print("calcular_ppm() -> duracion_segundos:", duracion_segundos)
    print("calcular_ppm() -> num_palabras:", num_palabras)
    print("calcular_ppm() -> duracion_minutos:", duracion_minutos)
    print("calcular_ppm() -> ppm:", ppm)
    return ppm


def calcular_tiempo_por_palabra2(texto, duracion_total):
    velocidad_ppm = calcular_ppm(texto, duracion_total)
    # print("calcular_tiempo_por_palabra() -> velocidad_ppm:", velocidad_ppm)

    palabras = texto.split()
    num_palabras = len(palabras)
    # print("calcular_tiempo_por_palabra() -> num_palabras:", num_palabras)

    duracion_minutos = duracion_total / 60
    # print("calcular_tiempo_por_palabra() -> duracion_minutos:", duracion_minutos)

    velocidad_ppm_real = num_palabras / duracion_minutos
    # print("calcular_tiempo_por_palabra() -> velocidad_ppm_real:", velocidad_ppm_real)

    # Ajustar la velocidad a la velocidad de PPM dada, si es necesario
    factor_ajuste = velocidad_ppm / velocidad_ppm_real if velocidad_ppm < velocidad_ppm_real else 1

    # print("calcular_tiempo_por_palabra() -> factor_ajuste:", factor_ajuste)

    tiempo_promedio_por_palabra = duracion_total / num_palabras * factor_ajuste
    # print("calcular_tiempo_por_palabra() -> duracion_total:", duracion_total)
    # print("calcular_tiempo_por_palabra() -> num_palabras:", num_palabras)
    # print("calcular_tiempo_por_palabra() -> factor_ajuste:", factor_ajuste)
    # print("calcular_tiempo_por_palabra() -> tiempo_promedio_por_palabra:", tiempo_promedio_por_palabra)

    longitud_total = sum(len(palabra) for palabra in palabras)
    # print("calcular_tiempo_por_palabra() -> longitud_total:", longitud_total)

    tiempos = []
    
    for palabra in palabras:
        factor_proporcional = len(palabra) / longitud_total
        tiempo_palabra = tiempo_promedio_por_palabra / factor_proporcional
        # print("calcular_tiempo_por_palabra() -> palabra, factor_proporcional, tiempo_palabra:", palabra, factor_proporcional, tiempo_palabra)

        tiempos.append((palabra, tiempo_palabra))

    return tiempos


def calcular_tiempo_por_palabra(texto, duracion_total):
    palabras = texto.split()
    num_palabras = len(palabras)
    # print("calcular_tiempo_por_palabra() -> num_palabras:", num_palabras)

    longitud_total = sum(len(palabra) for palabra in palabras)
    # print("calcular_tiempo_por_palabra() -> longitud_total:", longitud_total)

    if longitud_total == 0 or num_palabras == 0:
        return []

    # Tiempo total en segundos asignado a una letra
    tiempo_por_letra = duracion_total / longitud_total
    # print("calcular_tiempo_por_palabra() -> tiempo_por_letra:", tiempo_por_letra)

    tiempos = []
    for palabra in palabras:
        # Tiempo para la palabra actual, basado en su longitud
        tiempo_palabra = tiempo_por_letra * len(palabra)
        # print("calcular_tiempo_por_palabra() -> palabra, tiempo_por_letra, tiempo_palabra:", palabra, tiempo_por_letra, tiempo_palabra)

        tiempos.append((palabra, tiempo_palabra))

    return tiempos


def procesar_scene(scene, carpeta, orientacion, idioma):
    global CONTADOR_ESCENAS

    print("scene:", scene)
    # output_filename = f"./audios/audio_{CONTADOR_ESCENAS}.mp3"
    output_filename = os.path.join(BASE_PATH, f"audios/audio_{CONTADOR_ESCENAS}.mp3")
    single_text_with_space = scene["video_keyword"] #" ".join(scene["video_keyword"])
    video_keyword = scene["video_keyword"].split(", ")

    print("single_text_with_space:", single_text_with_space)

    # CODIGO OK
    # videos_envato = search_envato_video(single_text_with_space, orientacion)
    # CODIGO OK

    # CODIGO OK
    videos_storyblocks = search_storyblocks_videos(api_key, secret_key, expires, user_id, project_id, single_text_with_space)
    # CODIGO OK

    # print("videos_storyblocks:", videos_storyblocks)
    print("video_keyword[0]:", video_keyword[0])
    videos_pexels = search_pexels_video(video_keyword[0], orientacion)
    # videos_pexels = search_pexels_video(single_text_with_space)
    # print("videos_pexels:", videos_pexels)

    # CODIGO OK
    videos = videos_storyblocks or videos_pexels
    # CODIGO OK
    # videos = videos_pexels

    print("# de videos A:", len(videos))
    if len(videos) == 0:
        videos = search_pexels_video(single_text_with_space, orientacion)
        print("# de videos B:", len(videos))
    audio = text_to_speech_polly(scene["narration"], output_filename, idioma)
    imagen = "" #generate_image_prompt(scene["prompt_dalle"], carpeta, "horizontal")
    duracion_audio = obtener_duracion_audio(output_filename)
    clip = generar_clips(videos, duracion_audio, orientacion)

    return {
        "videos": videos,
        "audio": audio,
        "imagen": imagen,
        "clip": clip,
        "duracion_audio": duracion_audio,
        "narration": scene["narration"]
    }


def generar_clips_original(videos, duracion_audio):
    # Crea clips de 5 segundos de cada video y los concatena hasta alcanzar la duración del audio.
    clips_concatenados = []
    tiempo_actual = 0
    indice_video = 0

    while tiempo_actual < duracion_audio:
        clip = VideoFileClip(videos[indice_video]).subclip(0, 5)  # Asume que cada video tiene al menos 5 segundos
        clips_concatenados.append(clip)
        tiempo_actual += 5
        indice_video = (indice_video + 1) % len(videos)  # Cicla a través de los videos


    clip_final = concatenate_videoclips(clips_concatenados, method="compose")

    output_filename = f"./clips/clip_{CONTADOR_ESCENAS}.mp4"

    clip_final.write_videofile(output_filename, codec='libx264', audio_codec='aac') #libmp3lame

    return clip_final # or output_filename


# Redefinir la función resizer dentro de moviepy
def patched_resizer(pic, newsize):
    pilim = Image.fromarray(pic)
    resized_pil = pilim.resize(newsize, Image.LANCZOS)
    return np.array(resized_pil)

# Aplicar el parche
resize_fx.resizer = patched_resizer

def generar_clips(videos, duracion_audio, orientacion):
    # Dimensiones de la salida deseada (vertical)

    random.shuffle(videos)

    print("duracion_audio:", duracion_audio)

    segundos_videos = 3

    if (orientacion == "portrait"):
        desired_width = 720
        desired_height = 1280
    else:
        desired_width = 1280
        desired_height = 720

    clips_concatenados = []
    tiempo_actual = 0
    indice_video = 0

    while tiempo_actual < duracion_audio:
        print('videos[indice_video]:', videos[indice_video])
        video_url = videos[indice_video]
        local_filename = os.path.join(BASE_PATH, f"video_{indice_video}.mp4")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        with requests.get(video_url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        # Procesar el video localmente con MoviePy
        clip = VideoFileClip(local_filename).subclip(0, segundos_videos)

        # Obtener las dimensiones del clip original
        original_width, original_height = clip.size

        print("original_width, original_height:", original_width, original_height)

        # Verificar si el video es horizontal
        if orientacion == "portrait" and original_width > original_height:
            # Calcular el nuevo ancho para mantener la relación de aspecto vertical
            new_width = original_height * (desired_width / desired_height)
            x_center = original_width / 2
            x1 = x_center - new_width / 2
            x2 = x_center + new_width / 2
            print("new_width:", new_width)
            print("x_center:", x_center)
            print("x1:", x1)
            print("x2:", x2)
            print("desired_width, desired_height:", desired_width, desired_height)

            # Recortar el video al nuevo ancho y la altura original
            clip = clip.crop(x1=x1, x2=x2, y1=0, y2=original_height)
        
        # Redimensionar el video a las dimensiones deseadas (720x1280)
        print ("=======================")
        print("clip:", clip)
        print ("=======================")

        clip = clip.resize((desired_width, desired_height))
        clips_concatenados.append(clip)

        tiempo_actual += segundos_videos
        indice_video = (indice_video + 1) % len(videos)

    # Concatenar todos los clips ajustados
    clip_final = concatenate_videoclips(clips_concatenados, method="compose")

    # Construir la ruta del archivo de salida usando BASE_PATH
    output_filename = os.path.join(BASE_PATH, f"clips/clip_{CONTADOR_ESCENAS}.mp4")

    # Crear la carpeta de salida si no existe
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    # Guardar el clip final concatenado
    print("output_filename:", output_filename)
    clip_final.write_videofile(output_filename, codec='libx264', audio_codec='aac')

    return clip_final  # o output_filename


def crear_thumbnail(titulo, ruta_fondo, ruta_persona, orientacion):
    # Cargar la imagen de fondo y la imagen de la persona

    if (orientacion == "portrait"):
        desired_width = 720
        desired_height = 1280
    else:
        desired_width = 1280
        desired_height = 720

    fondo = Image.open(ruta_fondo)
    fondo = fondo.resize((desired_width, desired_height))  # Tamaño para YouTube Shorts
    imagen_final = Image.new('RGB', fondo.size, (255, 255, 255))
    imagen_final.paste(fondo, (0,0))

    # Crear y superponer layer negro con opacidad del 50%
    negro_con_opacidad = Image.new('RGBA', fondo.size, (0, 0, 0, 127))  # 127 es aproximadamente 50% de opacidad
    imagen_final.paste(negro_con_opacidad, (0,0), negro_con_opacidad)  # Usando la misma imagen como máscara para mantener la opacidad

    if (ruta_persona != ""):
        persona = Image.open(ruta_persona)
        persona = persona.resize((700, 700))
        if persona.mode != 'RGBA':
            persona = persona.convert('RGBA')
        posicion_persona = (30, 600)
        imagen_final.paste(persona, posicion_persona, persona)

    # Agregar texto con padding
    draw = ImageDraw.Draw(imagen_final)
    font = ImageFont.truetype(os.path.join(BASE_PATH, 'fonts/bebas_neue/BebasNeue-Regular.ttf'), 110)
    padding = 40  # Ajusta el padding a tu gusto
    lineas = wrap(titulo, width=15)
    y = 175 + padding
    for linea in lineas:
        # ancho_linea, _ = font.font.getsize(linea)
        (width, height), (offset_x, offset_y) = font.font.getsize(linea)
        draw.text(((720 - width) // 2, y), linea, (255, 255, 255), font=font)
        y += height + padding

    nombre_thumbnail = titulo.replace("\n", "_")
    filename = f'thumbnails/{nombre_thumbnail}.jpg'
    imagen_final.save(os.path.join(BASE_PATH, filename))

    return filename


# Función principal
def main(outline, musica, palabraclave, idioma, orientacion, duracion):
    global CONTADOR_ESCENAS

    # titulo = outline.split('\n')[1].strip().replace('¿', '').replace('?', '')

    partes_titulos = outline.split(":")

    print("\n======================== partes_titulos:\n", partes_titulos, "\n========================\n")

    titulo = partes_titulos[0]

    feeling = ""

    # feeling = """
    #     ¿Cómo crear una cuenta de correo Gmail?

    #     En la computadora (pc):

    #     1 - Ingresá a Gmail y seleccioná “Crear cuenta”.
    #     2 - Completá los datos solicitados: nombre, apellidos, nombre de usuario y contraseña. Si el usuario ya está en uso, tenés que elegir otro.
    #     3 - Por seguridad, Gmail solicita un número de teléfono al que te enviará un código de verificación. Ingresá el código que recibas.
    #     4 - Completá los datos solicitados: fecha de nacimiento y sexo.
    #     5 - Gmail ofrece la opción de añadir un número de teléfono asociado a tu cuenta (opcional).
    #     6 - Por último, tenés que leer y aceptar las Condiciones de Servicio de Gmail, ¡y listo!

    #     En el celular:

    #     1 - Ingresá a Gmail y seleccioná “Crear cuenta”
    #     2 - Ingresá los datos solicitados: nombre, apellidos, fecha de nacimiento y sexo.
    #     3 - Elegí un nombre de usuario para tu dirección de correo electrónico. Si ya está en uso, tendrás que elegir otro.
    #     4 - Creá una contraseña segura: debe tener 8 (ocho) caracteres como mínimo, y podés combinar letras, números y símbolos.
    #     5 - Gmail te ofrece la opción de añadir un número de teléfono asociado a tu cuenta (opcional).
    #     6 - Por último, deberás Leer y Aceptar las Condiciones de Servicio de Gmail, ¡y listo!
    # """
    # print('# sentimiento inglés:', feeling)

    # Buscar video relacionado
    # adobe_stock_videos = search_adobe_stock_video(feeling)
    # print("adobe_stock_videos:", adobe_stock_videos)

    # titulo = translate_client.translate(title, target_language='es')['translatedText']
    print('# título español:', feeling or titulo or outline)

    script = generate_script(outline, palabraclave, idioma, duracion)
    script_json = json.loads(script)

    # script = '{"script_video_ia":[{"scene_dialog":[{"scene_part":"Introducción","narration":"¿Te imaginas transformar hilo en arte para tu hogar? Hoy aprenderemos a hacer cojines y fundas de crochet.","prompt_dalle":"Create an image of a cozy living room with crochet cushions and covers on the sofa, showcasing a handmade, artistic atmosphere.","video_keyword":"Crochet Cushions and Covers"},{"scene_part":"Materiales Necesarios","narration":"Primero, selecciona tu hilo favorito y ganchillos de crochet adecuados para el tamaño.","prompt_dalle":"Display a variety of colorful yarns and different sizes of crochet hooks arranged neatly, ready for crafting.","video_keyword":"Crochet Materials"},{"scene_part":"Inicio del Proyecto","narration":"Comenzamos con un anillo mágico, base para cojines perfectos. ¡Es más fácil de lo que piensas!","prompt_dalle":"Illustrate hands forming a magic ring with crochet, indicating the beginning of a crochet cushion project.","video_keyword":"Magic Ring Crochet"},{"scene_part":"Desarrollo del Patrón","narration":"Sigue el patrón de puntos, crea formas y texturas únicas. Cada puntada acerca a un cojín con personalidad.","prompt_dalle":"Show a close-up of hands crocheting intricate patterns on a cushion cover, emphasizing the creation of unique shapes and textures.","video_keyword":"Crochet Patterns"},{"scene_part":"Cierre Sorpresa","narration":"Y cuando menos lo esperas, ¡zas! Cierras el último punto y... tienes una obra maestra en tus manos.","prompt_dalle":"Visualize the moment of finishing the last stitch on a crochet cushion cover, revealing a beautiful, completed masterpiece.","video_keyword":"Crochet Masterpiece"},{"scene_part":"Llamado a la Acción","narration":"Ahora es tu turno, elige tus colores y empieza a tejer. Comparte tus creaciones y ¡sorprende al mundo con tu talento!","prompt_dalle":"Create an inspiring image of a completed crochet cushion with an invitation to start crocheting, encouraging viewers to share their own creations.","video_keyword":"Crochet Call to Action"}]}]}'
    print("============================== INICIO GUION ==================================")
    print(script)
    print("============================== FINAL GUION ===================================")
    # keywords = generate_keywords(outline)
    print("============================== INICIO KEYWORDS ===============================")
    # print(keywords)
    print("============================== FINAL KEYWORDS ================================")
    # images = generate_images(script_json)
    print("============================== INICIO IMAGENES ===============================")
    # print(images)
    print("============================== FINAL IMAGENES ================================")
    thumbnail_prompt_dalle = script_json["script_video_ia"]["thumbnail_prompt_dalle"]
    print("thumbnail_prompt_dalle", thumbnail_prompt_dalle)

    thumbnail_filename = generate_image_prompt(thumbnail_prompt_dalle, "miniaturas", orientacion)
    # crear_thumbnail(titulo.replace(" ", "\n"), thumbnail_filename, "")

    # Usar la función para obtener el texto generado
    # generated_text = extract_narrations(script)

    elementos_partes = []
    carpeta_elementos = int(time.time())

    # json_data = json.loads(script)
    script_ia = script_json['script_video_ia']
    # print("script_ia:", script_ia)
    for dialog in script_ia["scene_dialog"]:
        CONTADOR_ESCENAS += 1
        elementos = procesar_scene(dialog, carpeta_elementos, orientacion, idioma)
        elementos_partes.append(elementos)
        # print("elementos:", elementos)

    # Crear video con el video de fondo y audio
    video_filename = f"videos/{titulo}_{tiempo}.mp4"
    background_music = find_file_by_keyword(os.path.join(BASE_PATH, f"music"), musica)
    print(f"background_music: {background_music}")
    # create_video_with_background_video(images, background_videos_urls, audio_files, background_music, video_filename)
    create_video_with_background_video(elementos_partes, titulo, video_filename, background_music, thumbnail_filename, orientacion)

    print('# Crear video con el video de fondo y audio')
    print(video_filename)


    # IMPORTANTE NO BORRAR, ES PARTE DEL CODIGO PARA SUBIR A YOUTUBE DIRECTAMENTE

    # # Subir video a YouTube
    # youtube = get_authenticated_service()

    # print('Autenticando usuario para subir video a YouTube')
    # print(youtube)

    # response = upload_video(youtube, video_filename, title, script)
    # print(f"Video subido con éxito: {response['id']}")

    # print(response)

    # IMPORTANTE NO BORRAR, ES PARTE DEL CODIGO PARA SUBIR A YOUTUBE DIRECTAMENTE


def obtener_subject_por_id(subject_id):
    # Definir el arreglo de subjects
    subjects = [
        """
        ¿Cómo hacer Arroz Blanco?

        Ingredientes:

            - 1 Libra Arroz Largo
            - 2 1/2 Tazas Agua
            - 1/2 Cucharada grande Sal
            - 1 Cucharada grande Aceite De Girasol

        Pasos para la preparación:

            - Paso 1: Lleve al fuego un caldero de fondo grueso con el agua y la sal, cuando rompa el hervor, añade el arroz, cocina a fuego medio hasta que el arroz absorba toda el agua, tapa y cocina a fuego bajo por 20 minutos aproximadamente.
            - Paso 2: Pasado el tiempo, vierte el aceite, deja cocinar por tres minutos más, retira del fuego y sirve.
        """,
        """
        ¿Cómo hacer Flan de Caramelo?

        Utensilios: 
        
            - Mezclador
            - Horbo
            - Plato de hornear

        Ingredientes:

            - 5 Unidades Huevo
            - 2 Unidades Leche Evaporada Carnation UHT 300ml
            - 1 Lata Leche Condensada La Lechera® 403G.
            - 1/4 Cucharadita Sal De Mesa
            - 1/2 Cucharadita Extracto De Vainilla
            - 1 Taza Azúcar
            - 1/4 Taza Agua

        Pasos para la preparación:

            Paso 1: Prepara un almíbar con el agua y el azúcar, acaramela un molde, reserva.
            Paso 2: Licúa el resto de los ingredientes, vierte en el molde acaramelado, cubre con papel de aluminio y lleva al horno precalentado 350° F por una hora o hasta que al introducir un palillo este salga limpio.
            Paso 3: Pasdo el tiempo retira del horno, deja refrescar, desmolda y sirve.
        """,
        """
        1) Aplicaciones de IA
        1a) IA en la Salud
        1a1) Diagnóstico Asistido por IA
        """,
        """
        1) Fundamentos de Inversión
        1a) Inversión en el Mercado de Valores
        1a1) ¿Cómo puedo empezar a invertir en acciones y bonos siendo principiante?
        """
    ]

    # Validar si el id proporcionado está dentro del rango del arreglo
    if 0 <= subject_id < len(subjects):
        return subjects[subject_id]
    else:
        return "ID inválido"


def generate_hmac_storyblocks(secret, expires, resource):
    """
    Genera el HMAC para la autenticación de la API de Storyblocks.

    :param secret: Clave secreta de la API.
    :param expires: Tiempo de expiración en segundos desde la época Unix.
    :param resource: Recurso solicitado.
    :return: HMAC en formato hexadecimal.
    """

    key = f"{secret}{expires}"
    message = resource.encode()
    signature = hmac.new(key.encode(), message, hashlib.sha256).hexdigest()

    return signature


def search_storyblocks_videos(api_key, secret_key, expires, user_id, project_id, keywords):
    """
    Realiza una búsqueda de videos en la API de Storyblocks.

    :param api_key: Clave pública de la API.
    :param secret_key: Clave secreta de la API.
    :param expires: Tiempo de expiración en segundos desde la época Unix.
    :param user_id: Identificador único del usuario.
    :param project_id: Identificador único del proyecto.
    :param keywords: Palabras clave para la búsqueda, separadas por coma.
    :return: Lista de URLs de los videos encontrados.
    """
    resource = "/api/v2/videos/search"
    hmac_signature = generate_hmac_storyblocks(secret_key, expires, resource)

    url = f"https://api.storyblocks.com{resource}"
    
    keywords_list = keywords.split(", ")
    
    for i in range(len(keywords_list), 0, -1):
        current_keywords = ", ".join(keywords_list[:i])
        params = {
            'APIKEY': api_key,
            'EXPIRES': expires,
            'HMAC': hmac_signature,
            'project_id': project_id,
            'user_id': user_id,
            'keywords': current_keywords,
            'content_type': 'footage',
            'quality': 'HD',
            'page': 1,
            'results_per_page': 20,
        }

        response = requests.get(url, params=params)
        video_results = response.json().get("results", [])

        print("===============================================================================================")
        # print("search_storyblocks_videos -> keywords:", current_keywords)
        # print("===============================================================================================")
        print("search_storyblocks_videos -> video_results:", len(video_results))
        print("===============================================================================================")

        if video_results:
            break

    # desired_height = 1280   #640
    background_videos_urls = []

    for video in video_results:
        preview_url = video["preview_urls"].get("_720p")
        if preview_url:
            background_videos_urls.append(preview_url)

    return background_videos_urls
    

def download_storyblocks_video(api_key, secret_key, expires, user_id, project_id, video_id):
    """
    Descarga un video de la API de Storyblocks utilizando el ID del video.

    :param api_key: Clave pública de la API.
    :param secret_key: Clave secreta de la API.
    :param expires: Tiempo de expiración en segundos desde la época Unix.
    :param user_id: Identificador único del usuario.
    :param project_id: Identificador único del proyecto.
    :param video_id: ID del video a descargar.
    """
    resource = f"/api/v2/videos/{video_id}/download"
    hmac_signature = generate_hmac_storyblocks(secret_key, expires, resource)

    url = f"https://api.storyblocks.com{resource}"
    params = {
        'APIKEY': api_key,
        'EXPIRES': expires,
        'HMAC': hmac_signature,
        'project_id': project_id,
        'user_id': user_id,
    }

    response = requests.get(url, params=params)
    print(response.text)


if __name__ == "__main__":
    # Marcar el inicio del tiempo de ejecución
    inicio = time.time()

    # subject = obtener_subject_por_id(3)

    parser = argparse.ArgumentParser(description="Script para pasar títulos por consola.")
    parser.add_argument("titulo", help="Introduce un título para el video.")
    parser.add_argument("musica", help="Introduce un tema para la música.")
    parser.add_argument("palabraclave", help="Introduce una palabra clave.")
    parser.add_argument("idioma", help="Introduce el idioma para el video.")
    parser.add_argument("orientacion", help="Introduce la orientación del video.")
    parser.add_argument("duracion", help="Introduce la duración del video.")
    args = parser.parse_args()

    print("\n======================== args:\n", args, "\n========================\n")

    main(args.titulo or subject, args.musica, args.palabraclave, args.idioma, args.orientacion, args.duracion)
    # main(titulo)
    
    # Marcar el fin del tiempo de ejecución
    fin = time.time()

    # Calcular el tiempo total de ejecución
    tiempo_ejecucion = fin - inicio

    print(f"El tiempo de ejecución del script fue de {tiempo_ejecucion} segundos o {tiempo_ejecucion / 60} minutos.")