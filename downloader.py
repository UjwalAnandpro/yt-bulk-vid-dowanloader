import yt_dlp
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

if len(links) == 0:
    print("no links")
    exit()

url = links[0]

try:

    ydl_opts = {
        "format": "bestvideo[height<=360]+bestaudio/best[height<=360]",
        "outtmpl": "video.%(ext)s",
        "extractor_args": {"youtube": {"player_client": ["android"]}},
        "js_runtimes": ["node"]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    video = None

    for f in os.listdir("."):
        if f.startswith("video"):
            video = f

    file = drive.CreateFile({
        "title": video,
        "parents": [{"id": FOLDER_ID}]
    })

    file.SetContentFile(video)
    file.Upload()

    os.remove(video)

    with open("completed.txt","a") as f:
        f.write(url+"\n")

except:

    with open("failed.txt","a") as f:
        f.write(url+"\n")

links.pop(0)

with open("pending.txt","w") as f:
    for link in links:
        f.write(link+"\n")
