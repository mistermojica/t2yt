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
from base64 import b64decode
from PIL import Image, ImageDraw, ImageFont
import textwrap

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

dt = datetime.now()
tiempo = int(datetime.timestamp(dt))

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
except Exception as err:
    print(err)


# Configurar credenciales y claves API
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client_secret.json"
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
ADOBE_STOCK_API_KEY = os.environ.get("ADOBE_STOCK_API_KEY", "")
ADOBE_STOCK_X_PRODUCT = os.environ.get("ADOBE_STOCK_X_PRODUCT", "")
ADOBE_ACCESS_CLIENT_ID = os.environ.get("ADOBE_ACCESS_CLIENT_ID", "")
ADOBE_ACCESS_CLIENT_SECRET = os.environ.get("ADOBE_ACCESS_CLIENT_SECRET", "")
CONTADOR_ESCENAS = 0

client = OpenAI()

# openai.api_key = OPENAI_API_KEY
client.api_key = OPENAI_API_KEY


def log(param):
    print("==========================================")
    print(param)
    print("==========================================")

# creds = Credentials.from_authorized_user_info(info='client_secret.json')

# Aquí va la implementación de GPT-4 para generar el guión
def generate_script(outline):
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


    prompt = f"""
        Objetivo:

        Actua como un creador de videos educativos para YouTube Shorts, creando un guión que transformen expresiones en contenidos cortos y cautivadores sobre este tema principal ["{outline}"], con descripciones claras y consistentes en cada parte, y enriquecidas con una narrativa educativa y atractiva para sumergir a la audiencia en el aprendizaje. El guion también debe incorporar los siguientes elementos sin mencionarlos literalmente en la narración, que se usan para el éxito viral en YouTube Shorts:

        Comenzar con algo que sirva de gancho, que capte inmediatamente la atención. Ejemplos: "¿La IA compone una canción en 1 minuto: éxito o fracaso?", "Chatbot de IA organiza mi agenda: ¿Mejor que un asistente?", "Desafío de IA: ¿Quién edita fotos mejor, humano o máquina?", "IA para ahorrar: ¿Realmente reduce mis gastos mensuales?". (No mencionar este elemento literalmente en la narración)
        Limitar la duración del guión a 54 segundos o menos, asegurando que el contenido sea rápido y fácil de consumir.
        Abordar temas de tendencia, como eventos actuales, desafíos virales, memes populares o temas de gran interés. (No mencionar este elemento literalmente en la narración)
        Incluir un giro o evento inesperado que genere emoción o sorpresa (sin hacer mención tácitamente de este punto), como un cambio abrupto en la narrativa o una reacción poco común. (No mencionar este elemento literalmente en la narración)
        Concluir con un mensaje directo para la acción del espectador, como compartir, dar me gusta, comentar o participar en una actividad específica, promoviendo así la participación y difusión del video. (No mencionar este elemento literalmente en la narración)

        Identificación de títulos y subtítulos:

        Instrucción Importante: Cada título o subtítulo debe ser descrito de manera detallada y coherente.

        - Nombre del título: [Descripción condensada del título, incluyendo pasos, acciones que el estudiante debe ejecutar para aprender sobre el tema.]
        - Nombre del subtítulo: [Descripción condensada del subtítulo, incluyendo pasos, acciones que el estudiante debe ejecutar para aprender sobre el tema.]
        - [Continuar con otros subtítulos según sea necesario.]

        Estructura JSON del resultado final:

        El JSON debe contener un objeto en un arreglo de un elemento, representando el título del video, colocado en un campo llamado "script_video_ia".

        Cada objeto del título debe incluir:

        scene_dialog: Un solo arreglo de entradas narrativas, correspondiente a un título. El arreglo de entradas narrativas debe incluir elementos con esta estructura:
        -- scene_part: Una etiqueta o identificador para la parte específica del título que se está narrando.
        -- narration: En español latino, el texto narrativo real hablado por el narrador, que debe describir el título, los pasos y las acciones en detalle, en un estilo consistente con el enfoque general del video.
        -- prompt_dalle: en inglés, desarrollar un mensaje para DALL·E que describa la "narración" con detalle y precisión. Debe ser lo suficientemente detallado para que GPT-4 pueda enviarlo directamente a DALL·E sin ningún ajuste adicional.
        -- video_keyword: en inglés, especificar 2 palabras claves que representen el tema principal ["{outline}"] y el campo ["narration"]. Repite la primera palabra clave en todos los elementos de "scene_dialog" y agrega una adicional. Es muy importante que sean 2 palabras claves en idioma inglés.
        
        Consistencia en las descripciones y definiciones de título y subtítulo:

        Asegurar que el título y subtítulo sean idénticos en cada objeto del video, al texto proporcionado en el tema principal.
        Evitar cualquier distorsión de la información y ser muy preciso y exacto, hablando con el lenguaje de un educador.
        Prestar atención al idioma de cada parte, el idioma predeterminado es el español para las indicaciones y descripciones de los títulos, y para las narraciones de los subtítulos.
    """

    # (c) Imagina una serie de ilustraciones para un libro de cuentos para niños que relata una historia bíblica. Cada imagen debe tener una coherencia visual con las demás, manteniendo el mismo estilo artístico y la misma apariencia para los personajes y escenarios a lo largo de toda la historia. Los personajes deben ser fácilmente reconocibles y mantener su identidad en cada imagen, con vestimentas y rasgos consistentes. Genera una descripción detallada de cada personaje y colócala en el campo 'personajes_acto', con el objetivo de preservar la coherencia visual entre las imágenes generadas con DALL-E.

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a useful virtual assistant for story telling about YouTube Shorts."},
            {"role": "user", "content": prompt}
        ],
        # model="gpt-3.5-turbo-16k",
        model="gpt-4-1106-preview",
        # max_tokens=1000,
        temperature=0.5,
        response_format={"type": "json_object"}
    )

    respuesta = response.choices[0].message.content
    
    print(respuesta)
    
    return respuesta


def generate_keywords(outline):

    prompt = f"""
        Act as an expert finding keywords in outlines like this: [{outline}]. Then generate the main keyword in English that help to find videos related to the outline.
    """

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a useful virtual assistant for story telling about YouTube Shorts. Just return the main keywords divided by spaces."},
            {"role": "user", "content": prompt}
        ],
        # model="gpt-3.5-turbo-16k",
        model="gpt-4-1106-preview",
        # max_tokens=1000,
        temperature=0.5,
        # response_format={"type": "json_object"}
    )

    respuesta = response.choices[0].message.content
    
    print("KEYWORDS:", respuesta)
    
    return respuesta


def generate_images(script):
   
    # print(script)
    script_json = json.loads(script)

    acts = script_json["script_video_ia"]

    image_paths = []

    previous_image_prompt = ""

    carpeta = int(time.time())

    for act in acts:
        # personajes = "\n".join([f"{p['name']}: {p['description']}" for p in act['characters']])

        # escena = f"""Crea una imagen en un estilo de animación vibrante y detallado, con estilo Pixar a partir de estos elementos:\n\n
        # [ESCENA: {act['prompt_dalle'].strip()}]\n\n
        # [PERSONAJES: {personajes.strip()}]\n\n
        # """
        # DO NOT add any detail to the prompt, just use it AS-IS: 

        print('ACTS:', acts)

        escena = f"""Create an image rendered in a vibrant and colorful three-dimensional style, inspired by the visual quality and atmosphere of 3D animated movies like 'Toy Story' and 'Shrek'. This image should appeal to a wide audience, with expressive characters and friendly environments that capture the essence of a lively animated world. The focus should be on creating a clear and cheerful presentation, conveying the story in a visually enchanting and easy-to-understand manner, without replicating specific characters from these movies and avoiding traditional clipart or cartoon styles, for a YouTube Short video using this elements:\n\n
        [STEP: {act['prompt_dalle'].strip()}]\n\n
        [IMPORTANT: Always follow the Prompt Guidelines. Avoid words or concepts that go against terms of service. Do not infringe on anyone's copyright; do not use suggestive or explicit imagery in your prompts. Do not emphasize or imply any elements that would not be considered G-rated.]\r\n
        """
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

            print(previous_image_prompt)

            # print(image_url)
            # print(image_data)
            
            # Suponiendo que la respuesta incluye la imagen generada en el campo 'data'
            # image_data = response.json()['data']
            if not os.path.exists(f"./imagenes/generadas/{carpeta}"):
                os.mkdir(f"./imagenes/generadas/{carpeta}")

            image_path = f"./imagenes/generadas/{carpeta}/{acts.index(act)}.png"

            # Aquí deberías escribir la imagen en el sistema de archivos
            with open(image_path, 'wb') as f:
                # f.write(requests.get(image_url).content)
                f.write(b64decode(image_data))
            
            image_paths.append(image_path)
        else:
            log(f"Error generating image", response.text)
            image_paths.append(None)

    return image_paths


def generate_image_prompt(prompt, carpeta):
    global CONTADOR_ESCENAS

    print('PROMPT:', prompt)

    escena = f"""Create an image rendered in a vibrant and colorful three-dimensional style, inspired by the visual quality and atmosphere of 3D animated movies like 'Toy Story' and 'Shrek'. This image should appeal to a wide audience, with expressive characters and friendly environments that capture the essence of a lively animated world. The focus should be on creating a clear and cheerful presentation, conveying the story in a visually enchanting and easy-to-understand manner, without replicating specific characters from these movies and avoiding traditional clipart or cartoon styles, for a YouTube Shorts video using this elements:\n\n
    [STEP: {prompt}]\n\n
    [IMPORTANT: Always follow the Prompt Guidelines. Avoid words or concepts that go against terms of service. Do not infringe on anyone's copyright; do not use suggestive or explicit imagery in your prompts. Do not emphasize or imply any elements that would not be considered G-rated.]\r\n
    """
    # [BIBLE CHARACTERS: {personajes.strip()}]. Remember to use the Bible characters description exactly as defined in the DALL·E prompt!\n\n

    # if (previous_image_prompt != ""):
    #     continuidad = f"""[FOR VISUAL CONTINUITY: To ensure visual continuity and consistent style with the previous image, I am including the original prompt used in the previous image generation below. This prompt, delimited by three backticks (```), will serve as a reference for DALLE 3, facilitating the creation of a new image that maintains stylistic and visual similarities with the previous one. ```{previous_image_prompt}```]"""
    # else:
    #     continuidad = ""

    # prompt = escena # + continuidad
    log(escena)

    response = client.images.generate(
        model="dall-e-3",
        prompt=escena,
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

        print(previous_image_prompt)

        # print(image_url)
        # print(image_data)
        
        # Suponiendo que la respuesta incluye la imagen generada en el campo 'data'
        # image_data = response.json()['data']
        if not os.path.exists(f"./imagenes/generadas/{carpeta}"):
            os.mkdir(f"./imagenes/generadas/{carpeta}")

        image_path = f"./imagenes/generadas/{carpeta}/{CONTADOR_ESCENAS}.png"

        # Aquí deberías escribir la imagen en el sistema de archivos
        with open(image_path, 'wb') as f:
            # f.write(requests.get(image_url).content)
            f.write(b64decode(image_data))
        
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
        # model="gpt-3.5-turbo",
        model="gpt-4-1106-preview",
        temperature=0.5,
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


def text_to_speech_polly(text, output_filename):
    language="es-US" #es-MX
    voice="Miguel" #es-MX: Mia, Andrés | es-US: Miguel, Lupe, Penelope 

    polly_client = boto3.Session(profile_name='doccumi', region_name="us-west-2").client("polly") #doccumi or cdkpolly
    response = polly_client.synthesize_speech(
        # Engine='neural',
        OutputFormat="mp3",
        Text=f'<speak><prosody rate="90%">{text}</prosody></speak>', #<amazon:domain name="news"></amazon:domain>
        # Text=f'<speak><prosody rate="90%"><amazon:domain name="news">{text}</amazon:domain></prosody></speak>', #<amazon:domain name="news"></amazon:domain>
        TextType="ssml", #text
        VoiceId=voice,
        LanguageCode=language,
    )
    
    audio_data = response["AudioStream"].read()
    # audio = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")

    with open(output_filename, "wb") as out:
        out.write(audio_data)

    # speech_file_path =  Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
        model="tts-1-hd", #tts-1
        voice="nova",
        input=text
    )

    # response.stream_to_file(output_filename)

    # audio = response.read()

    return output_filename # audio_data or audio or output_filename


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
def search_pexels_video(query):
    url = f"https://api.pexels.com/v1/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        'query': query,
        'per_page': 20,
        'orientation': 'portrait', #'landscape',
        'order_by':'popular'
    }

    response = requests.get(url, headers=headers, params=params)
    video_results = response.json()["videos"]

    desired_width =  720    #360
    desired_height = 1280   #640

    background_videos_urls = []

    random.shuffle(video_results)

    for video in video_results:
        for video_file in video["video_files"]:
            video_width = video_file["width"]
            video_height = video_file["height"]
            
            # if video_width == desired_width and video_height == desired_height:
            if video_height == desired_height:
            # if desired_width == desired_width:
                video_url = video_file["link"]
                # print(f"video_url: {video_url}")
                background_videos_urls.append(video_url)
                # print(video_url)
                break
            # else:
                # print(f"link: {video_file}")

    return background_videos_urls


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
    video_filenames = []
    for i, url in enumerate(background_videos):
        input_filename = f'./resources/background_video_{i}.mp4'
        download_video(url, input_filename)
        video_filenames.append(input_filename)

    # Cargar y recortar fragmentos de 5 segundos al azar de cada video de fondo
    video_clips = []
    for f in video_filenames:
        clip = mpe.VideoFileClip(f)
        clip_duration = clip.duration
        start_times = [random.uniform(0, clip_duration - 5) for i in range(int(clip_duration / 5))]
        start_times.sort()
        clips = [clip.subclip(t, t+5) for t in start_times]
        video_clips.append(clips)
        print(f'filename: {f} | clip_duration: {clip_duration} | num_clips: {len(clips)}')

    # Consolidar los fragmentos del video
    final_clips = []
    max_num_clips = max([len(clips) for clips in video_clips])
    for i in range(max_num_clips):
        for j in range(len(video_clips)):
            if i < len(video_clips[j]):
                clip = video_clips[j][i]
                if clip.duration < 5:
                    # Si el fragmento es menor a 5 segundos, se suma al siguiente fragmento
                    if i < max_num_clips - 1 and len(video_clips[j]) > i + 1:
                        next_clip = video_clips[j][i+1]
                        if next_clip.duration >= 5:
                            next_clip = next_clip.subclip(0, 5 - clip.duration)
                            clip = mpe.concatenate_videoclips([clip, next_clip])
                            video_clips[j][i+1] = next_clip.subclip(5 - clip.duration)
                    else:
                        # Si es el último fragmento, se agrega tal cual
                        pass
                else:
                    # Si el fragmento es de 5 segundos, se agrega tal cual
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


def create_video_with_background_video(elementos_partes, titulo, output_filename, background_music):
    
    # print("elementos_partes:", elementos_partes)
    print("output_filename:", output_filename)
    print("background_music:", background_music)
    # return None

    elementos = {}

    # Recorrer el arreglo
    for elemento in elementos_partes:
        # Recorrer cada clave en el elemento
        for clave in elemento:
            # Si la clave no está en el diccionario, agregarla y crear una lista vacía
            # Añadir el valor correspondiente a la lista de esa clave
            elementos.setdefault(clave, []).append(elemento[clave])

    # Mostrar las listas generadas
    # for clave, lista in elementos.items():
        # print(f"{clave}: {lista}")

    # Descargar los videos de fondo
    # video_filenames = []
    # for i, url in enumerate(background_videos):
    #     input_filename = f'./resources/background_video_{i}.mp4'
    #     download_video(url, input_filename)
    #     video_filenames.append(input_filename)

    # Cargar y recortar fragmentos de 5 segundos al azar de cada video de fondo
    # video_clips = []
    # for f in video_filenames:
    #     clip = mpe.VideoFileClip(f)
    #     clip_duration = clip.duration
    #     start_times = [random.uniform(0, clip_duration - 5) for i in range(int(clip_duration / 5))]
    #     start_times.sort()
    #     clips = [clip.subclip(t, t+5) for t in start_times]
    #     video_clips.append(clips)
    #     print(f'filename: {f} | clip_duration: {clip_duration} | num_clips: {len(clips)}')

    # Consolidar los fragmentos del video
    # video_clips = elementos["clip"]
    # final_clips = []
    # max_num_clips = max([len(clips) for clips in video_clips])
    # for i in range(max_num_clips):
    #     for j in range(len(video_clips)):
    #         if i < len(video_clips[j]):
    #             clip = video_clips[j][i]
    #             if clip.duration < 5:
    #                 # Si el fragmento es menor a 5 segundos, se suma al siguiente fragmento
    #                 if i < max_num_clips - 1 and len(video_clips[j]) > i + 1:
    #                     next_clip = video_clips[j][i+1]
    #                     if next_clip.duration >= 5:
    #                         next_clip = next_clip.subclip(0, 5 - clip.duration)
    #                         clip = mpe.concatenate_videoclips([clip, next_clip])
    #                         video_clips[j][i+1] = next_clip.subclip(5 - clip.duration)
    #                 else:
    #                     # Si es el último fragmento, se agrega tal cual
    #                     pass
    #             else:
    #                 # Si el fragmento es de 5 segundos, se agrega tal cual
    #                 pass
    #             final_clips.append(clip)

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
            audio_file = elementos["audio"][index]
            audio_clip = AudioFileClip(audio_file)
            audio_duration_calculated = audio_clip.duration
            # Calcular el tiempo de despliegue de cada palabra
            tiempos_palabras = calcular_tiempo_por_palabra(text, audio_duration_calculated)  # Asumiendo que 'duracion_total' es la duración total del video en segundos

            for palabra, duracion in tiempos_palabras:
                # text_clip = TextClip(palabra, fontsize=50, color='white', size=video.size).set_duration(duracion).set_pos('center').set_start(current_time)

                text_clip = TextClip(
                    palabra,
                    # size=(200, 50),
                    font='Lane',
                    fontsize=40,
                    color='white',
                    method='caption',
                    align='center'
                ).set_duration(duracion).set_pos(('center', 'center')).set_start(current_time) #, size=video.size
                txt_size = text_clip.size
                # print("create_video_with_background_video -> txt_size:", txt_size)

                bg_size = (txt_size[0] + 10, txt_size[1] + 10)
                # print("create_video_with_background_video -> bg_size:", bg_size)

                bg_clip = ColorClip(size=bg_size, color=(0, 0, 0), duration=duracion).set_opacity(0.7).set_position(('center', 'center')).set_start(current_time)
                # bg_clip = ImageClip("solid-color.png", duration=duracion).set_opacity(0.5).set_position('center').set_start(current_time)
            
                # combined_clip = mpe.CompositeVideoClip([bg_clip, text_clip])
                # Crear un CompositeVideoClip para combinar ambos clips

                tamano_video = video.size
                altura_deseada = tamano_video[1] - (tamano_video[1] * 0.3)

                combined_clip = mpe.CompositeVideoClip([bg_clip.set_position("center"), text_clip], size=(300, 100))

                combined_clip = combined_clip.set_position(("center", altura_deseada))

                narration_clips.append(combined_clip)
                current_time += duracion


        print("create_video_with_background_video -> current_time:", current_time)

        # Añadir los TextClips al video

        thumbnail_filename = crear_thumbnail(titulo.replace(" ", "\n"), './backgrounds/background3.jpg', './fotos/omar1.png')

        # Convertir la imagen en un ImageClip
        thumbnail_clip = mpe.ImageClip(thumbnail_filename).set_duration(2)  # Duración de 5 segundos, ajusta según necesites

        # Crear una lista de clips con el thumbnail al principio
        clips = [thumbnail_clip.set_position("center")] + [video] + narration_clips

        video_all = mpe.CompositeVideoClip(clips)

    # Agregar efectos de fundido en entrada y salida
    video = add_fade_in_out_effect(video_all, 2)

    # Guardar el video resultante
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

    # credentials = service_account.Credentials.from_service_account_file(CLIENT_SECRET_FILE, scopes=SCOPES)
    # youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    # return youtube
    
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    print(flow)
    credentials = flow.run_local_server(port=0)
    print(credentials)
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

# Función para calcular el tiempo de despliegue de cada palabra
# def calcular_tiempo_por_palabra(texto, segundos):
#     palabras = texto.split()
#     velocidad_ppm = calcular_ppm(texto, segundos)
#     print("calcular_tiempo_por_palabra() -> velocidad_ppm:", velocidad_ppm)

#     tiempo_promedio_por_palabra = 60 / velocidad_ppm  # Tiempo en segundos
#     print("calcular_tiempo_por_palabra() -> tiempo_promedio_por_palabra:", tiempo_promedio_por_palabra)

#     tiempos = []

#     for palabra in palabras:
#         factor_proporcional = len(palabra) / len(texto.replace(" ", ""))
#         tiempo_palabra = tiempo_promedio_por_palabra * factor_proporcional * len(palabra)
#         tiempos.append((palabra, tiempo_palabra))

#     return tiempos

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


def procesar_scene(scene, carpeta):
    global CONTADOR_ESCENAS

    print("scene:", scene)
    output_filename = f"./audios/audio_{CONTADOR_ESCENAS}.mp3"
    single_text_with_space = " ".join(scene["video_keyword"])
    print("single_text_with_space:", single_text_with_space)
    videos = search_pexels_video(" ".join(scene["video_keyword"]))
    print("# de videos 1:", len(videos))
    if len(videos) == 0:
        videos = search_pexels_video(scene["video_keyword"][0])
        print("# de videos 2:", len(videos))
    audio = text_to_speech_polly(scene["narration"], output_filename)
    imagen = "" #generate_image_prompt(scene["prompt_dalle"], carpeta)
    duracion_audio = obtener_duracion_audio(output_filename)
    clip = generar_clips(videos, duracion_audio)

    return {
        "videos": videos,
        "audio": audio,
        "imagen": imagen,
        "clip": clip,
        "duracion_audio": duracion_audio,
        "narration": scene["narration"]
    }


def procesar_scene_local(scene, carpeta):
    global CONTADOR_ESCENAS

    elemento = {
        "videos": ['https://player.vimeo.com/external/529683387.hd.mp4?s=7865594f7abca027d0a2eaf1e4f26d737e9672b8&profile_id=174&oauth2_token_id=57447761', 'https://player.vimeo.com/external/476736541.hd.mp4?s=f05c357bb3f086d56f8198d10f01069afaf1684f&profile_id=174&oauth2_token_id=57447761', 'https://player.vimeo.com/external/464571830.hd.mp4?s=00768b2e0071f61084314b8f87b0e83704f2e6fa&profile_id=174&oauth2_token_id=57447761', 'https://player.vimeo.com/external/504060845.hd.mp4?s=e31c144264286b4f6134542cf70c4bc7ddf0af2f&profile_id=174&oauth2_token_id=57447761', 'https://player.vimeo.com/external/538990224.hd.mp4?s=e999af85e338179de6246cf5cfb992540685aa58&profile_id=174&oauth2_token_id=57447761', 'https://player.vimeo.com/external/504059190.hd.mp4?s=8fc35a255b6cd6a7662803d8287252c300df1bf7&profile_id=174&oauth2_token_id=57447761', 'https://player.vimeo.com/external/529103004.hd.mp4?s=b2c7621a8bb554d53015488dd8dd08954760c961&profile_id=174&oauth2_token_id=57447761', 'https://player.vimeo.com/external/452497809.hd.mp4?s=8770a9f582a38225403bf852571a5367cceea7c5&profile_id=174&oauth2_token_id=57447761', 'https://player.vimeo.com/external/511560121.hd.mp4?s=45fcf873f7095f83ebd37d8e2ac02c5e0ad1f56d&profile_id=174&oauth2_token_id=57447761', 'https://player.vimeo.com/external/539581584.hd.mp4?s=c91f35d633463b003f95ec5c9118818e1a0431dd&profile_id=174&oauth2_token_id=57447761', 'https://player.vimeo.com/external/455000650.hd.mp4?s=a7df539dc7bc743390d2f8f3641de41884de1ea6&profile_id=174&oauth2_token_id=57447761', 'https://player.vimeo.com/external/464188889.hd.mp4?s=d72927e7e30f0ad500839aa7dcfdd40c5cc78657&profile_id=174&oauth2_token_id=57447761', 'https://player.vimeo.com/external/511560122.hd.mp4?s=14a94706de465fb01a4dccf1df4d81af94bda725&profile_id=174&oauth2_token_id=57447761', 'https://player.vimeo.com/external/511560125.hd.mp4?s=22ea5373d09f11c46d7bbe09d8a68ca4634da921&profile_id=174&oauth2_token_id=57447761'],
        "audio": f'./audios/audio_{CONTADOR_ESCENAS}.mp3',
        "imagen": '',
        "clip": VideoFileClip(f'./clips/clip_{CONTADOR_ESCENAS}.mp4'),
        "duracion_audio": obtener_duracion_audio(f'./audios/audio_{CONTADOR_ESCENAS}.mp3'),
        "narration": scene["narration"]
    }

    return elemento


def generar_clips(videos, duracion_audio):
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
    font = ImageFont.truetype('./fonts/bebas_neue/BebasNeue-Regular.ttf', 110)  # Puedes cambiar la fuente y el tamaño
    draw.text((100, 175), textwrap.fill(titulo, width=15), (255, 255, 255), font=font, align='center')

    nombre_thumbnail = titulo.replace("\n", "_")
    filename = f'./thumbnails/{nombre_thumbnail}.jpg'
    imagen_final.save(filename)

    return filename


# Función principal
def main(outline, musica):
    global CONTADOR_ESCENAS

    # Generar guión
    # translate_client = translate.Client()

    # titulo = outline.split('\n')[1].strip().replace('¿', '').replace('?', '')
    titulo = outline

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

    script = generate_script(outline)
    # script = '{"script_video_ia":[{"scene_dialog":[{"scene_part":"Introducción","narration":"¿Te imaginas transformar hilo en arte para tu hogar? Hoy aprenderemos a hacer cojines y fundas de crochet.","prompt_dalle":"Create an image of a cozy living room with crochet cushions and covers on the sofa, showcasing a handmade, artistic atmosphere.","video_keyword":"Crochet Cushions and Covers"},{"scene_part":"Materiales Necesarios","narration":"Primero, selecciona tu hilo favorito y ganchillos de crochet adecuados para el tamaño.","prompt_dalle":"Display a variety of colorful yarns and different sizes of crochet hooks arranged neatly, ready for crafting.","video_keyword":"Crochet Materials"},{"scene_part":"Inicio del Proyecto","narration":"Comenzamos con un anillo mágico, base para cojines perfectos. ¡Es más fácil de lo que piensas!","prompt_dalle":"Illustrate hands forming a magic ring with crochet, indicating the beginning of a crochet cushion project.","video_keyword":"Magic Ring Crochet"},{"scene_part":"Desarrollo del Patrón","narration":"Sigue el patrón de puntos, crea formas y texturas únicas. Cada puntada acerca a un cojín con personalidad.","prompt_dalle":"Show a close-up of hands crocheting intricate patterns on a cushion cover, emphasizing the creation of unique shapes and textures.","video_keyword":"Crochet Patterns"},{"scene_part":"Cierre Sorpresa","narration":"Y cuando menos lo esperas, ¡zas! Cierras el último punto y... tienes una obra maestra en tus manos.","prompt_dalle":"Visualize the moment of finishing the last stitch on a crochet cushion cover, revealing a beautiful, completed masterpiece.","video_keyword":"Crochet Masterpiece"},{"scene_part":"Llamado a la Acción","narration":"Ahora es tu turno, elige tus colores y empieza a tejer. Comparte tus creaciones y ¡sorprende al mundo con tu talento!","prompt_dalle":"Create an inspiring image of a completed crochet cushion with an invitation to start crocheting, encouraging viewers to share their own creations.","video_keyword":"Crochet Call to Action"}]}]}'
    print("============================== INICIO GUION ==================================")
    print(script)
    print("============================== FINAL GUION ===================================")
    # keywords = generate_keywords(outline)
    print("============================== INICIO KEYWORDS ===============================")
    # print(keywords)
    print("============================== FINAL KEYWORDS ================================")
    # images = generate_images(script)
    print("============================== INICIO IMAGENES ===============================")
    # print(images)
    print("============================== FINAL IMAGENES ================================")


    # Usar la función para obtener el texto generado
    generated_text = extract_narrations(script)

    elementos_partes = []
    carpeta_elementos = int(time.time())

    json_data = json.loads(script)
    for script_ia in json_data['script_video_ia']:
        for dialog in script_ia["scene_dialog"]:
            CONTADOR_ESCENAS += 1
            elementos = procesar_scene(dialog, carpeta_elementos)
            elementos_partes.append(elementos)
            # print("elementos:", elementos)

    # print('# Generar guión:', script["generated_text"])
    # print('# Generar sentimiento:', script["feeling_value"])

    # # Convertir guión en audio
    # audio_files = []
    # for i, segment in enumerate(generated_text.split("\n\n")):
    #     output_filename = f"./audios/audio_{i}.mp3"
    #     print("output_filename", output_filename)
    #     # synthesize_speech(segment, output_filename)
    #     text_to_speech_polly(segment, output_filename)
    #     audio_files.append(output_filename)

    # print('# Convertir guión en audio.')
    # print(output_filename)

    # feeling = translate_client.translate(script["feeling_value"], target_language='en')['translatedText']
    
    # script_keywords = "cook or rice or chef"

    # Buscar video relacionado
    # adobe_stock_videos = search_adobe_stock_video(script_keywords)
    # print("adobe_stock_videos:", adobe_stock_videos)
    # video_results = search_pexels_video(keywords) #title
    # print('# de videos encontrados:', len(video_results))
    # print(video_results[0]["video_files"])
    # print(video_results)

    # Si se encuentra un video relacionado, descargarlo
    # if video_results:
    #     video_url = video_results[0]["video_files"][0]["link"]
    #     download_video(video_url, "background_video.mp4")
    # else:
    #     print("No se encontró ningún video relacionado.")
    #     return

    # print('# Si se encuentra un video relacionado, descargarlo')

    # background_videos_urls = []
    # for video_url in video_results:
    #     background_videos_urls.append(video_url)
    #     print(f"======= video_url: {video_url} =======")

    # background_videos_urls = []
    # num_videos_to_take = 3
    # for i in range(min(num_videos_to_take, len(video_results))):
    #     video_url = video_results[0]["video_files"][i]['link']
    #     background_videos_urls.append(video_url)

    # print(background_videos_urls)

    # Crear video con el video de fondo y audio
    video_filename = f"./videos/{titulo}_{tiempo}.mp4"
    background_music = find_file_by_keyword("./music/", musica)
    print(f"background_music: {background_music}")
    # create_video_with_background_video(images, background_videos_urls, audio_files, background_music, video_filename)
    create_video_with_background_video(elementos_partes, titulo, video_filename, background_music)

    print('# Crear video con el video de fondo y audio')
    print(video_filename)


    # # Subir video a YouTube
    # youtube = get_authenticated_service()

    # print('Autenticando usuario para subir video a YouTube')
    # print(youtube)


    # response = upload_video(youtube, video_filename, title, script)
    # print(f"Video subido con éxito: {response['id']}")

    # print(response)


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


if __name__ == "__main__":
    # Marcar el inicio del tiempo de ejecución
    inicio = time.time()

    subject = obtener_subject_por_id(3)

    parser = argparse.ArgumentParser(description="Script para pasar títulos por consola.")
    parser.add_argument("titulo", help="Introduce un título para el video.")
    parser.add_argument("musica", help="Introduce un tema para la música.")
    args = parser.parse_args()

    print(args)

    main(args.titulo or subject, args.musica)
    # main(titulo)
    
    # Marcar el fin del tiempo de ejecución
    fin = time.time()

    # Calcular el tiempo total de ejecución
    tiempo_ejecucion = fin - inicio

    print(f"El tiempo de ejecución del script fue de {tiempo_ejecucion} segundos o {tiempo_ejecucion / 60} minutos.")