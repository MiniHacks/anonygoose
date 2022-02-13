from bitstring import BitStream, BitArray
from pyrtmp.misc.flvdump import FLVFile, FLVMediaType


class BetterFLVFile(FLVFile):

    def __init__(self, file) -> None:
        self.file = file
        self.prev_tag_size = 0
        # write header
        stream = BitStream()
        stream.append(b'FLV')
        stream.append(BitStream(uint=1, length=8))
        stream.append(BitStream(uint=5, length=8))
        stream.append(BitStream(uint=9, length=32))
        stream.append(BitStream(uint=self.prev_tag_size, length=32))
        self.file.write(stream.bytes)

