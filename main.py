import json
import os
import subprocess
import time
import urllib.request


class run_shell:
    """
    run(cmd_in: str) -> object   subprocessのrunと一緒

    Popen(cmd_in: str) -> object subprocessのPopenと一緒
    """

    def run(cmd_in: str) -> object:
        if os.name == "nt":
            out_out = subprocess.run(
                cmd_in, shell=True, encoding="utf-8", errors="ignore", stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
        else:
            out_out = subprocess.run(
                "exec " + cmd_in,
                shell=True,
                encoding="utf-8",
                errors="ignore",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        return out_out

    def Popen(cmd_in: str) -> object:
        if os.name == "nt":
            out_out = subprocess.Popen(
                cmd_in, shell=True, encoding="utf-8", errors="ignore", stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
        else:
            out_out = subprocess.Popen(
                "exec " + cmd_in,
                shell=True,
                encoding="utf-8",
                errors="ignore",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        return out_out


class Mycounter:
    def __init__(self) -> None:
        self.co = 1

    def add(self):
        self.co = self.co + 1


def get_dict(urls, qe):
    """
    apiから静的解析
    """

    qe = Mycounter()
    if "program" in urls:
        playlist = []
        while True:
            url = urls.replace(r"program", r"api/programs") + r"/talks" + f"?_p={qe.co}"
            print(qe.co, url)
            a = urllib.request.Request(url)
            with urllib.request.urlopen(a) as res:
                a = res.read()

            minilist = json.loads(a)
            if len(minilist) == 0:
                break
            playlist.extend(minilist)
            time.sleep(3)
            qe.add()
        return playlist
    else:
        url = urls.replace(r"talk/", r"api/talks/")
        a = urllib.request.Request(url)
        with urllib.request.urlopen(a) as res:
            a = res.read()
        return [json.loads(a)]


def make_audiodata(metadata):
    audioFileUrl = metadata["audioFileUrl"]
    imageUrl = metadata["imageUrl"]

    title = metadata["title"]
    createdAt = metadata["createdAt"]
    programTitle = metadata["programTitle"]
    description = metadata["description"].replace("\n", "")
    radioid = metadata["id"]
    tem = createdAt.split(" ")[0]
    nen = tem.split("-")[0]
    run_shell.run(f"curl.exe -o post_audio.m4a {audioFileUrl}")
    run_shell.run("ffmpeg\\ffmpeg.exe -i  post_audio.m4a temp.mp3")
    run_shell.run(f"curl.exe -o cover.jpg {imageUrl}")
    run_shell.run(
        "ffmpeg\\ffmpeg.exe -i temp.mp3 -i cover.jpg -map 0:a -map 1:v -c copy -disposition:1 attached_pic -id3v2_version 3 "
        f'-metadata album="{programTitle}" -metadata date={nen} -metadata title="{title}" -metadata comment="{description}" -metadata genre="Radio" -metadata publisher="Radiotalk" [{programTitle}][{tem}]{title}_{radioid}.mp3'
    )
    os.remove("post_audio.m4a")
    os.remove("temp.mp3")
    os.remove("cover.jpg")


url = input("番組URL or ラジオURL>>")
# url = r"https://radiotalk.jp/program/32332"

metadata = get_dict(url, Mycounter)
print(len(metadata), metadata)
for i in metadata:
    make_audiodata(i)
    time.sleep(1)
