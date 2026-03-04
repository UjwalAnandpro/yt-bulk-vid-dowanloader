import yt_dlp
import time
import os

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

FOLDER_ID = os.environ["DRIVE_FOLDER_ID"]

scope = ["https://www.googleapis.com/auth/drive"]

gauth = GoogleAuth()
gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
    "token.json", scope
)

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

        video = [f for f in os.listdir(".") if f.startswith("video")][0]

        file = drive.CreateFile({
            "title": video,
            "parents": [{"id": FOLDER_ID}]
        })

        file.SetContentFile(video)
        file.Upload()

        os.remove(video)

        completed.append(url)

    except:
        failed.append(url)

    time.sleep(5)

with open("completed.txt","a") as f:
    f.write("\n".join(completed) + "\n")

with open("failed.txt","a") as f:
    f.write("\n".join(failed) + "\n")
