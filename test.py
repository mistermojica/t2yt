import requests
from moviepy.editor import VideoFileClip

def download_video(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def process_video(local_filename):
    try:
        clip = VideoFileClip(local_filename).subclip(0, 10)  # Ejemplo de subclip de 0 a 10 segundos
        clip.preview()
    except Exception as e:
        print(f"Error processing video: {e}")

def main():
    video_url = "https://dm0qx8t0i9gc9.cloudfront.net/watermarks/video/BPDPkANXukm1vn7si/videoblocks-aerial-shot-of-autonomous-autopilot-cars-driving-on-junction-driveway-spbd-artificial-intelligence-scans-detect-vehicles-avoids-traffic-jams-self-driving-concept-safety-control_rw8b2cko___468c0f501559f9b5e849921093c33191__P720.mp4?type=preview&origin=VIDEOBLOCKS&timestamp_ms=1718219589579&publicKey=test_87e1cbe4f99b14c4a12e37392fa02353fbb01a90b3e8eff743113a917d1&apiVersion=2.0&stockItemId=11101601&resolution=720p&endUserId=3afe0cf541eaac2044500f6fc23e8bc27daab775&projectId=bibl-ia-tv-p&searchId=868289f1-d2a8-43bf-8340-aff621165347&searchPageId=b76be171-44c2-49a2-9fec-f9f1c7dd7566"
    local_filename = "video.mp4"
    download_video(video_url, local_filename)
    process_video(local_filename)

if __name__ == "__main__":
    main()
