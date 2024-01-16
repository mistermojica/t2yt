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


# from pydub import AudioSegment
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import moviepy.editor as mpe
import moviepy.video as mpv
import moviepy.audio as mpa
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

client = OpenAI()

# openai.api_key = OPENAI_API_KEY
client.api_key = OPENAI_API_KEY


def log(param):
    print("==========================================")
    print(param)
    print("==========================================")

# creds = Credentials.from_authorized_user_info(info='client_secret.json')

# Aquí va la implementación de GPT-4 para generar el guión
def generate_script(verse_text):
    # Generate a JSON file and act as an educational tutorial creator for YouTube, creating a script with as many parts as necessary that transform common questions such as "How to...?" in detailed and captivating explanations about [{verse_text}], with clear and consistent descriptions in each part, and enriched with an educational and engaging narrative to immerse the audience in learning.
    
    prompt = f"""
        Goal:

        Generate a JSON file and act as an educational video creator for YouTube Shorts, creating a script with as many parts as necessary that transform common questions such as "How to...?" in short and captivating explanations about [{verse_text}], with clear and consistent descriptions in each part, and enriched with an educational and engaging narrative to immerse the audience in learning.

        Identification of titles and subtitles:

        - Important Instruction: Each title or subtitle must be described in a detailed and coherent manner.

        - Name of the title: [Condensed description of the title, including steps, actions that the student must execute to learn about the topic.]
        - Name of the subtitle: [Condensed description of the subtitle, including steps, actions that the student must execute to learn about the topic.]
        - [Continue with other subtitles as necessary.]

        JSON structure:

        The JSON should contain a series of objects, each representing a different title of the tutorial, placed in a field called "script_video_ia".

        Each title object must include:

        - prompt_dalle: in English, develop a message for DALL·E that describes a specific title in detail and precision. It should be detailed enough so that GPT-4 can send it directly to DALL·E without any additional adjustments.

        - scene_dialog: A series of narrative entries, each corresponding to a different part of a title. These entries are delivered by a single narrator in a voice-over style, done with educational language that is easy for anyone to understand, essential to convey the story and context of each title. Each narrative entry must include:
        -- scene_part: A tag or identifier for the specific part of the title being narrated.
        -- narration: In Spanish, the actual narrative text spoken by the narrator, which must describe the title, steps, and actions in detail, in a style consistent with the overall approach of the tutorial.

        Consistency in the descriptions and definitions of titles and subtitles:

        - Ensure that the titles and subtitles are identical in each object of the tutorial, to the texts provided in the outline.
        - Avoid any distortion of information and be very precise and accurate, speaking with the language of a teacher educator.
        - Pay attention to the language of each part, the default language is Spanish for the indications and descriptions of the titles, and for the narrations of the subtitles.
    """

    # (c) Imagina una serie de ilustraciones para un libro de cuentos para niños que relata una historia bíblica. Cada imagen debe tener una coherencia visual con las demás, manteniendo el mismo estilo artístico y la misma apariencia para los personajes y escenarios a lo largo de toda la historia. Los personajes deben ser fácilmente reconocibles y mantener su identidad en cada imagen, con vestimentas y rasgos consistentes. Genera una descripción detallada de cada personaje y colócala en el campo 'personajes_acto', con el objetivo de preservar la coherencia visual entre las imágenes generadas con DALL-E.

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a useful virtual assistant for story telling about tutorials."},
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

        escena = f"""Create an image rendered in a vibrant and colorful three-dimensional style, inspired by the visual quality and atmosphere of 3D animated movies like 'Toy Story' and 'Shrek'. This image should appeal to a wide audience, with expressive characters and friendly environments that capture the essence of a lively animated world. The focus should be on creating a clear and cheerful presentation, conveying the story in a visually enchanting and easy-to-understand manner, without replicating specific characters from these movies and avoiding traditional clipart or cartoon styles, for a tutorial video using this elements:\n\n
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
    language="es-US"
    voice="Miguel"

    polly_client = boto3.Session(profile_name='doccumi', region_name="us-west-2").client("polly")
    response = polly_client.synthesize_speech(
        OutputFormat="mp3",
        Text=f'<speak><prosody rate="90%">{text}</prosody></speak>',
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
        model="tts-1",
        voice="nova",
        input=text
    )

    response.stream_to_file(output_filename)

    # return audio


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
        print(final_clip)
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
def create_video_with_background_video(background_videos, audio_files, background_music, output_filename):
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

    video = mpe.concatenate_videoclips([video] * repetitions)
    video = video.subclip(0, audio_duration)

    # Establecer el audio del video
    video = video.set_audio(final_audio)

    # Agregar efectos de fundido en entrada y salida
    video = add_fade_in_out_effect(video, 2)

    # Guardar el video resultante
    video.write_videofile(output_filename, codec='libx264', audio_codec='libmp3lame')

    # Eliminar archivos temporales de video
    for filename in video_filenames:
        os.remove(filename)



def add_fade_in_out_effect(video_file, fade_duration=2):
    fadein = mpv.fx.all.fadein(video_file, fade_duration)    
    fadeout = mpv.fx.all.fadeout(fadein, fade_duration)
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


# Función principal
def main(title):
    # Generar guión
    # translate_client = translate.Client()

    feeling = """
        ¿Cómo hacer Arroz Blanco?

        Ingredientes:
            - 1 Libra Arroz Largo
            - 2 1/2 Tazas Agua
            - 1/2 Cucharada grande Sal
            - 1 Cucharada grande Aceite De Girasol

        Pasos para la preparación:
            - Paso 1: Lleve al fuego un caldero de fondo grueso con el agua y la sal, cuando rompa el hervor, añade el arroz, cocina a fuego medio hasta que el arroz absorba toda el agua, tapa y cocina a fuego bajo por 20 minutos aproximadamente.
            - Paso 2: Pasado el tiempo, vierte el aceite, deja cocinar por tres minutos más, retira del fuego y sirve.
    """

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
    print('# título español:', feeling or title or titulo)

    # script = generate_script(feeling or title or titulo)
    print("============================== INICIO GUION ==================================")
    # print(script)
    print("============================== FINAL GUION ===================================")
    # images = generate_images(script)
    print("============================== INICIO IMAGENES ===============================")
    # print(images)
    print("============================== FINAL IMAGENES ================================")
    # Usar la función para obtener el texto generado
    script = """
{
  "script_video_ia": [
    {
      "title": "Introducción al Arroz Blanco Perfecto",
      "prompt_dalle": "Create an image of a bowl of fluffy white rice with a spoon in it, steam rising, placed on a wooden table with raw rice grains and a pot of boiling water in the background.",
      "scene_dialog": [
        {
          "scene_part": "Introducción",
          "narration": "Bienvenidos, amantes de la cocina, hoy vamos a dominar el arte de hacer arroz blanco, un básico que acompaña a incontables platillos. ¿Listos para convertir un puñado de granos en la estrella de la mesa? ¡Empecemos!"
        }
      ]
    },
    {
      "title": "Preparando los Ingredientes",
      "prompt_dalle": "Show an image of one pound of long grain rice, two and a half cups of water, half a tablespoon of salt, and a tablespoon of sunflower oil measured and arranged neatly on a kitchen counter.",
      "scene_dialog": [
        {
          "scene_part": "Ingredientes",
          "narration": "Para nuestro arroz blanco necesitaremos: 1 libra de arroz largo, 2 1/2 tazas de agua, 1/2 cucharada grande de sal y 1 cucharada grande de aceite de girasol. Asegúrate de tenerlos todos a mano para facilitar el proceso."
        }
      ]
    },
    {
      "title": "Cocinando el Arroz",
      "prompt_dalle": "Illustrate a thick-bottomed pot on the stove with water boiling and salt being added, with a bag of long-grain rice on the side ready to be poured in.",
      "scene_dialog": [
        {
          "scene_part": "Paso1",
          "narration": "Paso 1: Coloca un caldero de fondo grueso al fuego con el agua y la sal. Espera a que hierva para incorporar el arroz. Cocínalo a fuego medio, sin tapar, hasta que absorba toda el agua. La paciencia es clave aquí, así que no te apresures."
        }
      ]
    },
    {
      "title": "El Toque Final",
      "prompt_dalle": "Visualize a pot of cooked rice on a stove with a drizzle of sunflower oil being added, a kitchen timer showing 20 minutes, and a spoon ready to fluff the rice.",
      "scene_dialog": [
        {
          "scene_part": "Paso2",
          "narration": "Paso 2: Cuando el arroz haya absorbido el agua, es momento de tapar y bajar el fuego. Cocina por 20 minutos para que se esponje. Después, añade el aceite de girasol y deja que cocine tres minutos más. ¡Estamos casi listos para el gran final!"
        }
      ]
    },
    {
      "title": "Servir y Disfrutar",
      "prompt_dalle": "Depict a fluffy, steaming bowl of white rice being served onto a plate, with a garnish of parsley on top for a touch of color, suggesting it's ready to be enjoyed.",
      "scene_dialog": [
        {
          "scene_part": "Finalización",
          "narration": "Retira el arroz del fuego y déjalo reposar unos minutos. Luego, con un tenedor, remuévelo suavemente para que se suelte. Sirve en tu plato favorito y decóralo a tu gusto. ¡Tu arroz blanco está listo para deleitar!"
        }
      ]
    }
  ]
}
    """
    generated_text = extract_narrations(script)

    # print('# Generar guión:', script["generated_text"])
    # print('# Generar sentimiento:', script["feeling_value"])

    # Convertir guión en audio
    audio_files = []
    for i, segment in enumerate(generated_text.split("\n\n")):
        output_filename = f"./audios/audio_{i}.mp3"
        print("output_filename", output_filename)
        # synthesize_speech(segment, output_filename)
        text_to_speech_polly(segment, output_filename)
        audio_files.append(output_filename)

    print('# Convertir guión en audio.')
    # print(output_filename)

    # feeling = translate_client.translate(script["feeling_value"], target_language='en')['translatedText']
    
    script_keywords = "cook or rice or chef"

    # Buscar video relacionado
    # adobe_stock_videos = search_adobe_stock_video(script_keywords)
    # print("adobe_stock_videos:", adobe_stock_videos)
    video_results = search_pexels_video(script_keywords) #title
    print('# de videos encontrados:', len(video_results))
    # print(video_results[0]["video_files"])
    print(video_results)

    # Si se encuentra un video relacionado, descargarlo
    # if video_results:
    #     video_url = video_results[0]["video_files"][0]["link"]
    #     download_video(video_url, "background_video.mp4")
    # else:
    #     print("No se encontró ningún video relacionado.")
    #     return

    # print('# Si se encuentra un video relacionado, descargarlo')

    background_videos_urls = []
    for video_url in video_results:
        background_videos_urls.append(video_url)
        print(f"======= video_url: {video_url} =======")

    # background_videos_urls = []
    # num_videos_to_take = 3
    # for i in range(min(num_videos_to_take, len(video_results))):
    #     video_url = video_results[0]["video_files"][i]['link']
    #     background_videos_urls.append(video_url)

    # print(background_videos_urls)

    # Crear video con el video de fondo y audio
    video_filename = f"./videos/{titulo}_{tiempo}.mp4"
    background_music = find_file_by_keyword("./music/", "inspiracional")
    print(f"background_music: {background_music}")
    create_video_with_background_video(background_videos_urls, audio_files, background_music, video_filename)

    print('# Crear video con el video de fondo y audio')
    print(video_filename)


    # # Subir video a YouTube
    # youtube = get_authenticated_service()

    # print('Autenticando usuario para subir video a YouTube')
    # print(youtube)


    # response = upload_video(youtube, video_filename, title, script)
    # print(f"Video subido con éxito: {response['id']}")

    # print(response)


if __name__ == "__main__":
    titulo = "Best Motivational Morning Speech"
    parser = argparse.ArgumentParser(description="Script para pasar títulos por consola.")
    parser.add_argument("titulo", help="Introduce un título para el video.")
    args = parser.parse_args()

    main(args.titulo or titulo)
    # main(titulo)