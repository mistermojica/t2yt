import os
import openai
import requests
import argparse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.cloud import texttospeech
from moviepy.editor import mp
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

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
def generate_script(title):
    prompt = f"Genera un texto breve, coherente y persuasivo para un video Short de YouTube basado en el título y que dure un minuto, que sea un solo texto corrido, en español, en primera persona, no incluyas las palabras 'discurso', 'motivadora', 'charla': {title}\n\nGuión:"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7,
    )

    script = response.choices[0].text.strip()
    return script

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
        speaking_rate=0.66
    )

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    with open(output_filename, "wb") as out:
        out.write(response.audio_content)

# Pexels API
# Aquí va la implementación para buscar videos en Pexels
def search_pexels_video(query):
    url = f"https://api.pexels.com/v1/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        'query': query,
        'per_page': 1,
        'orientation': 'portrait'
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()["videos"]

# Aquí va la implementación para descargar videos
def download_video(url, output_filename):
    response = requests.get(url, stream=True)

    with open(output_filename, "wb") as output_file:
        for chunk in response.iter_content(chunk_size=8192):
            output_file.write(chunk)

# Crear video con video de fondo y audio
# Aquí va la implementación para combinar video de fondo y audio
def create_video_with_background_video(background_videos, audio_files, output_filename):
    # audio_clips = [AudioFileClip(audio_file) for audio_file in audio_files]
    # concatenated_audio = concatenate_audioclips(audio_clips)

    # background_video_clip = VideoFileClip(background_video)
    # background_video_with_audio = background_video_clip.set_audio(concatenated_audio)
    
    # background_video_with_audio.write_videofile(output_filename, codec='libx264', audio_codec='libmp3lame')

    # Descargar los videos de fondo
    video_filenames = []
    for i, url in enumerate(background_videos):
        filename = f'background_video_{i}.mp4'
        download_video(url, filename)
        video_filenames.append(filename)

    # Cargar y concatenar videos de fondo
    video_clips = [mp.VideoFileClip(f) for f in video_filenames]
    video = mp.concatenate_videoclips(video_clips)

    # Cargar y combinar archivos de audio
    audio = mp.CompositeAudioClip([mp.AudioFileClip(f) for f in audio_files])

    # Repetir el video de fondo para cubrir la duración del audio
    video_duration = video.duration
    audio_duration = audio.duration
    repetitions = int(audio_duration / video_duration) + 1
    video = mp.concatenate_videoclips([video] * repetitions)
    video = video.subclip(0, audio_duration)

    # Establecer el audio del video
    video = video.set_audio(audio)

    # Guardar el video resultante
    video.write_videofile(output_filename, codec='libx264', audio_codec='aac')

    # Eliminar archivos temporales de video
    for filename in video_filenames:
        os.remove(filename)

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
    script = generate_script(title)
    print('# Generar guión')
    print(script)

    # Convertir guión en audio
    audio_files = []
    for i, segment in enumerate(script.split("\n\n")):
        output_filename = f"audio_{i}.mp3"
        synthesize_speech(segment, output_filename)
        audio_files.append(output_filename)

    print('# Convertir guión en audio')
    print(output_filename)

    # Buscar video relacionado
    video_results = search_pexels_video(title)
    print('# Buscar video relacionado')
    print(video_results[0]["video_files"])

    # # Si se encuentra un video relacionado, descargarlo
    # if video_results:
    #     video_url = video_results[0]["video_files"][0]["link"]
    #     download_video(video_url, "background_video.mp4")
    # else:
    #     print("No se encontró ningún video relacionado.")
    #     return

    print('# Si se encuentra un video relacionado, descargarlo')

    background_videos_urls = []
    for video in video_results['videos']:
        video_url = video['video_files'][0]['link']
        background_videos_urls.append(video_url)
        print(video_url)


    # Crear video con el video de fondo y audio
    video_filename = "final_video.mp4"
    create_video_with_background_video(background_videos_urls, audio_files, video_filename)

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
