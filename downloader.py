import yt_dlp
import time
import os
import json

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.client import OAuth2Credentials

# Drive folder id from github secret
FOLDER_ID = os.environ["DRIVE_FOLDER_ID"]

# load oauth token json
with open("token.json") as f:
    token_data = json.load(f)

credentials = OAuth2Credentials(
    access_token=token_data["access_token"],
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

# read pending links
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

        for f in os.listdir("."):
            if f.startswith("video"):
                video = f

        if video is None:
            raise Exception("video not found")

        file = drive.CreateFile({
            "title": video,
            "parents": [{"id": FOLDER_ID}]
        })

        file.SetContentFile(video)
        file.Upload()

        os.remove(video)

        completed.append(url)

    except Exception as e:
        failed.append(url)

    time.sleep(5)

# write completed
with open("completed.txt","a") as f:
    for url in completed:
        f.write(url + "\n")

# write failed
with open("failed.txt","a") as f:
    for url in failed:
        f.write(url + "\n")
