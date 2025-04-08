
# Youtube 4k/8k Downloader by Arghya

A clean and minimal YouTube 4K/8K video downloader built with Python and Tkinter.


## Features

✅ Download videos in 4K and 8K (when available)

✅ Real-time download progress

✅ Saves videos in a videos/ folder


## 🖥️ Requirements
	•	Python 3.8 or above
	•	pytube library
	•	tkinter (pre-installed with Python on most systems)

## Installation

  #### 1. Clone the repository

```bash
  git clone https://github.com/Arghya20/Youtube-4k-8k-Downloader.git
  cd Youtube-4k-8k-Downloader
```

#### 	2.	Install dependencies

```bash
  pip install pytube
```

#### 	3.	(Optional) Create a virtual environment
```bash
  python -m venv venv
  source venv/bin/activate  # Mac/Linux
  .\venv\Scripts\activate    # Windows
  pip install pytube
```

### 🚀 How to Use
#### 1.  Run the app:

```bash
  python3 youtube_gui.py
```

### 	2.	Paste your YouTube video link in the input field.
### 	3.	Click Download and the app will fetch the highest resolution (up to 8K).
### 	4.	The video will be saved in the videos/ folder created in the current directory.



## 📁 Folder Structure

```bash
youtube-downloader-gui/
├── youtube_gui.py
├── videos/           ← downloaded videos will be saved here
├── requirements.txt  ← optional
└── README.md
```
    