import asyncio
import heapq
import queue
import subprocess
import logging
import os
import tempfile
import threading
import cv2

import image_processing.blur as blur

from pyrtmp import StreamClosedException, RTMPProtocol
from pyrtmp.messages import SessionManager
from pyrtmp.messages.audio import AudioMessage
from pyrtmp.messages.command import (
    NCConnect,
    NCCreateStream,
    NSPublish,
    NSCloseStream,
    NSDeleteStream,
)
from pyrtmp.messages.data import MetaDataMessage
from pyrtmp.messages.protocolcontrol import (
    WindowAcknowledgementSize,
    SetChunkSize,
    SetPeerBandwidth,
)
from pyrtmp.messages.usercontrol import StreamBegin
from pyrtmp.messages.video import VideoMessage
from pyrtmp.misc.flvdump import FLVFile, FLVMediaType
import tempfile

from . import stream_forwarder
from .better_flv_file import BetterFLVFile
from .conf import the_dir

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import multiprocessing



async def simple_controller(reader, writer):
    ffmpeg_frame_conversion_subprocess: subprocess.Popen = subprocess.Popen(
        [
            "stdbuf",
            "-o0",
            "ffmpeg",
            "-f",
            "flv",
            # "-listen",
            # "1",
            "-i",
            "pipe:0",  # read from stdin
            # f"rtmp://localhost:1935/{user_specific_endpoint}",  #
            "-c",
            "copy",
            "-vcodec",
            "png",
            "-f",
            "image2",
            f"{the_dir}/img%10d.png",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    # ffmpeg_audio_conversion_subprocess: subprocess.Popen = subprocess.Popen(
    #     [
    #         "ffmpeg",
    #         "-f",
    #         "flv", 
    #         "-i",
    #         "pipe:0",
    #         "-f",
    #         "segment",
    #         "-segment_time",
    #         "0.0033",
    #         f"{the_dir}/audio/test_%d.mp3",
    #     ],
    #     stdin=subprocess.PIPE,
    # )

    # threading.Thread(target=foo).start()
    seen_nums = set()
    frames = queue.PriorityQueue()
    taskie = threading.Thread(target=stream_forwarder.stream_blurred_frames, args=(frames, "rtmp://localhost:1233/"))
    taskie.start()

    session = SessionManager(reader=reader, writer=writer)
    video_flv = None
    audio_flv = None
    user_id, user_secret = None
    try:
        logger.debug(f"Client connected {session.peername}")

        # do handshake
        await session.handshake()

        # read chunks
        async for chunk in session.read_chunks_from_stream():
            message = chunk.as_message()
            logger.debug(f"Receiving {str(message)} {message.chunk_id}")
            if isinstance(message, NCConnect):
                user_id, user_secret, *rest = message.command_object['app'].split('/')
                if len(rest) > 0:
                    # screw these guys
                    return
                
                session.write_chunk_to_stream(
                    WindowAcknowledgementSize(ack_window_size=5000000)
                )
                session.write_chunk_to_stream(
                    SetPeerBandwidth(ack_window_size=5000000, limit_type=2)
                )
                session.write_chunk_to_stream(StreamBegin(stream_id=0))
                session.write_chunk_to_stream(SetChunkSize(chunk_size=8192))
                session.writer_chunk_size = 8192
                session.write_chunk_to_stream(message.create_response())
                await session.drain()
                logger.debug("Response to NCConnect")
            elif isinstance(message, WindowAcknowledgementSize):
                pass
            elif isinstance(message, NCCreateStream):
                session.write_chunk_to_stream(message.create_response())
                await session.drain()
                logger.debug("Response to NCCreateStream")
            elif isinstance(message, NSPublish):
                # create flv file at temp
                video_flv = BetterFLVFile(file=ffmpeg_frame_conversion_subprocess.stdin)
                # audio_flv = BetterFLVFile(file=ffmpeg_audio_conversion_subprocess.stdin)
                session.write_chunk_to_stream(StreamBegin(stream_id=1))
                session.write_chunk_to_stream(message.create_response())
                await session.drain()
                logger.debug("Response to NSPublish")
            elif isinstance(message, MetaDataMessage):
                # Write meta data to file
                video_flv.write(0, message.to_raw_meta(), FLVMediaType.OBJECT)
                # audio_flv.write(0, message.to_raw_meta(), FLVMediaType.OBJECT)
            elif isinstance(message, SetChunkSize):
                session.reader_chunk_size = message.chunk_size
            elif isinstance(message, VideoMessage):
                # Write video data to file
                video_flv.write(message.timestamp, message.payload, FLVMediaType.VIDEO)
                print(message.timestamp)
                for file in sorted(os.listdir(path=the_dir)):
                    if file == 'audio':
                        continue
                    file_num = int(file[3:][:10])
                    if file_num not in seen_nums:
                        file_loc = os.path.join(the_dir, file)
                        print("pushing ", file_num)
                        seen_nums.add(file_num)
                        # Assume 30 frames per second (wrong)
                        ms_offset = file_num / 30
                        frames.put((file_num, ms_offset, cv2.imread(file_loc)))
                        os.unlink(file_loc)

            elif isinstance(message, AudioMessage):
                pass
                # Write data data to file
                # audio_flv.write(message.timestamp, message.payload, FLVMediaType.AUDIO)
            elif isinstance(message, NSCloseStream):
                pass
            elif isinstance(message, NSDeleteStream):
                pass
            else:
                logger.debug(f"Unknown message {str(message)}")

    except StreamClosedException as ex:
        logger.debug(f"Client {session.peername} disconnected!")
    finally:
        if video_flv:
            video_flv.close()
        if audio_flv:
            audio_flv.close()


async def serve_rtmp(use_protocol=True, port=1935):
    loop = asyncio.get_running_loop()
    if use_protocol is True:
        server = await loop.create_server(
            lambda: RTMPProtocol(controller=simple_controller, loop=loop),
            "0.0.0.0",
            port,
        )
    else:
        server = await asyncio.start_server(simple_controller, "0.0.0.0", port)
    addr = server.sockets[0].getsockname()
    logger.info(f"Serving on {addr}")
    async with server:
        await server.serve_forever()


def wrapper(port: int):
    asyncio.run(serve_rtmp(port=port))


IS_DEBUG = True
NUM_PROCESS = 2

if __name__ == "__main__":
    if IS_DEBUG is True:
        wrapper(1935)
    else:
        from multiprocessing import Process
        import uvloop

        uvloop.install()
        process = []
        for i in range(NUM_PROCESS):
            p = Process(target=wrapper, args=(1935 + i + 1,))
            p.start()
            process.append(p)
        for p in process:
            p.join()
