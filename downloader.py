import yt_dlp
import time
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LoadServiceConfigFile("token.json")
drive = GoogleDrive(gauth)

with open("pending.txt") as f:
    links = f.read().splitlines()

completed = []
failed = []

for url in links:

    try:
        ydl_opts = {
            "format": "bestvideo[height<=360]+bestaudio/best[height<=360]",
            "outtmpl": "video.%(ext)s"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file = drive.CreateFile({'title': 'video.mp4'})
        file.SetContentFile("video.mp4")
        file.Upload()

        os.remove("video.mp4")

        completed.append(url)

    except:
        failed.append(url)

    time.sleep(5)

open("completed.txt","a").write("\n".join(completed))
open("failed.txt","a").write("\n".join(failed))
