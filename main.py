from pytubefix import YouTube
from rich import print
from tqdm import tqdm
import ssl
import certifi
import os
import ffmpeg

# Fix SSL issue
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

# Global progress bar instance
progress_bar = None

def show_progress(stream, chunk, bytes_remaining):
    global progress_bar
    if progress_bar:
        progress_bar.update(len(chunk))

# Ask user for URL
url = input("Enter the YouTube video URL: ")

try:
    yt = YouTube(url, on_progress_callback=show_progress)
    print(f"[bold cyan]Title:[/] {yt.title}")

    # Filter video-only streams
    streams = yt.streams.filter(adaptive=True, mime_type="video/mp4").order_by('resolution').desc()

    print("\nAvailable video resolutions:")
    available = []
    filtered_streams = []

    for stream in streams:
        if stream.resolution and stream.resolution not in available:
            available.append(stream.resolution)
            filtered_streams.append(stream)
            print(f"{len(filtered_streams)}. {stream.resolution}")

    choice = int(input("\nEnter the number of the quality you want: ")) - 1
    selected_stream = filtered_streams[choice]

    # Set up progress bar for video
    filesize = selected_stream.filesize or selected_stream.filesize_approx
    progress_bar = tqdm(total=filesize, unit='B', unit_scale=True, desc='Downloading Video')
    video_path = selected_stream.download(filename="video_only.mp4")
    progress_bar.close()

    print(f"[green]Downloaded video stream: {selected_stream.resolution}[/green]")

    # Download audio with progress
    audio_stream = yt.streams.filter(only_audio=True).first()
    filesize = audio_stream.filesize or audio_stream.filesize_approx
    progress_bar = tqdm(total=filesize, unit='B', unit_scale=True, desc='Downloading Audio')
    audio_path = audio_stream.download(filename="audio_only.mp4")
    progress_bar.close()

    print("[green]Downloaded audio stream[/green]")

    # Merge video + audio using ffmpeg
    output_file = f"{yt.title.replace(' ', '_')}_merged.mp4"
    video_input = ffmpeg.input(video_path)
    audio_input = ffmpeg.input(audio_path)

    (
        ffmpeg
        .output(video_input, audio_input, output_file, vcodec='copy', acodec='aac', strict='experimental')
        .run(overwrite_output=True)
    )

    print(f"[bold green]Final video saved as: {output_file}[/bold green]")

    # Clean up temp files
    os.remove(video_path)
    os.remove(audio_path)

except Exception as e:
    print(f"[red]Error:[/] {e}")