from pytube import YouTube, Search
import os
import json

# Función para descargar los videos
def download_video(video_url, output_path):
    yt = YouTube(video_url)
    ys = yt.streams.get_highest_resolution()
    ys.download(output_path)
    video_info = {
        'title': yt.title,
        'description': yt.description,
        'views': yt.views,
        'rating': yt.rating,
        'length': yt.length,
        'author': yt.author,
        'publish_date': yt.publish_date.isoformat() if yt.publish_date else None,
        'keywords': yt.keywords,
        'video_url': video_url,
        'thumbnail_url': yt.thumbnail_url,
        'channel_url': yt.channel_url,
        'channel_id': yt.channel_id,
        'watch_url': yt.watch_url,
        'embed_url': yt.embed_url,
        'video_id': yt.video_id,
        # 'streams': [str(stream) for stream in yt.streams],  # Lista de streams disponibles
        # 'caption_tracks': [caption.__dict__ for caption in yt.caption_tracks],  # Lista de captions
        # 'captions': yt.captions.__dict__,  # Captions query
        # 'metadata': yt.metadata.__dict__,  # Metadata del video
        # 'streaming_data': yt.vid_info.get('streamingData', {}),
        # 'vid_info': yt.vid_info  # Información del video
    }
    print(f'Descargado: ', json.dumps(video_info, indent=4))

# Término de búsqueda y carpeta de descargas
search_query = 'MrBeast'
output_path = './downloads'  # Carpeta donde se guardarán los videos

# Crear la carpeta de descargas si no existe
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Realizar la búsqueda de videos
search = Search(search_query)

# Descargar cada short
for result in search.results:
    print(result)
    video_id = result.video_id
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    download_video(video_url, output_path)
