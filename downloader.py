import yt_dlp
import time
import os
import json

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.client import OAuth2Credentials

FOLDER_ID = os.environ["DRIVE_FOLDER_ID"]

with open("token.json") as f:
    token_data = json.load(f)

credentials = OAuth2Credentials(
    access_token=token_data["token"],
    client_id=token_data["client_id"],
    client_secret=token_data["client_secret"],
    refresh_token=token_data["refresh_token"],
    token_expiry=None,
    token_uri=token_data["token_uri"],
    user_agent=None
)

gauth = GoogleAuth()
gauth.credentials = credentials

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

        video = None

        for file in os.listdir("."):
            if file.startswith("video"):
                video = file

        if video is None:
            raise Exception("video not found")

        gfile = drive.CreateFile({
            "title": video,
            "parents": [{"id": FOLDER_ID}]
        })

        gfile.SetContentFile(video)
        gfile.Upload()

        os.remove(video)

        completed.append(url)

    except Exception:
        failed.append(url)

    time.sleep(5)

with open("completed.txt","a") as f:
    for link in completed:
        f.write(link + "\n")

with open("failed.txt","a") as f:
    for link in failed:
        f.write(link + "\n")
