import asyncio
import os
import queue
from typing import Tuple, List
import aiofiles
import numpy as np
from pyrtmp.messages.audio import AudioMessage
import subprocess

from .conf import the_dir
from image_processing import blur

def stream_blurred_frames(
    frames_to_blur_queue: "queue.PriorityQueue[Tuple[int, int, np.ndarray]]",
    rtmp_address: str,
    user_id_holder: List[str]
):
    print("###########################3333 hi")
    ffmpeg_streaming_process = None

    print("################################3 process started")
    while True:
        print("got img")
        filenum, ms_offset, image = frames_to_blur_queue.get()
        if image is None:
            ffmpeg_streaming_process.stdin.close()
            ffmpeg_streaming_process.wait()
            return

        img_height, img_width, img_channels = image.shape

        if ffmpeg_streaming_process is None:
            ffmpeg_streaming_process = subprocess.Popen(
            [
                "ffmpeg",
                # *audio_instr,
                "-f",
                "rawvideo",
                "-vcodec",
                "rawvideo",
                "-pix_fmt",
                "bgr24",
                "-s",
                f"{img_width}x{img_height}",
                "-r",
                "30",
                "-i",
                "pipe:0",
                # "-c",
                # "copy",
                "-f",
                "flv",
                rtmp_address
                # "rtmp://localhost:1935/live/app",
            ],
            stdin=subprocess.PIPE
        )
    
        image = blur.blur(image, user_id_holder[0])

        # if os.path.exists(audio_filename := f"{the_dir}/audio/test_{filenum}.mp3"):
        #     audio_instr = ["-i", audio_filename]
        # else:
        #     audio_instr = []

        ffmpeg_streaming_process.stdin.write(image.tobytes())