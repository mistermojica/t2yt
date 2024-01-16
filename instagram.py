import os
import instaloader
from moviepy.editor import VideoFileClip
from openai import OpenAI

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
client.api_key = OPENAI_API_KEY


def descargar_video_instagram(id):
    # L = instaloader.Instaloader()

    # P = instaloader.Post(L.context, {}, None)
    # post = P.from_shortcode(L.context, url)
    # L.download_post(post, './video_instagram.mp4')
    L = instaloader.Instaloader()
    post = instaloader.Post.from_shortcode(L.context, id)
    video_url = post.video_url
    filename = L.format_filename(post, target=post.owner_username)
    L.download_pic(filename=filename, url=video_url, mtime=post.date_utc)

id = "C142f0ou8M2"
print("Descargando video:", id)
descargar_video_instagram(id)
print("Video descargado:", id)

def extraer_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

video_path = './video_instagram.mp4'
audio_path = './audio_instagram.mp3'
print("Extrayendo MP3:", audio_path, video_path)
extraer_audio(video_path, audio_path)
print("MP3 Extraido:", audio_path, video_path)


def transcribir_audio_whisper(audio_path):
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_path,
        response_format="text"
    )

    return 

print("Transcribiendo MP3:", audio_path)
transcripcion = transcribir_audio_whisper(audio_path)
print(transcripcion)