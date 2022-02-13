import asyncio
import heapq
import subprocess
import logging
import os
import tempfile
import cv2

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
from .better_flv_file import BetterFLVFile

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import threading

the_dir = f"{tempfile.gettempdir()}/me"
try:
    os.mkdir(the_dir)
except FileExistsError:
    pass

async def simple_controller(reader, writer):
    ffmpeg_subprocess: subprocess.Popen = subprocess.Popen(
        [
            "stdbuf", 
            "-o0",
            "ffmpeg",
            "-f",
            "flv",
            # "-listen",
            # "1",
            "-i",
            "pipe:0", # read from stdin
            # f"rtmp://localhost:1935/{user_specific_endpoint}",  #
            "-c",
            "copy",
            "-vcodec",
            "png",
            # "-update",
            # "y",
            "-f",
            "image2",
            # "pipe:1" # send png to stdout
            f"{the_dir}/img%10d.png",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )

    # threading.Thread(target=foo).start()
    seen_nums = set()
    frames = []

    session = SessionManager(reader=reader, writer=writer)
    flv = None
    try:
        logger.debug(f"Client connected {session.peername}")

        # do handshake
        await session.handshake()

        # read chunks
        async for chunk in session.read_chunks_from_stream():
            message = chunk.as_message()
            logger.debug(f"Receiving {str(message)} {message.chunk_id}")
            if isinstance(message, NCConnect):
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
                flv = BetterFLVFile(
                    file=ffmpeg_subprocess.stdin
                )
                session.write_chunk_to_stream(StreamBegin(stream_id=1))
                session.write_chunk_to_stream(message.create_response())
                await session.drain()
                logger.debug("Response to NSPublish")
            elif isinstance(message, MetaDataMessage):
                # Write meta data to file
                flv.write(0, message.to_raw_meta(), FLVMediaType.OBJECT)
            elif isinstance(message, SetChunkSize):
                session.reader_chunk_size = message.chunk_size
            elif isinstance(message, VideoMessage):
                # Write video data to file
                flv.write(message.timestamp, message.payload, FLVMediaType.VIDEO)
                for file in sorted(os.listdir(path=the_dir)):
                    file_num = int(file[3:-4])
                    if file_num not in seen_nums:
                        file_loc = os.path.join(the_dir, file)
                        print("pushing " , file_num)
                        seen_nums.add(file_num)
                        heapq.heappush(frames, (file_num, cv2.imread(file_loc)))
                        os.unlink(file_loc)

            elif isinstance(message, AudioMessage):
                # Write data data to file
                flv.write(message.timestamp, message.payload, FLVMediaType.AUDIO)
            elif isinstance(message, NSCloseStream):
                pass
            elif isinstance(message, NSDeleteStream):
                pass
            else:
                logger.debug(f"Unknown message {str(message)}")

    except StreamClosedException as ex:
        logger.debug(f"Client {session.peername} disconnected!")
    finally:
        if flv:
            flv.close()


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
