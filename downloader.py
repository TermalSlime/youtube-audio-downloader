import shutil
import uuid
import os
import main
from yt_dlp import YoutubeDL
from os import path

allowed_links = ["www.youtube.com", "youtu.be"]

def duration_filter(info, *, incomplete):
    duration = info.get("duration")

    if not main.config["max_duration"] == -1:
        if duration and duration > main.config["max_duration"]:
            return "video too long"

ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'match_filter': duration_filter
        }


def optimize_url(url: str):
    is_full = url.find("www.youtube.com")

    if is_full == -1:
        list_char = url.find("?list")
        if list_char == -1:
            return url
        
        not_need = url[list_char:len(url)]
        url = url.replace(not_need, "")
    else:
        list_char = url.find("&")
        if list_char == -1:
            return url
        
        not_need = url[list_char:len(url)]
        url = url.replace(not_need, "")
        
    return url
        

def download_video_via_url(url: str):

    right_link = False
    for i in allowed_links:
        if url.find(i) != -1:
            right_link = True
            break
    
    if right_link == False:
        return -2

    url = optimize_url(url)

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

        if not "requested_downloads" in info.keys():
            return -1

        file_info = {"name": info["title"],
                     "file": info["requested_downloads"][0]["filename"], 
                     "ext": info["requested_downloads"][0]["audio_ext"], 
                     "uuid": uuid.uuid4()}

        if path.exists(file_info["file"]):

            if not path.exists("temp"):
                os.mkdir("temp")

            shutil.move(file_info["file"], "temp/{}".format(file_info["file"]))
            os.renames("temp/{}".format(file_info["file"]), "temp/{}.{}".format(file_info["uuid"], file_info["ext"]))

            with open("temp/{}.txt".format(file_info["uuid"]), "w") as f:
                f.write(file_info["name"])
                f.close()
            
            return file_info["uuid"]
