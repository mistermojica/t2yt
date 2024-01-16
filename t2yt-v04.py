import os
import io
import openai
import requests
import argparse
import subprocess
import boto3
import random
import json
import numpy as np

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

openai.api_key = OPENAI_API_KEY

# creds = Credentials.from_authorized_user_info(info='client_secret.json')
# print(creds)

# OpenAI GPT-4
# Aquí va la implementación de GPT-4 para generar el guión
def generate_script(frase_central):
    # prompt = f"Genera un texto breve, coherente y persuasivo para un video corto basado en el título y que dure un minuto o menos, que sea un solo texto corrido, en español, en primera persona, no te presentes, no incluyas las palabras 'discurso', 'motivadora', 'charla'. La frase central es: {title}\n\nGuión:"
    # prompt = f"Genera un texto breve, coherente y persuasivo para un video corto basado en la frase central. Que dure aproximadamente un minuto. Que sea un solo texto corrido. En español. En primera persona. No te presentes. No incluyas las palabras 'discurso', 'motivadora', 'charla'. Evalúa el sentimiento de la frase central utilizando el parámetro '__SENTIMETRIA__:'. La frase central es: {frase_central}\n\nTexto:"
    # prompt = f'Genera un texto breve, coherente y persuasivo para un video corto en español basado en la frase central "{frase_central}". El texto debe durar aproximadamente un minuto y ser un solo párrafo a manera de consejo. No incluyas las palabras o frases "{frase_central}", "discurso", "motivadora", "charla" o "frase central". No incluyas la frase central en el texto. Al final del texto, evalúa la frase central y resúmela en una sola palabra traducida en inglés utilizando el parámetro CDKCENTRO\n\nTexto:\n\nCDKCENTRO:'
    # prompt = f'Genera un guión breve, coherente y persuasivo para un video de un minuto en español basado en esta idea principal "{frase_central}". El guión debe presentarse como un único párrafo en forma de consejo. Evita utilizar palabras o expresiones como "{frase_central}", "discurso", "motivadora", "charla" o "idea principal". No incluyas la idea principal "{frase_central}" directamente en el guión. Al concluir el guión, evalúa la idea principal y resume su esencia en una sola palabra, utilizando el parámetro "CDKTEXTO".\n\nTexto:\n\CDKTEXTO:'
    # prompt = f'Por favor, genera un guión breve y persuasivo para un video corto en español. El video se centrará en la idea de "{frase_central}". Por favor, evita utilizar las palabras "{frase_central}", "discurso", "motivadora", "charla" o "idea principal" en el guión. El guión debe durar aproximadamente un minuto y presentarse como un único párrafo en forma de consejo. Al final del guión, evalúa la idea de "{frase_central}" y resume su esencia en una sola palabra utilizando el parámetro "CDKCENTRO". Por favor, incluye la palabra que resuma su esencia en el parámetro "CDKCENTRO" al final del texto.\n\nGuión:\n\nCDKCENTRO:'
    # prompt = f'Please generate a short and persuasive script for a short video in Spanish. The video will focus on the idea of "{frase_central}". Please avoid using the words "{frase_central}", "speech", "motivational", "chat", or "main idea" in the script. The script should be approximately one minute long and presented as a single paragraph in the form of advice. At the end of the script, it evaluates the idea of "{frase_central}" and summarizes its essence in a single word using the "CDKCENTRO" parameter. Please include the word that sums up your essence in the "CDKCENTRO" parameter at the end of the text.\n\nScript:\n\nCDKCENTRO:'
    prompt = f'Genera un texto extenso, coherente, lenguaje abundante y persuasivo para un video corto en español basado en la frase central "{frase_central}". No repitas una misma frase o un mismo patrón. No incluyas las palabras o frases "{frase_central}", "discurso", "motivadora", "charla" o "frase central". No incluyas la frase central en el texto. El resultado final debes retornarlo en formato JSON. El guión colócalo en un parámetro llamado CDKTEXTO. Y valúa la frase central y resúmela en una sola palabra utilizando el parámetro CDKCENTRO.'

    print('\n\n', prompt, '\n\n')

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.3,
    )

    # script = response.choices[0].text.strip()

    print('\n\n', response, '\n\n')

    generated_text = response.choices[0].text.strip()

    print('\ngenerated_text:\n', generated_text, '\n\n')

    response_object = json.loads(generated_text)

    # feeling_start = generated_text.find("CDKCENTRO:") + len("CDKCENTRO:")

    # if feeling_start != -1:
    #     feeling_end = generated_text.find("\n", feeling_start)
    #     feeling_value = generated_text[feeling_start:feeling_end].strip()
    #     generated_text = generated_text[:feeling_start - len("CDKCENTRO:")] + generated_text[feeling_end:]
    # else:
    #     feeling_value = "No encontrado"

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

    polly_client = boto3.Session(profile_name='cdkpolly', region_name="us-west-2").client("polly")
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

    # return audio


# Pexels API
# Aquí va la implementación para buscar videos en Pexels
def search_pexels_video(query):
    url = f"https://api.pexels.com/v1/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        'query': query,
        'per_page': 5,
        'orientation': 'portrait',
        'order_by':'popular'
    }

    response = requests.get(url, headers=headers, params=params)
    video_results = response.json()["videos"]

    # print("===================== video_results =====================")
    # print(video_results)
    # print("===================== video_results =====================")

    desired_width = 360
    desired_height = 640

    background_videos_urls = []

    random.shuffle(video_results)

    for video in video_results:
        for video_file in video["video_files"]:
            video_width = video_file["width"]
            video_height = video_file["height"]
            
            if video_width == desired_width and video_height == desired_height:
            # if video_height == desired_height:
                video_url = video_file["link"]
                background_videos_urls.append(video_url)
                # print(video_url)
                break

    return background_videos_urls

# Aquí va la implementación para descargar videos
def download_video(url, output_filename):
    response = requests.get(url, stream=True)

    with open(output_filename, "wb") as output_file:
        for chunk in response.iter_content(chunk_size=8192):
            output_file.write(chunk)


def resize_video(input_file, output_file, width, height):
    # Open video file
    # clip = mpe.VideoFileClip(input_file)

    # # Resize video while keeping aspect ratio
    # clip_resized = clip.resize(height=(height if height is not None else clip.size[1] * width // clip.size[0]), 
    #                           width=(width if width is not None else clip.size[0] * height // clip.size[1]))

    # # Pad video to desired dimensions
    # clip_padded = clip_resized.pad(width, height, (width - clip_resized.w) // 2, (height - clip_resized.h) // 2)

    # # Write output file
    # clip_padded.write_videofile(output_file)

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
        print(resized_clip)
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
        input_filename = f'./videos/background_video_{i}.mp4'
        download_video(url, input_filename)
        video_filenames.append(input_filename)

    video_clips = []
    for filename in video_filenames:
        clip = mpe.VideoFileClip(filename)
        clip_duration = clip.duration
        num_clips = int(clip_duration / 5) + 1  # dividir el video en fragmentos de 5 segundos
        clips = [clip.subclip(i*5, (i+1)*5) for i in range(num_clips)]
        video_clips.append(clips)

    # Consolidar los fragmentos del video
    final_clips = []
    for i in range(num_clips):
        for j in range(len(video_clips)):
            if i < len(video_clips[j]):
                final_clips.append(video_clips[j][i])

    # Concatenar los clips de video
    video = mpe.concatenate_videoclips(final_clips)

    # Cargar y combinar archivos de audio
    voice_audio = mpe.CompositeAudioClip([mpe.AudioFileClip(f) for f in audio_files])
    music_audio = mpe.AudioFileClip(background_music).volumex(0.25)
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


def add_fade_in_out_audio(audio_file, fade_duration=2):
    fadein = mpa.fx.all.audio_fadein(audio_file, fade_duration)
    fadeout = mpa.fx.all.audio_fadeout(fadein, fade_duration)
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

# Función principal
def main(title):
    # Generar guión
    translate_client = translate.Client()

    titulo = translate_client.translate(title, target_language='es')['translatedText']
    print('# título español:', titulo)

    script = generate_script(titulo)

    # print(script)
    
    # print('# Generar guión:', script["generated_text"])
    # print('# Generar sentimiento:', script["feeling_value"])

    # Convertir guión en audio
    audio_files = []
    for i, segment in enumerate(script["generated_text"].split("\n\n")):
        output_filename = f"./audios/audio_{i}.mp3"
        # synthesize_speech(segment, output_filename)
        text_to_speech_polly(segment, output_filename)
        audio_files.append(output_filename)

    print('# Convertir guión en audio')
    # print(output_filename)

    feeling = translate_client.translate(script["feeling_value"], target_language='en')['translatedText']
    print('# sentimiento inglés:', feeling)

    # Buscar video relacionado
    video_results = search_pexels_video(feeling) #title
    print('# de videos encontrados:', len(video_results))
    # print(video_results[0]["video_files"])
    # print(video_results)

    # # Si se encuentra un video relacionado, descargarlo
    # if video_results:
    #     video_url = video_results[0]["video_files"][0]["link"]
    #     download_video(video_url, "background_video.mp4")
    # else:
    #     print("No se encontró ningún video relacionado.")
    #     return

    print('# Si se encuentra un video relacionado, descargarlo')

    background_videos_urls = []
    for video_url in video_results:
        background_videos_urls.append(video_url)
        # print(f"======= video_url: {video_url} =======")

    # background_videos_urls = []
    # num_videos_to_take = 3
    # for i in range(min(num_videos_to_take, len(video_results))):
    #     video_url = video_results[0]["video_files"][i]['link']
    #     background_videos_urls.append(video_url)

    # print(background_videos_urls)

    # Crear video con el video de fondo y audio
    video_filename = f"./videos/final_video_{tiempo}.mp4"
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
