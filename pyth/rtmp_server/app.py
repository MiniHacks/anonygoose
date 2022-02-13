import threading
from fastapi import FastAPI
from pydantic import BaseModel
import subprocess

app = FastAPI()


@app.get("/")
async def test():
    return "hi!"


class CreateStreamReqBody(BaseModel):
    yt_rtmp_uri: str


class CreateStreamResponse(BaseModel):
    stream_url: str


@app.post("/create_stream")
def create_stream(body: CreateStreamReqBody):
    user_specific_endpoint = "live/app"
    user_facing_url = f"rtmp://anony.news/{user_specific_endpoint}"

    secret_internal_rtmp_port = 1234
    internal_rtmp_url = (
        f"rtmp://localhost:{secret_internal_rtmp_port}/{user_specific_endpoint}"
    )

    params = [
        "ffmpeg",
        "-f",
        "flv",
        "-listen",
        "1",
        "-i",
        f"rtmp://localhost:1935/{user_specific_endpoint}",  #
        "-c",
        "copy",
        "-vcodec",
        "png",
        "-update",
        "y",
        "-f",
        "image2",
        "pipe:1",
    ]

    ffmpeg_subprocess = subprocess.Popen(params, stdout=subprocess.PIPE)

    def on_subprocess_end():
        ffmpeg_subprocess.wait()

    def convert_faces():
        import cv2
        import numpy as np
        while True:
            img = cv2.imdecode(np.frombuffer(ffmpeg_subprocess.stdout.read(), dtype=np.uint8), cv2.IMREAD_COLOR)
            cv2.imshow("a", img)
            cv2.waitKey(delay=34)

    threading.Thread(target=convert_faces).start()
    threading.Thread(target=on_subprocess_end).start()

    return user_facing_url
