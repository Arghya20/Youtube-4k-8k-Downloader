import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pytubefix import YouTube
import ssl, certifi, os, ffmpeg, requests
from io import BytesIO
from threading import Thread

ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Youtube 4k/8k Downloader by Arghya")
        self.root.geometry("750x550")
        
        # Theme colors
        self.bg_dark = "#1E1E1E"
        self.bg_darker = "#121212"
        self.text_color = "#FFFFFF"
        self.accent_color = "#007BFF"
        self.secondary_text = "#AAAAAA"
        self.input_bg = "#2D2D2D"
        self.button_bg = "#333333"
        
        self.root.configure(bg=self.bg_dark)

        # Main frame
        self.main_frame = tk.Frame(root, bg=self.bg_dark, padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)
        
        # URL input
        self.url_frame = tk.Frame(self.main_frame, bg=self.bg_dark)
        self.url_frame.pack(fill="x", pady=(20, 10))
        
        self.url_entry = tk.Entry(self.url_frame, font=("Arial", 11), bg=self.input_bg, 
                                 fg=self.text_color, insertbackground=self.text_color, 
                                 bd=0, highlightthickness=1, highlightbackground="#555555")
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=8)
        
        self.fetch_btn = tk.Button(self.url_frame, text="Fetch Video", font=("Arial", 11),
                                  bg=self.button_bg, fg=self.text_color, bd=0, padx=15, pady=8,
                                  activebackground="#444444", activeforeground=self.text_color,
                                  cursor="hand2", command=self.fetch_info)
        self.fetch_btn.pack(side="right", padx=(10, 0))
        
        # Info frame
        self.info_frame = tk.Frame(self.main_frame, bg=self.bg_dark)
        self.info_frame.pack(fill="x", pady=20)
        
        self.thumbnail_frame = tk.Frame(self.info_frame, bg=self.bg_darker, width=160, height=90,
                                       highlightthickness=1, highlightbackground="#555555")
        self.thumbnail_frame.pack(side="left")
        self.thumbnail_frame.pack_propagate(False)
        
        self.thumbnail_label = tk.Label(self.thumbnail_frame, bg=self.bg_darker)
        self.thumbnail_label.pack(fill="both", expand=True)
        
        self.details_frame = tk.Frame(self.info_frame, bg=self.bg_dark, padx=15)
        self.details_frame.pack(side="left", fill="both", expand=True)
        
        self.title_label = tk.Label(self.details_frame, text="",
                                   font=("Arial", 12, "bold"), fg=self.text_color,
                                   bg=self.bg_dark, anchor="w", justify="left", wraplength=400)
        self.title_label.pack(fill="x", anchor="w")
        
        self.desc_label = tk.Label(self.details_frame, text="Video Description",
                                  font=("Arial", 10), fg=self.secondary_text,
                                  bg=self.bg_dark, anchor="w", justify="left")
        self.desc_label.pack(fill="x", anchor="w", pady=(5, 0))
        
        # Quality dropdown
        self.quality_frame = tk.Frame(self.main_frame, bg=self.bg_dark)
        self.quality_frame.pack(fill="x", pady=10)
        
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('TCombobox', 
                            fieldbackground=self.input_bg,
                            background=self.input_bg,
                            foreground=self.text_color,
                            arrowcolor=self.text_color)
        
        self.res_combobox = ttk.Combobox(self.quality_frame, state="readonly", width=10, font=("Arial", 11))
        self.res_combobox.pack(anchor="center")
        
        # Download button
        self.download_btn_frame = tk.Frame(self.main_frame, bg=self.bg_dark)
        self.download_btn_frame.pack(pady=20)
        
        self.download_btn = tk.Button(self.download_btn_frame, text="Download", font=("Arial", 12),
                                     bg=self.button_bg, fg=self.text_color, 
                                     bd=1, relief="solid", width=15, height=1,
                                     activebackground="#444444", activeforeground=self.text_color,
                                     cursor="hand2", command=self.start_download)
        self.download_btn.pack()
        
        # Progress bar
        self.progress_frame = tk.Frame(self.main_frame, bg=self.bg_dark)
        self.progress_frame.pack(fill="x", pady=(10, 5))
        
        self.style.configure("Blue.Horizontal.TProgressbar", 
                           background=self.accent_color,
                           troughcolor=self.input_bg)
        
        self.progress = ttk.Progressbar(self.progress_frame, style="Blue.Horizontal.TProgressbar", 
                                      length=600, mode='determinate')
        self.progress.pack(fill="x", padx=5)
        
        self.progress_percent = tk.Label(self.main_frame, text="0%", font=("Arial", 12), 
                                       bg=self.bg_dark, fg=self.accent_color)
        self.progress_percent.pack(pady=5)
        
        self.status_label = tk.Label(self.main_frame, text="", 
                                    font=("Arial", 11), bg=self.bg_dark, fg=self.secondary_text)
        self.status_label.pack(pady=5)
        
        # Initialize
        self.yt = None
        self.filtered_streams = []
        self.video_path = ""
        self.audio_path = ""

    def fetch_info(self):
        url = self.url_entry.get().strip()
        if not url:
            return messagebox.showerror("Error", "Please enter a URL")
        
        try:
            self.progress["value"] = 0
            self.progress_percent.config(text="0%")
            self.status_label.config(text="")
            
            self.yt = YouTube(url, on_progress_callback=self.progress_hook)
            self.title_label.config(text=self.yt.title)

            response = requests.get(self.yt.thumbnail_url)
            img_data = Image.open(BytesIO(response.content)).resize((160, 90))
            thumb = ImageTk.PhotoImage(img_data)
            self.thumbnail_label.configure(image=thumb)
            self.thumbnail_label.image = thumb

            streams = self.yt.streams.filter(adaptive=True, mime_type="video/mp4").order_by("resolution").desc()
            self.filtered_streams = []
            resolutions = []
            for s in streams:
                if s.resolution and s.resolution not in resolutions:
                    resolutions.append(s.resolution)
                    self.filtered_streams.append(s)
                    
            if not resolutions:
                messagebox.showinfo("Info", "No MP4 streams found for this video")
                return
                
            self.res_combobox["values"] = resolutions
            self.res_combobox.current(0)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch video info\n{e}")

    def progress_hook(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percent = int((bytes_downloaded / total_size) * 100)
        self.progress["value"] = percent
        self.progress_percent.config(text=f"{percent}%")
        self.root.update_idletasks()

    def start_download(self):
        Thread(target=self.download).start()

    def download(self):
        try:
            self.status_label.config(text="Downloading...", fg=self.secondary_text)
            self.progress["value"] = 0
            self.progress_percent.config(text="0%")

            idx = self.res_combobox.current()
            if idx < 0 or not self.filtered_streams:
                messagebox.showerror("Error", "Please fetch video info first")
                return

            os.makedirs("videos", exist_ok=True)
            video_stream = self.filtered_streams[idx]
            self.video_path = video_stream.download(output_path="videos", filename="video_only.mp4")

            audio_stream = self.yt.streams.filter(only_audio=True).first()
            self.audio_path = audio_stream.download(output_path="videos", filename="audio_only.mp4")

            title_safe = "".join([c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in self.yt.title])
            title_safe = title_safe.replace(" ", "_")
            output_path = f"videos/{title_safe}_merged.mp4"

            (
                ffmpeg
                .output(ffmpeg.input(self.video_path), ffmpeg.input(self.audio_path),
                        output_path, vcodec='copy', acodec='aac', strict='experimental')
                .run(overwrite_output=True)
            )

            os.remove(self.video_path)
            os.remove(self.audio_path)

            self.progress["value"] = 100
            self.progress_percent.config(text="100%")
            self.status_label.config(text="Downloaded Successfully", fg=self.secondary_text)

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_label.config(text="Download Failed", fg="#FF6B6B")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()